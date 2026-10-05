"""Run CleanStar: python run_cleanstar.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# The project source folder must be available before this import.
from cleanstar.pipeline import main, format_run_report  # pylint: disable=wrong-import-position,import-error


if __name__ == "__main__":
    result = main()
    report = format_run_report(result)
    print(report)

    report_dir = Path(__file__).resolve().parent / "reports"
    report_path = report_dir / (result["load_run_id"] + ".txt")
    try:
        report_dir.mkdir(exist_ok=True)
        report_path.write_text(report + "\n", encoding="utf-8")
    except OSError as error:
        print(
            f"\nPipeline completed, but the report could not be saved to {report_path}.\n"
            f"The report is displayed above. Do not rerun the pipeline just to save it.\n"
            f"File error: {error}",
            file=sys.stderr,
        )
    else:
        print(f"\nReport saved: {report_path}")
