"""Dataset and table configuration for CleanStar.

Define source filenames, destination tables, column mappings, and load metadata
here as ingestion is implemented. Snowflake connection settings live in config.py.
"""

# Clean source columns not listed here remain VARCHAR.
# RAW and QUARANTINE source columns always remain VARCHAR.
# Apply these types when generating clean_tables.sql; SQL files do not read Python.
CLEAN_COLUMN_TYPES = {
    "PATIENT_BIRTHDATE": "DATE",
    "BIRTHDATE": "DATE",
    "COVERAGE_START_DATE": "DATE",
    "COVERAGE_END_DATE": "DATE",
    "SERVICE_START_DATETIME": "TIMESTAMP_TZ",
    "SERVICE_END_DATETIME": "TIMESTAMP_TZ",
    "CLAIM_CREATED_DATETIME": "TIMESTAMP_TZ",
    "START_DATETIME": "TIMESTAMP_TZ",
    "END_DATETIME": "TIMESTAMP_TZ",
    "CLAIM_AMOUNT": "NUMBER(18, 2)",
    "BASE_ENCOUNTER_COST": "NUMBER(18, 2)",
    "VALIDATION_ERROR_COUNT": "NUMBER(38, 0)",
}

RAW_LOADS = [
    (
        "billing_claims_dirty.csv.gz",
        "CLEANSTAR.RAW.BILLING_CLAIMS_RAW",
        (
            "CLAIM_ID", "ENCOUNTER_ID", "PATIENT_ID", "PROVIDER_ID",
            "ORGANIZATION_ID", "PAYER_ID", "INSURANCE_PLAN_NAME",
            "MEMBER_ID", "GROUP_NUMBER", "RELATIONSHIP_TO_INSURED",
            "PATIENT_FIRST_NAME", "PATIENT_MIDDLE_INITIAL",
            "PATIENT_LAST_NAME", "PATIENT_SUFFIX", "PATIENT_BIRTHDATE",
            "PATIENT_GENDER", "PATIENT_ADDRESS", "PATIENT_CITY",
            "PATIENT_STATE", "PATIENT_ZIP", "PATIENT_PHONE",
            "SERVICE_START_DATETIME", "SERVICE_END_DATETIME",
            "ENCOUNTER_CLASS", "PROCEDURE_CODE", "PROCEDURE_DESCRIPTION",
            "DIAGNOSIS_CODE", "DIAGNOSIS_DESCRIPTION", "CLAIM_AMOUNT",
            "PROVIDER_NAME", "PROVIDER_NPI", "PROVIDER_SPECIALTY",
            "CLAIM_STATUS", "CLAIM_CREATED_DATETIME",
            "VALIDATION_ERROR_COUNT", "VALIDATION_ERRORS"
        )
    ),
    (
        "encounter_info_dirty.csv.gz",
        "CLEANSTAR.RAW.ENCOUNTER_INFO_RAW",
        (
            "ENCOUNTER_ID", "START_DATETIME", "END_DATETIME", "PATIENT_ID",
            "ORGANIZATION_ID", "PROVIDER_ID", "ENCOUNTER_CLASS",
            "ENCOUNTER_CODE", "ENCOUNTER_DESCRIPTION", "DIAGNOSIS_CODE",
            "DIAGNOSIS_DESCRIPTION", "BASE_ENCOUNTER_COST"
        )
    ),
    (
        "patient_info_dirty.csv.gz",
        "CLEANSTAR.RAW.PATIENT_INFO_RAW",
        (
            "PATIENT_ID", "BIRTHDATE", "FIRST_NAME", "MIDDLE_INITIAL",
            "LAST_NAME", "SUFFIX", "GENDER", "ADDRESS", "CITY", "STATE",
            "ZIP", "PHONE", "PAYER_ID", "INSURANCE_PLAN_NAME", "MEMBER_ID",
            "GROUP_NUMBER", "RELATIONSHIP_TO_INSURED", "COVERAGE_START_DATE",
            "COVERAGE_END_DATE", "COVERAGE_STATUS"
        )
    ),
    (
        "provider_info_dirty.csv.gz",
        "CLEANSTAR.RAW.PROVIDER_INFO_RAW",
        (
            "PROVIDER_ID", "ORGANIZATION_ID", "PROVIDER_NAME", "SPECIALTY",
            "NPI"
        )
    )
]


RAW_METADATA_COLUMNS = (
    ("LOAD_RUN_ID", "VARCHAR"),
    ("SOURCE_FILE", "VARCHAR"),
    ("INGESTED_AT", "TIMESTAMP_TZ"),
)


QUALITY_METADATA_COLUMNS = (
    ("SOURCE_ROW_HASH", "NUMBER(38, 0)"),
    ("VALIDATION_STATUS", "VARCHAR"),
    ("VALIDATION_RULE_IDS", "VARCHAR"),
    ("VALIDATION_MESSAGES", "VARCHAR"),
)


CURATED_TABLES = {
    "CLEANSTAR.RAW.BILLING_CLAIMS_RAW": {
        "clean_table": "CLEANSTAR.CLEAN.BILLING_CLAIMS_CLEAN",
        "quarantine_table": (
            "CLEANSTAR.QUARANTINE.BILLING_CLAIMS_QUARANTINE"
        ),
    },
    "CLEANSTAR.RAW.ENCOUNTER_INFO_RAW": {
        "clean_table": "CLEANSTAR.CLEAN.ENCOUNTER_INFO_CLEAN",
        "quarantine_table": (
            "CLEANSTAR.QUARANTINE.ENCOUNTER_INFO_QUARANTINE"
        ),
    },
    "CLEANSTAR.RAW.PATIENT_INFO_RAW": {
        "clean_table": "CLEANSTAR.CLEAN.PATIENT_INFO_CLEAN",
        "quarantine_table": (
            "CLEANSTAR.QUARANTINE.PATIENT_INFO_QUARANTINE"
        ),
    },
    "CLEANSTAR.RAW.PROVIDER_INFO_RAW": {
        "clean_table": "CLEANSTAR.CLEAN.PROVIDER_INFO_CLEAN",
        "quarantine_table": (
            "CLEANSTAR.QUARANTINE.PROVIDER_INFO_QUARANTINE"
        ),
    },
}
