"""Collect pre-cleaning summary counts without changing or classifying records."""

from pathlib import Path


AUDIT_SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "validation"


def run_audit_query(cursor, filename, load_run_id):
    """Execute an external SQL query and return one dictionary of counts."""
    if not isinstance(load_run_id, str) or not load_run_id.strip():
        raise ValueError("A nonempty load_run_id is required for an audit.")

    sql = (AUDIT_SQL_DIR / filename).read_text(encoding="utf-8-sig")
    cursor.execute(sql, (load_run_id,))
    column_names = [column[0].lower() for column in cursor.description]
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f"Audit query returned no summary: {filename}")
    return dict(zip(column_names, row))


def audit_claims(cursor, load_run_id):
    return run_audit_query(cursor, "audit_claims.sql", load_run_id)


def audit_encounter(cursor, load_run_id):
    return run_audit_query(cursor, "audit_encounter.sql", load_run_id)


def audit_patient(cursor, load_run_id):
    return run_audit_query(cursor, "audit_patient.sql", load_run_id)


def audit_provider(cursor, load_run_id):
    return run_audit_query(cursor, "audit_provider.sql", load_run_id)


def run_raw_audit(cursor, load_run_id):
    """Collect four summaries. The caller owns the cursor and connection.

    SQL errors propagate. Issue counts are report data, not exceptions.
    No printing, table writes, or row-level results are performed here.
    """
    return {
        "claims": audit_claims(cursor, load_run_id),
        "encounters": audit_encounter(cursor, load_run_id),
        "patients": audit_patient(cursor, load_run_id),
        "providers": audit_provider(cursor, load_run_id),
    }


def format_audit_report(results, load_run_id):
    """Return a readable report from existing summaries without querying data."""
    lines = [
        "CLEANSTAR PRE-CLEANING AUDIT",
        "=" * 40,
        f"Load Run ID: {load_run_id}",
    ]

    for dataset in ("claims", "encounters", "patients", "providers"):
        lines.extend(["", f"[{dataset.title()}]"])
        for metric, count in results[dataset].items():
            label = metric.replace("_", " ").title().replace("Ids", "IDs")
            lines.append(f"{label + ':':<28} {count:>10,}")

    lines.extend([
        "",
        "Counts describe raw data for this load before cleaning.",
        "Issue counts can overlap; one record may have multiple issues.",
    ])
    return "\n".join(lines)


def print_audit_report(results, load_run_id):
    """Display the pre-cleaning report in the terminal."""
    print(format_audit_report(results, load_run_id))
