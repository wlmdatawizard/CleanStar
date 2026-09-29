"""Business-rule IDs, descriptions, and actions for CleanStar.

Claims conditions live in sql/transformations/classify_claims.sql.
Other dataset rules remain reference definitions until implemented.
This catalog contains data only; CLM-010 through CLM-014 cover typed clean fields.
"""

VALIDATION_RULES = [
    {
        "rule_id": "CLM-001", "dataset": "Claims", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CURRENT_LOAD",
        "description": "Exact duplicate row within current load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "CLM-002", "dataset": "Claims", "field": "CLAIM_ID",
        "category": "CONSISTENCY", "scope": "CURRENT_LOAD",
        "description": "ID is reused by conflicting records within current load",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-003", "dataset": "Claims", "field": "CLAIM_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Claim ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-004", "dataset": "Claims", "field": "PATIENT_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Patient ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-005", "dataset": "Claims", "field": "ENCOUNTER_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Encounter ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-006", "dataset": "Claims", "field": "CLAIM_AMOUNT",
        "category": "VALIDITY", "scope": "ROW",
        "description": "Claim amount must be numeric", "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-007", "dataset": "Claims", "field": "CLAIM_AMOUNT",
        "category": "VALIDITY", "scope": "ROW",
        "description": "Claim amount must not be negative", "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-008", "dataset": "Claims", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CLEAN_HISTORY",
        "description": "Exact record already exists in CLEAN from an earlier load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "CLM-009", "dataset": "Claims", "field": "CLAIM_ID",
        "category": "CONSISTENCY", "scope": "CLEAN_HISTORY",
        "description": "ID conflicts with a CLEAN record from an earlier load",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-010",
        "dataset": "Claims",
        "field": "PATIENT_BIRTHDATE",
        "category": "VALIDITY",
        "scope": "ROW",
        "description": "Patient birthdate must be a valid date",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-011",
        "dataset": "Claims",
        "field": "SERVICE_START_DATETIME",
        "category": "VALIDITY",
        "scope": "ROW",
        "description": "Service start must be a valid timestamp",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-012",
        "dataset": "Claims",
        "field": "SERVICE_END_DATETIME",
        "category": "VALIDITY",
        "scope": "ROW",
        "description": "Service end must be a valid timestamp",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-013",
        "dataset": "Claims",
        "field": "CLAIM_CREATED_DATETIME",
        "category": "VALIDITY",
        "scope": "ROW",
        "description": "Claim created time must be a valid timestamp",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "CLM-014",
        "dataset": "Claims",
        "field": "VALIDATION_ERROR_COUNT",
        "category": "VALIDITY",
        "scope": "ROW",
        "description": "Validation error count must be a representable integer",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "ENC-001", "dataset": "Encounters", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CURRENT_LOAD",
        "description": "Exact duplicate row within current load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "ENC-002", "dataset": "Encounters", "field": "ENCOUNTER_ID",
        "category": "CONSISTENCY", "scope": "CURRENT_LOAD",
        "description": "ID is reused by conflicting records within current load",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "ENC-003", "dataset": "Encounters", "field": "ENCOUNTER_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Encounter ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "ENC-004", "dataset": "Encounters", "field": "PATIENT_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Patient ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "ENC-005", "dataset": "Encounters", "field": "PROVIDER_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Provider ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "ENC-006", "dataset": "Encounters", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CLEAN_HISTORY",
        "description": "Exact record already exists in CLEAN from an earlier load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "ENC-007", "dataset": "Encounters", "field": "ENCOUNTER_ID",
        "category": "CONSISTENCY", "scope": "CLEAN_HISTORY",
        "description": "ID conflicts with a CLEAN record from an earlier load",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "PAT-001", "dataset": "Patients", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CURRENT_LOAD",
        "description": "Exact duplicate row within current load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "PAT-002", "dataset": "Patients", "field": "PATIENT_ID",
        "category": "CONSISTENCY", "scope": "CURRENT_LOAD",
        "description": "ID is reused by conflicting records within current load",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "PAT-003", "dataset": "Patients", "field": "PATIENT_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Patient ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "PAT-004", "dataset": "Patients", "field": "BIRTHDATE",
        "category": "VALIDITY", "scope": "ROW",
        "description": "Birthdate must be a valid date", "action": "QUARANTINE",
    },
    {
        "rule_id": "PAT-005", "dataset": "Patients", "field": "ZIP",
        "category": "VALIDITY", "scope": "ROW",
        "description": "ZIP must contain 5 digits or ZIP+4", "action": "WARNING",
    },
    {
        "rule_id": "PAT-006", "dataset": "Patients", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CLEAN_HISTORY",
        "description": "Exact record already exists in CLEAN from an earlier load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "PAT-007", "dataset": "Patients", "field": "PATIENT_ID",
        "category": "CONSISTENCY", "scope": "CLEAN_HISTORY",
        "description": "ID conflicts with a CLEAN record from an earlier load",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "PRO-001", "dataset": "Providers", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CURRENT_LOAD",
        "description": "Exact duplicate row within current load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "PRO-002", "dataset": "Providers", "field": "PROVIDER_ID",
        "category": "CONSISTENCY", "scope": "CURRENT_LOAD",
        "description": "ID is reused by conflicting records within current load",
        "action": "QUARANTINE",
    },
    {
        "rule_id": "PRO-003", "dataset": "Providers", "field": "PROVIDER_ID",
        "category": "COMPLETENESS", "scope": "ROW",
        "description": "Provider ID is required", "action": "QUARANTINE",
    },
    {
        "rule_id": "PRO-004", "dataset": "Providers", "field": "NPI",
        "category": "VALIDITY", "scope": "ROW",
        "description": "NPI must contain exactly 10 digits", "action": "WARNING",
    },
    {
        "rule_id": "PRO-005", "dataset": "Providers", "field": "Entire row",
        "category": "UNIQUENESS", "scope": "CLEAN_HISTORY",
        "description": "Exact record already exists in CLEAN from an earlier load",
        "action": "DEDUPLICATE",
    },
    {
        "rule_id": "PRO-006", "dataset": "Providers", "field": "PROVIDER_ID",
        "category": "CONSISTENCY", "scope": "CLEAN_HISTORY",
        "description": "ID conflicts with a CLEAN record from an earlier load",
        "action": "QUARANTINE",
    },
]
