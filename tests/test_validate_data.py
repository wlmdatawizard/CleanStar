"""Offline checks for query execution and result handling; no Snowflake login."""

import unittest
from unittest.mock import Mock

from cleanstar.validate_data import validate_data


class ValidateDataTests(unittest.TestCase):
    def test_queries_use_same_run_and_preserve_categories(self):
        cursor = Mock()
        cursor.description = [
            ("CLAIM_ID",), ("VALIDATION_STATUS",),
            ("VALIDATION_RULE_IDS",), ("VALIDATION_MESSAGES",),
        ]
        cursor.fetchall.side_effect = [
            [("claim-1", "QUARANTINED", "CLM-006", "Claim amount must be numeric")],
            [], [], [],
        ]

        results = validate_data(cursor, "run-123")

        self.assertEqual(list(results), ["claims", "encounters", "patients", "providers"])
        self.assertEqual(results["claims"][0]["VALIDATION_STATUS"], "QUARANTINED")
        self.assertEqual(results["claims"][0]["VALIDATION_RULE_IDS"], "CLM-006")
        self.assertEqual(results["providers"], [])
        expected_tables = ["BILLING_CLAIMS_RAW", "ENCOUNTER_INFO_RAW",
                           "PATIENT_INFO_RAW", "PROVIDER_INFO_RAW"]
        self.assertEqual(cursor.execute.call_count, 4)
        for call, table in zip(cursor.execute.call_args_list, expected_tables):
            sql, parameters = call.args
            self.assertIn("CLEANSTAR.RAW." + table, sql)
            self.assertEqual(sql.count("%s"), 1)
            self.assertEqual(parameters, ("run-123",))
        cursor.close.assert_not_called()

    def test_sql_error_stops_remaining_queries(self):
        cursor = Mock()
        failure = RuntimeError("Simulated inaccessible table")
        cursor.execute.side_effect = failure
        with self.assertRaises(RuntimeError) as raised:
            validate_data(cursor, "run-123")
        self.assertIs(raised.exception, failure)
        self.assertEqual(cursor.execute.call_count, 1)
        cursor.fetchall.assert_not_called()

    def test_missing_run_id_fails_before_queries(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                cursor = Mock()
                with self.assertRaises(ValueError):
                    validate_data(cursor, value)
                cursor.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
