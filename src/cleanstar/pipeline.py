"""Coordinate CleanStar pipeline operations."""

import csv
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cleanstar.data_config import RAW_LOADS
from cleanstar.audit import run_raw_audit, format_audit_report
from cleanstar.validate_setup import validate_setup
from cleanstar.transform import (transform_claims, transform_encounter,
                                 transform_patient, transform_provider)


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"


def count_csv_rows(file_path):
    """Count CSV records, excluding the header."""
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)
        return sum(1 for _ in reader)


def get_source_row_counts(data_dir=DATA_DIR):
    """Count configured CSV records, excluding headers."""
    return {
        table.rsplit(".", 1)[-1]: count_csv_rows(Path(data_dir) / filename.removesuffix(".gz"))
        for filename, table, _ in RAW_LOADS
    }


def get_load_row_counts(cursor, load_run_id):
    """Count only raw rows belonging to this run."""
    sql = (PROJECT_DIR / "sql/validation/count_load_rows.sql").read_text(encoding="utf-8-sig")
    results = {}
    for _, table, _ in RAW_LOADS:
        cursor.execute(sql, (table, load_run_id))
        results[table.rsplit(".", 1)[-1]] = cursor.fetchone()[0]
    return results


def reconcile_load_counts(source_counts, loaded_counts):
    """Report matching or skipped loads; stop on partial count mismatches."""
    results = {}
    for table, source in source_counts.items():
        loaded = loaded_counts[table]
        status = "MATCH" if loaded == source else "NO_NEW_ROWS" if loaded == 0 else "MISMATCH"
        results[table] = {"source_rows": source, "loaded_rows": loaded, "status": status}
    mismatches = [table for table, counts in results.items() if counts["status"] == "MISMATCH"]
    if mismatches:
        raise RuntimeError("Source/load row count mismatch: " + ", ".join(mismatches))
    return results


def create_load_context():
    """Create one run ID and UTC timestamp to share across a pipeline run."""
    load_run_id = uuid4().hex
    ingested_at = datetime.now(timezone.utc)

    return load_run_id, ingested_at


def upload_files(cursor, data_dir=DATA_DIR):
    """Upload configured CSVs and return each filename with its PUT results.

    Uses an existing cursor; the caller owns the connection. This uploads files
    only, without loading table rows or changing the local source files.
    """
    sql = (PROJECT_DIR / "sql" / "ingestion" / "upload_files.sql").read_text(
        encoding="utf-8-sig"
    )
    files = [Path(data_dir) / filename.removesuffix(".gz") for filename, _, _ in RAW_LOADS]

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


def get_snowflake_connection():
    """Import the connector only when starting a live run."""
    from cleanstar.connection import get_snowflake_connection as connect
    return connect()


def format_run_report(result):
    lines = ["CLEANSTAR RUN SUMMARY", "=" * 60,
             f"Load Run ID: {result['load_run_id']}",
             f"Started: {result['ingested_at']}", "", "INGESTION"]
    for table, counts in result["reconciliation"].items():
        lines.append(f"{table}: source={counts['source_rows']:,}, "
                     f"loaded={counts['loaded_rows']:,} ({counts['status']})")
    lines += ["", "NO_NEW_ROWS means nothing was loaded for this run; "
              "Snowflake may have skipped an already-loaded file.", "",
              format_audit_report(result["audit"], result["load_run_id"]),
              "", "TRANSFORMATION"]
    for dataset, counts in result["transformations"].items():
        lines.append(f"{dataset}: clean={counts['clean_rows']:,}, "
                     f"quarantine={counts['quarantine_rows']:,}")
    lines.append("Clean includes warnings; quarantine includes duplicates.")
    return "\n".join(lines)


def main(data_dir=DATA_DIR):
    """Run each pipeline step in order using one Snowflake session.

    Setup runs separately. Raw ingestion and each dataset commit independently;
    inspect a failed run before retrying because earlier data may remain.
    """
    source_counts = get_source_row_counts(data_dir)
    load_run_id, ingested_at = create_load_context()
    print(f"Load Run ID: {load_run_id}")

    with get_snowflake_connection() as connection:
        with connection.cursor() as cursor:
            validate_setup(cursor)
            upload_results = upload_files(cursor, data_dir)
            validate_staged_files(cursor)

            copy_results = load_raw_tables(cursor, load_run_id, ingested_at)
            connection.commit()
            loaded_counts = get_load_row_counts(cursor, load_run_id)
            reconciliation = reconcile_load_counts(source_counts, loaded_counts)

            audit = run_raw_audit(cursor, load_run_id)
            connection.commit()  # Finish reads before creating temporary tables.
            transformations = {
                "claims": transform_claims(cursor, load_run_id),
                "encounters": transform_encounter(cursor, load_run_id),
                "patients": transform_patient(cursor, load_run_id),
                "providers": transform_provider(cursor, load_run_id),
            }

    return {
        "load_run_id": load_run_id,
        "ingested_at": ingested_at.isoformat(),
        "uploads": upload_results,
        "copy_results": copy_results,
        "reconciliation": reconciliation,
        "audit": audit,
        "transformations": transformations,
    }
