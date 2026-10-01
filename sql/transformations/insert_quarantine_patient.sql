-- Insert original source values, including duplicate records from categorized_patient.sql.
-- Parameter: LOAD_RUN_ID. Use the same pipeline session.
-- Run both destination inserts once per load, together in a transaction.
-- These statements append rows; rerunning them would insert duplicates.
INSERT INTO CLEANSTAR.QUARANTINE.PATIENT_INFO_QUARANTINE (
    PATIENT_ID,
    BIRTHDATE,
    FIRST_NAME,
    MIDDLE_INITIAL,
    LAST_NAME,
    SUFFIX,
    GENDER,
    ADDRESS,
    CITY,
    STATE,
    ZIP,
    PHONE,
    PAYER_ID,
    INSURANCE_PLAN_NAME,
    MEMBER_ID,
    GROUP_NUMBER,
    RELATIONSHIP_TO_INSURED,
    COVERAGE_START_DATE,
    COVERAGE_END_DATE,
    COVERAGE_STATUS,
    LOAD_RUN_ID,
    SOURCE_FILE,
    INGESTED_AT,
    SOURCE_ROW_HASH,
    VALIDATION_STATUS,
    VALIDATION_RULE_IDS,
    VALIDATION_MESSAGES
)
SELECT
    categorized_patient.RAW_PATIENT_ID,
    categorized_patient.RAW_BIRTHDATE,
    categorized_patient.RAW_FIRST_NAME,
    categorized_patient.RAW_MIDDLE_INITIAL,
    categorized_patient.RAW_LAST_NAME,
    categorized_patient.RAW_SUFFIX,
    categorized_patient.RAW_GENDER,
    categorized_patient.RAW_ADDRESS,
    categorized_patient.RAW_CITY,
    categorized_patient.RAW_STATE,
    categorized_patient.RAW_ZIP,
    categorized_patient.RAW_PHONE,
    categorized_patient.RAW_PAYER_ID,
    categorized_patient.RAW_INSURANCE_PLAN_NAME,
    categorized_patient.RAW_MEMBER_ID,
    categorized_patient.RAW_GROUP_NUMBER,
    categorized_patient.RAW_RELATIONSHIP_TO_INSURED,
    categorized_patient.RAW_COVERAGE_START_DATE,
    categorized_patient.RAW_COVERAGE_END_DATE,
    categorized_patient.RAW_COVERAGE_STATUS,
    categorized_patient.LOAD_RUN_ID,
    categorized_patient.SOURCE_FILE,
    categorized_patient.INGESTED_AT,
    categorized_patient.SOURCE_ROW_HASH,
    categorized_patient.VALIDATION_STATUS,
    categorized_patient.VALIDATION_RULE_IDS,
    categorized_patient.VALIDATION_MESSAGES
FROM CLEANSTAR.RAW.CATEGORIZED_PATIENT AS categorized_patient
WHERE categorized_patient.LOAD_RUN_ID = %s
  AND categorized_patient.VALIDATION_STATUS IN ('QUARANTINED', 'DEDUPLICATED');
