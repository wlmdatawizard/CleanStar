"""Check setup order and failure handling without a Snowflake account."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.connection.__enter__.return_value = self.connection
        module = types.ModuleType("cleanstar.connection")
        self.connect = module.get_snowflake_connection = MagicMock(return_value=self.connection)
        path = Path(__file__).resolve().parents[1] / "setup_cleanstar.py"
        spec = importlib.util.spec_from_file_location("setup_under_test", path)
        self.setup = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"cleanstar.connection": module}):
            spec.loader.exec_module(self.setup)

    def test_runs_all_files_in_order_and_closes_statement_cursors(self):
        executed = []
        cursors = []

        def execute(stream):
            executed.append(stream.read())
            cursor = MagicMock()
            cursors.append(cursor)
            yield cursor

        self.connection.execute_stream.side_effect = execute
        with patch("builtins.print"):
            self.setup.main()
        self.connect.assert_called_once_with(setup=True)
        self.assertEqual(len(executed), 10)
        for name, sql in zip(self.setup.SETUP_FILES, executed):
            self.assertEqual(sql, (self.setup.PROJECT_DIR / "sql" / name).read_text(encoding="utf-8-sig"))
        self.assertIn("USE ROLE SECURITYADMIN", executed[0])
        self.assertIn("GRANT USAGE ON WAREHOUSE", executed[-1])
        for cursor in cursors:
            cursor.close.assert_called_once()
        self.connection.__exit__.assert_called_once()

    def test_sql_failure_stops_setup_and_exits_connection(self):
        error = RuntimeError("simulated SQL failure")
        self.connection.execute_stream.side_effect = error
        with patch("builtins.print"), self.assertRaises(RuntimeError) as caught:
            self.setup.main()
        self.assertIs(caught.exception, error)
        self.connection.execute_stream.assert_called_once()
        self.connection.__exit__.assert_called_once()

    def test_missing_sql_stops_before_connecting(self):
        with patch.object(Path, "read_text", side_effect=FileNotFoundError("missing SQL")):
            with self.assertRaises(FileNotFoundError):
                self.setup.main()
        self.connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
