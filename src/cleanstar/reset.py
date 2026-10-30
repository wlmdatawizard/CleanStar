"""Clear existing CleanStar records before a fresh run."""

from io import StringIO
from pathlib import Path


def reset_tables():
    """Execute the reset SQL using the setup user's administrative role."""
    from cleanstar.connection import get_snowflake_connection

    sql_path = Path(__file__).resolve().parents[2] / "sql/reset_cleanstar.sql"
    sql = sql_path.read_text(encoding="utf-8-sig")
    print("Clearing all 12 CleanStar raw, clean, and quarantine tables...")
    with get_snowflake_connection(setup=True) as connection:
        for cursor in connection.execute_stream(StringIO(sql)):
            cursor.close()
    print("CleanStar reset completed.")
