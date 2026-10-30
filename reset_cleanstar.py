"""Empty all 12 test tables: python reset_cleanstar.py. Does not run ingestion."""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "src"))

from cleanstar.reset import reset_tables  # pylint: disable=wrong-import-position,import-error


def main():
    """Clear records without starting ingestion."""
    reset_tables()


if __name__ == "__main__":
    main()
