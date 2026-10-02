"""Offline orchestration checks; these do not execute Snowflake SQL."""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
# Import after adding src so tests run directly from the checkout.
from cleanstar import transform  # pylint: disable=wrong-import-position,import-error


class TransformTests(unittest.TestCase):
    def cursor_for(self, fail_step=None):
        cursor = Mock()
        cursor.steps = []

        def execute(sql, parameters=None):
            statement = "\n".join(
                line for line in sql.splitlines() if not line.startswith("--")
            ).strip()
            step = statement.split()[0].rstrip(";")
            if step == "CREATE":
                step = "categorize" if "CATEGORIZED_" in statement else "prepare"
            elif step == "INSERT":
                step = "quarantine" if "INSERT INTO CLEANSTAR.QUARANTINE." in statement else "clean"
            cursor.steps.append(step)
            if step in ("prepare", "categorize", "clean", "quarantine"):
                self.assertEqual(parameters, ("run-123",))
                self.assertEqual(sql.count("%s"), 1)
            else:
                self.assertIsNone(parameters)
            if step == fail_step:
                raise RuntimeError("simulated failure")
            cursor.rowcount = 8 if step == "clean" else 2

        cursor.execute.side_effect = execute
        return cursor

    def test_all_datasets_run_in_order_and_return_counts(self):
        for dataset in ("claims", "encounter", "patient", "provider"):
            with self.subTest(dataset=dataset):
                cursor = self.cursor_for()
                result = getattr(transform, "transform_" + dataset)(cursor, "run-123")
                self.assertEqual(result, {"clean_rows": 8, "quarantine_rows": 2})
                self.assertEqual(cursor.steps, ["ALTER", "prepare", "categorize", "BEGIN", "clean", "quarantine", "COMMIT"])
                executed = "\n".join(call.args[0] for call in cursor.execute.call_args_list)
                self.assertIn("CLEANSTAR.RAW.CATEGORIZED_" + dataset.upper(), executed)
                cursor.close.assert_not_called()

    def test_insert_failures_roll_back_and_propagate(self):
        for step in ("clean", "quarantine", "COMMIT"):
            with self.subTest(step=step):
                cursor = self.cursor_for(step)
                with self.assertRaisesRegex(RuntimeError, "simulated failure"):
                    transform.transform_claims(cursor, "run-123")
                self.assertEqual(cursor.steps[-1], "ROLLBACK")

    def test_preparation_failure_prevents_inserts(self):
        cursor = self.cursor_for("prepare")
        with self.assertRaises(RuntimeError):
            transform.transform_patient(cursor, "run-123")
        self.assertEqual(cursor.steps, ["ALTER", "prepare"])

    def test_bad_inputs_do_not_execute_sql(self):
        cursor = Mock()
        for run_id in (None, "", "   "):
            with self.assertRaises(ValueError):
                transform.transform_provider(cursor, run_id)
        with self.assertRaises(ValueError):
            transform.transform_dataset(cursor, "unknown", "run-123")
        cursor.execute.assert_not_called()

    def test_missing_script_fails_before_any_execution(self):
        cursor = Mock()
        reader = transform.read_transform_sql

        def read(filename):
            if filename == "rollback_transaction.sql":
                raise FileNotFoundError(filename)
            return reader(filename)

        with patch.object(transform, "read_transform_sql", side_effect=read):
            with self.assertRaises(FileNotFoundError):
                transform.transform_encounter(cursor, "run-123")
        cursor.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
