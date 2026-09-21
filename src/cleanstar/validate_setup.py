"""Check required pipeline objects using an existing Snowflake cursor.

This checks table access and required column names, not column types or data.
"""

from pathlib import Path

from cleanstar.data_config import (CURATED_TABLES, QUALITY_METADATA_COLUMNS, RAW_LOADS, RAW_METADATA_COLUMNS, )

VALIDATION_SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "validation"


def read_validation_sql(filename):
    return (VALIDATION_SQL_DIR / filename).read_text(encoding="utf-8-sig")


def check_table_columns(cursor, sql, table_name, expected_columns):
    """Return missing column names; Snowflake errors propagate to the caller."""
    cursor.execute(sql, (table_name,))
    actual_columns = {row[0] for row in cursor.fetchall()}
    return [
        f"{table_name}.{column_name}"
        for column_name in expected_columns
        if column_name not in actual_columns
    ]


def validate_setup(cursor):
    """Raise an error if required objects are inaccessible or columns are missing.

    The pipeline should call this before ingestion and stop if it raises.
    The caller retains responsibility for closing the cursor and connection.
    """
    table_sql = read_validation_sql("describe_table.sql")
    file_format_sql = read_validation_sql("describe_file_format.sql")
    stage_sql = read_validation_sql("describe_stage.sql")
    raw_metadata = tuple(name for name, _ in RAW_METADATA_COLUMNS)
    quality_metadata = tuple(name for name, _ in QUALITY_METADATA_COLUMNS)
    missing_columns = []

    for _, raw_table, source_columns in RAW_LOADS:
        raw_columns = source_columns + raw_metadata
        missing_columns.extend(
            check_table_columns(cursor, table_sql, raw_table, raw_columns)
        )

        processed_columns = raw_columns + quality_metadata
        for table_name in CURATED_TABLES[raw_table].values():
            missing_columns.extend(
                check_table_columns(cursor, table_sql, table_name, processed_columns)
            )

    if missing_columns:
        details = "\n".join(f"- {column}" for column in missing_columns)
        raise RuntimeError(f"CleanStar setup has missing columns:\n{details}")

    # These names match the objects defined in sql/setup.
    cursor.execute(file_format_sql, ("CLEANSTAR.RAW.CSV_FORMAT",))
    cursor.fetchall()
    cursor.execute(stage_sql, ("CLEANSTAR.RAW.RAW_STAGE",))
    cursor.fetchall()
