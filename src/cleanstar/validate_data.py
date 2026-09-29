"""Run business-rule SQL and collect categorized records for one load.

SQL files contain all business-rule logic. These functions do not modify tables
or open connections; the caller supplies and retains ownership of the cursor.
"""

from pathlib import Path


VALIDATION_SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "validation"

DATASET_VALIDATIONS = (
    ("claims", "validate_claims.sql"),
    ("encounters", "validate_encounters.sql"),
    ("patients", "validate_patients.sql"),
    ("providers", "validate_providers.sql"),
)


def run_validation_query(cursor, filename, load_run_id):
    """Read one SQL file and return records as dictionaries keyed by column name."""
    sql = (VALIDATION_SQL_DIR / filename).read_text(encoding="utf-8-sig")
    cursor.execute(sql, (load_run_id,))

    column_names = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(column_names, row)) for row in rows]


def validate_data(cursor, load_run_id):
    """Return each dataset's categorized records for the supplied load ID.

    Each record includes source values, tracking metadata, VALIDATION_STATUS,
    VALIDATION_RULE_IDS, and VALIDATION_MESSAGES. Business-rule failures are
    returned as categories, not Python exceptions. SQL/connection errors
    propagate and stop execution. A dataset with no rows returns an empty list.
    This collects results only; it does not insert CLEAN or QUARANTINE records.
    """
    if not isinstance(load_run_id, str) or not load_run_id.strip():
        raise ValueError("A nonempty load_run_id is required for data validation.")

    results = {}
    for dataset, filename in DATASET_VALIDATIONS:
        results[dataset] = run_validation_query(cursor, filename, load_run_id)

    return results
