"""Coordinate CleanStar pipeline operations."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cleanstar.data_config import RAW_LOADS


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"


def create_load_context():
    """Create one run ID and UTC timestamp to share across a pipeline run."""
    load_run_id = uuid4().hex
    ingested_at = datetime.now(timezone.utc)

    return load_run_id, ingested_at


def upload_files(cursor):
    """Upload configured CSVs and return each filename with its PUT results.

    Uses an existing cursor; the caller owns the connection. This uploads files
    only, without loading table rows or changing the local source files.
    """
    sql = (PROJECT_DIR / "sql" / "ingestion" / "upload_files.sql").read_text(
        encoding="utf-8-sig"
    )
    files = [DATA_DIR / filename.removesuffix(".gz") for filename, _, _ in RAW_LOADS]

    # Check all inputs before starting uploads to avoid a partial run for missing files.
    missing_files = [str(file) for file in files if not file.is_file()]
    if missing_files:
        raise FileNotFoundError("Missing source files:\n" + "\n".join(missing_files))

    results = []
    for file in files:
        file_uri = f"file://{file.resolve().as_posix()}"
        cursor.execute(sql, (file_uri,))
        rows = cursor.fetchall()

        # PUT returns transfer status in its seventh result column.
        # SKIPPED can mean the same file is already present on the stage.
        if not rows or any(row[6] not in ("UPLOADED", "SKIPPED") for row in rows):
            raise RuntimeError(f"Upload failed for {file.name}: {rows}")

        results.append((file.name, rows))

    return results


def validate_staged_files(cursor):
    """Check staged CSV structure as text; raise if files are missing or invalid.

    Temporary tables contain only source columns, so ingestion metadata does not
    cause false column-count errors. No rows are loaded or transformed.
    """
    sql_dir = PROJECT_DIR / "sql" / "validation"
    list_sql = (sql_dir / "list_staged_files.sql").read_text(encoding="utf-8-sig")
    create_sql = (sql_dir / "create_validation_table.sql").read_text(encoding="utf-8-sig")
    validate_sql = (sql_dir / "validate_staged_file.sql").read_text(encoding="utf-8-sig")
    drop_sql = (sql_dir / "drop_validation_table.sql").read_text(encoding="utf-8-sig")

    cursor.execute(list_sql)
    # LIST names include the stage name followed by the file's relative path.
    staged_files = {row[0].split("/", 1)[-1] for row in cursor.fetchall()}
    missing_files = [name for name, _, _ in RAW_LOADS if name not in staged_files]
    if missing_files:
        raise FileNotFoundError("Missing staged files:\n" + "\n".join(missing_files))

    results = []
    failures = []
    for filename, _, source_columns in RAW_LOADS:
        temporary_table = f"CLEANSTAR.RAW.VALIDATION_TEMP_{uuid4().hex.upper()}"
        column_definitions = ",\n    ".join(
            '"' + name.replace('"', '""') + '" VARCHAR'
            for name in source_columns
        )
        cursor.execute(
            create_sql.replace("{column_definitions}", column_definitions),
            (temporary_table,),
        )
        try:
            cursor.execute(validate_sql, (temporary_table, filename))
            errors = cursor.fetchall()
        finally:
            cursor.execute(drop_sql, (temporary_table,))

        results.append((filename, errors))
        if errors:
            # Snowflake's validation output puts the error description first.
            failures.extend(f"{filename}: {row[0]}" for row in errors)

    if failures:
        raise RuntimeError("Staged CSV validation failed:\n" + "\n".join(failures))

    return results


def load_raw_tables(cursor, load_run_id, ingested_at):
    """Load validated staged CSVs with shared run metadata and return COPY results.

    Call only after validate_staged_files() succeeds. Source fields are passed
    through unchanged into VARCHAR columns. Already-loaded files may be skipped
    by Snowflake; results are returned for reporting and later reconciliation.
    A failed statement stops this function but does not undo earlier statements.
    The caller owns the connection and any transaction boundaries.
    """
    sql_template = (PROJECT_DIR / "sql" / "ingestion" / "load_raw.sql").read_text(encoding="utf-8-sig")
    results = []

    for filename, table_name, source_columns in RAW_LOADS:
        target_columns = ", ".join('"' + name.replace('"', '""') + '"' for name in source_columns)
        staged_columns = ", ".join(f"staged_file.${index}" for index in range(1, len(source_columns) + 1))
        sql = sql_template.replace("{target_columns}", target_columns).replace("{staged_columns}", staged_columns)
        source_file = filename.removesuffix(".gz")
        cursor.execute(sql, (table_name, load_run_id, source_file, ingested_at.isoformat(), filename), )
        results.append((table_name, cursor.fetchall()))

    return results
