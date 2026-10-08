"""Test our retry decisions with a simulated connector, no login or real waits."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class Error(Exception):
    def __init__(self, errno, message="Simulated connection failure"):
        super().__init__(message)
        self.errno = errno


class DatabaseError(Error):
    pass


class OperationalError(DatabaseError):
    pass


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        snowflake = types.ModuleType("snowflake")
        connector = types.ModuleType("snowflake.connector")
        errors = types.ModuleType("snowflake.connector.errors")
        codes = types.ModuleType("snowflake.connector.errorcode")
        config = types.ModuleType("cleanstar.config")
        snowflake.connector = connector
        connector.connect = Mock()
        errors.OperationalError = OperationalError
        errors.Error = Error
        errors.DatabaseError = DatabaseError
        codes.ER_CONNECTION_TIMEOUT = 251011
        codes.ER_FAILED_TO_CONNECT_TO_DB = 250001
        codes.ER_RETRYABLE_CODE = 251012
        config.load_settings = Mock(return_value=dict.fromkeys(
            ("user", "password", "account", "warehouse", "database", "schema", "role"), "test"
        ))
        modules = {m.__name__: m for m in (snowflake, connector, errors, codes, config)}
        path = Path(__file__).resolve().parents[1] / "src/cleanstar/connection.py"
        spec = importlib.util.spec_from_file_location("connection_under_test", path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(self.module)
        self.connect = connector.connect
        self.module.sleep = Mock()
        self.addCleanup(patch.stopall)
        self.output = patch("builtins.print").start()

    def test_setup_connection_omits_uncreated_objects(self):
        self.module.get_snowflake_connection(setup=True)
        settings = self.connect.call_args.kwargs
        self.assertEqual(settings["role"], "SECURITYADMIN")
        for name in ("warehouse", "database", "schema"):
            self.assertNotIn(name, settings)
        self.assertEqual(settings["user"], "test")

    def test_pipeline_connection_keeps_configured_objects(self):
        self.module.get_snowflake_connection()
        for name in ("warehouse", "database", "schema", "role"):
            self.assertEqual(self.connect.call_args.kwargs[name], "test")

    def test_success_does_not_wait(self):
        result = self.module.get_snowflake_connection()
        self.assertIs(result, self.connect.return_value)
        self.connect.assert_called_once()
        self.module.sleep.assert_not_called()

    def test_temporary_failure_then_success(self):
        for code in (251011, 250001, 251012):
            with self.subTest(code=code):
                self.connect.reset_mock()
                self.module.sleep.reset_mock()
                connection = object()
                self.connect.side_effect = [OperationalError(code), connection]
                self.assertIs(self.module.get_snowflake_connection(), connection)
                self.assertEqual(self.connect.call_count, 2)
                self.module.sleep.assert_called_once_with(5)

    def test_exhaustion_raises_original_error(self):
        error = OperationalError(251011)
        self.connect.side_effect = error
        with self.assertRaises(OperationalError) as caught:
            self.module.get_snowflake_connection()
        self.assertIs(caught.exception, error)
        self.assertEqual(self.connect.call_count, 3)
        self.assertEqual(self.module.sleep.call_count, 2)

    def test_other_errors_are_not_retried(self):
        for error in (OperationalError(999999), ValueError("configuration"), Exception("authentication")):
            with self.subTest(error=error):
                self.connect.reset_mock()
                self.connect.side_effect = error
                with self.assertRaises(type(error)) as caught:
                    self.module.get_snowflake_connection()
                self.assertIs(caught.exception, error)
                self.connect.assert_called_once()
                self.module.sleep.assert_not_called()

    def test_missing_settings_stop_before_connect(self):
        self.module.load_settings.return_value["password"] = "  "
        self.module.load_settings.return_value["account"] = None
        with self.assertRaisesRegex(ValueError, "SNOWFLAKE_ACCOUNT, SNOWFLAKE_PASSWORD"):
            self.module.get_snowflake_connection()
        self.connect.assert_not_called()
        self.module.sleep.assert_not_called()

    def test_known_errors_get_specific_messages_without_retry(self):
        cases = [
            (Error(390100), "rejected the login"),
            (DatabaseError(390100), "rejected the login"),
            (DatabaseError(987654), "original database error"),
            (DatabaseError(250001), "Unable to reach"),
            (Error(390124), "MFA"),
            (OperationalError(390127), "MFA"),
            (OperationalError(250001, "Role TEST is not assigned to this user"), "role is unavailable"),
            (Error(251009), "Unable to reach"),
            (Error(987654), "original error"),
        ]
        for error, text in cases:
            with self.subTest(code=error.errno):
                self.connect.reset_mock()
                self.output.reset_mock()
                self.connect.side_effect = error
                with self.assertRaises(Error) as caught:
                    self.module.get_snowflake_connection()
                self.assertIs(caught.exception, error)
                self.connect.assert_called_once()
                self.module.sleep.assert_not_called()
                self.assertIn(text, self.output.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
