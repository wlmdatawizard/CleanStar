"""Create CleanStar's Snowflake objects: python setup_cleanstar.py."""

import sys
from io import StringIO
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from cleanstar.connection import get_snowflake_connection  # pylint: disable=wrong-import-position,import-error


SETUP_FILES = (
    "setup/roles.sql",
    "setup/warehouse.sql",
    "setup/database.sql",
    "setup/schemas.sql",
    "setup/file_format.sql",
    "setup/stages.sql",
    "tables/raw_tables.sql",
    "tables/clean_tables.sql",
    "tables/quarantine_tables.sql",
    "setup/grants.sql",
)


def main():
    """Run setup separately from ingestion, using an administrative user.

    The user must be able to use SECURITYADMIN and SYSADMIN. SQL errors stop
    setup; earlier object creation is not rolled back. Existing objects are
    preserved, not updated to match changed definitions.
    """
    # Read all files first so a missing file stops setup before any SQL runs.
    scripts = [(name, (PROJECT_DIR / "sql" / name).read_text(encoding="utf-8-sig"))
               for name in SETUP_FILES]

    with get_snowflake_connection(setup=True) as connection:
        for name, sql in scripts:
            print(f"Running {name}...")
            # The connector executes each statement in this file in order.
            for cursor in connection.execute_stream(StringIO(sql)):
                cursor.close()

    print("CleanStar setup completed. Connection closed.")


if __name__ == "__main__":
    main()
