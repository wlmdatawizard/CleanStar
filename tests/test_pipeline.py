"""Offline workflow tests; no account, network, or source data required."""

import sys
import unittest
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cleanstar import pipeline


class PipelineTests(unittest.TestCase):
    def setup_run(self, stack, fail=None):
        connection = MagicMock()
        cursor = connection.cursor.return_value
        connection.__enter__.return_value = connection
        cursor.__enter__.return_value = cursor
        connection.__exit__.side_effect = lambda *args: connection.close() and False
        cursor.__exit__.side_effect = lambda *args: cursor.close() and False
        stack.enter_context(patch("builtins.print"))
        counts = {table.rsplit(".", 1)[-1]: 10 for _, table, _ in pipeline.RAW_LOADS}
        values = {
            "get_source_row_counts": counts,
            "create_load_context": ("run-123", datetime(2026, 10, 2, tzinfo=timezone.utc)),
            "get_snowflake_connection": connection,
            "validate_setup": None, "upload_files": [], "validate_staged_files": [],
            "load_raw_tables": [], "get_load_row_counts": counts,
            "run_raw_audit": {k: {"total_rows": 10} for k in ("claims", "encounters", "patients", "providers")},
        }
        for dataset in ("claims", "encounter", "patient", "provider"):
            values["transform_" + dataset] = {"clean_rows": 8, "quarantine_rows": 2}
        calls = []
        mocks = {}
        for name, value in values.items():
            def effect(*args, _name=name, _value=value):
                calls.append(_name)
                if _name == fail:
                    raise RuntimeError("simulated failure")
                return _value
            mocks[name] = stack.enter_context(patch.object(pipeline, name, side_effect=effect))
        return connection, cursor, calls, mocks

    def test_success_order_summary_and_cleanup(self):
        with ExitStack() as stack:
            connection, cursor, calls, mocks = self.setup_run(stack)
            result = pipeline.main()
            self.assertEqual(calls[-4:], ["transform_claims", "transform_encounter", "transform_patient", "transform_provider"])
            self.assertLess(calls.index("validate_staged_files"), calls.index("load_raw_tables"))
            self.assertLess(calls.index("run_raw_audit"), calls.index("transform_claims"))
            for name in calls[-4:]:
                mocks[name].assert_called_once_with(cursor, "run-123")
            self.assertIn("clean=8, quarantine=2", pipeline.format_run_report(result))
            cursor.close.assert_called_once()
            connection.close.assert_called_once()

    def test_every_database_phase_failure_closes_resources_and_stops(self):
        phases = ["validate_setup", "upload_files", "validate_staged_files", "load_raw_tables", "get_load_row_counts", "run_raw_audit", "transform_claims", "transform_encounter", "transform_patient", "transform_provider"]
        for phase in phases:
            with self.subTest(phase=phase), ExitStack() as stack:
                connection, cursor, calls, _ = self.setup_run(stack, phase)
                with self.assertRaisesRegex(RuntimeError, "simulated failure"):
                    pipeline.main()
                self.assertEqual(calls[-1], phase)
                cursor.close.assert_called_once()
                connection.close.assert_called_once()

    def test_cursor_creation_failure_closes_connection(self):
        with ExitStack() as stack:
            connection, _, _, _ = self.setup_run(stack)
            connection.cursor.side_effect = RuntimeError("cursor unavailable")
            with self.assertRaises(RuntimeError):
                pipeline.main()
            connection.close.assert_called_once()

    def test_cursor_close_failure_still_closes_connection(self):
        with ExitStack() as stack:
            connection, cursor, _, _ = self.setup_run(stack)
            cursor.close.side_effect = RuntimeError("close unavailable")
            with self.assertRaises(RuntimeError):
                pipeline.main()
            connection.close.assert_called_once()

    def test_count_mismatch_stops_before_audit(self):
        with ExitStack() as stack:
            _, _, _, mocks = self.setup_run(stack)
            counts = {table.rsplit(".", 1)[-1]: 5 for _, table, _ in pipeline.RAW_LOADS}
            mocks["get_load_row_counts"].side_effect = lambda *args: counts
            with self.assertRaisesRegex(RuntimeError, "Source/load row count mismatch"):
                pipeline.main()
            mocks["run_raw_audit"].assert_not_called()

    def test_reconciliation_reports_skips_and_empty_sources(self):
        result = pipeline.reconcile_load_counts({"a": 10, "b": 0}, {"a": 0, "b": 0})
        self.assertEqual([r["status"] for r in result.values()], ["NO_NEW_ROWS", "MATCH"])



if __name__ == "__main__":
    unittest.main()
