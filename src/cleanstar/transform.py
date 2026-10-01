"""Run dataset transformations using SQL files and a caller-owned cursor.

Use a dedicated pipeline session with no active transaction; finish ingestion
before calling these functions. Temporary-table creation commits in Snowflake,
so preparation and categorization happen before the insert transaction.
Call each function once per load. These are append operations, not retry-safe
upserts. Temporary tables remain until the caller closes the session.
"""

import logging
from pathlib import Path


TRANSFORM_SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "transformations"


def read_transform_sql(filename):
    """Read a transformation SQL file."""
    return (TRANSFORM_SQL_DIR / filename).read_text(encoding="utf-8-sig")


def transform_dataset(cursor, dataset, load_run_id):
    """Prepare, categorize, and insert one dataset; return inserted row counts.

Both destination inserts commit together. Errors propagate to the caller;
an insert failure rolls back both inserts. Previously completed datasets are
not rolled back. The caller owns and closes the cursor and connection.
Timestamps without a source offset are interpreted as UTC for this session.
"""
    if dataset not in ("claims", "encounter", "patient", "provider"):
        raise ValueError(f"Unknown transformation dataset: {dataset}")
    if not isinstance(load_run_id, str) or not load_run_id.strip():
        raise ValueError("A nonempty load_run_id is required for transformation.")

    # Read every script before executing anything, including failure handling.
    filenames = {
        "timezone": "set_transform_timezone.sql",
        "prepare": f"prepare_{dataset}.sql",
        "categorize": f"categorized_{dataset}.sql",
        "clean": f"insert_clean_{dataset}.sql",
        "quarantine": f"insert_quarantine_{dataset}.sql",
        "begin": "begin_transaction.sql",
        "commit": "commit_transaction.sql",
        "rollback": "rollback_transaction.sql",
    }
    scripts = {step: read_transform_sql(name) for step, name in filenames.items()}
    parameters = (load_run_id,)

    cursor.execute(scripts["timezone"])
    cursor.execute(scripts["prepare"], parameters)
    cursor.execute(scripts["categorize"], parameters)

    cursor.execute(scripts["begin"])
    try:
        cursor.execute(scripts["clean"], parameters)
        clean_rows = cursor.rowcount
        cursor.execute(scripts["quarantine"], parameters)
        quarantine_rows = cursor.rowcount
        cursor.execute(scripts["commit"])
    except BaseException:
        try:
            cursor.execute(scripts["rollback"])
        except Exception:
            logging.getLogger(__name__).exception(
                "Rollback failed for %s; inspect the load before retrying.", dataset
            )
        raise

    return {"clean_rows": clean_rows, "quarantine_rows": quarantine_rows}


def transform_claims(cursor, load_run_id):
    return transform_dataset(cursor, "claims", load_run_id)


def transform_encounter(cursor, load_run_id):
    return transform_dataset(cursor, "encounter", load_run_id)


def transform_patient(cursor, load_run_id):
    return transform_dataset(cursor, "patient", load_run_id)


def transform_provider(cursor, load_run_id):
    return transform_dataset(cursor, "provider", load_run_id)
