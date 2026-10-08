"""Empty all 12 test tables: python reset_cleanstar.py. Does not run ingestion."""

import sys
from io import StringIO
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from cleanstar.connection import get_snowflake_connection  # pylint: disable=wrong-import-position,import-error


def main():
    """Run the reset SQL with the same administrative user used for setup."""
    sql = (PROJECT_DIR / "sql/reset_cleanstar.sql").read_text(encoding="utf-8-sig")
    print("Clearing all 12 CleanStar raw, clean, and quarantine tables...")
    with get_snowflake_connection(setup=True) as connection:
        for cursor in connection.execute_stream(StringIO(sql)):
            cursor.close()
    print("CleanStar reset completed. Table definitions and source files preserved.")


if __name__ == "__main__":
    main()
