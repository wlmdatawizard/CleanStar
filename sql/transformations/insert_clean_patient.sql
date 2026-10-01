-- Insert prepared, typed values from categorized_patient.sql.
-- Parameter: LOAD_RUN_ID. Use the same pipeline session.
-- Run both destination inserts once per load, together in a transaction.
-- These statements append rows; rerunning them would insert duplicates.
INSERT INTO CLEANSTAR.CLEAN.PATIENT_INFO_CLEAN (
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
    categorized_patient.PATIENT_ID,
    categorized_patient.BIRTHDATE,
    categorized_patient.FIRST_NAME,
    categorized_patient.MIDDLE_INITIAL,
    categorized_patient.LAST_NAME,
    categorized_patient.SUFFIX,
    categorized_patient.GENDER,
    categorized_patient.ADDRESS,
    categorized_patient.CITY,
    categorized_patient.STATE,
    categorized_patient.ZIP,
    categorized_patient.PHONE,
    categorized_patient.PAYER_ID,
    categorized_patient.INSURANCE_PLAN_NAME,
    categorized_patient.MEMBER_ID,
    categorized_patient.GROUP_NUMBER,
    categorized_patient.RELATIONSHIP_TO_INSURED,
    categorized_patient.COVERAGE_START_DATE,
    categorized_patient.COVERAGE_END_DATE,
    categorized_patient.COVERAGE_STATUS,
    categorized_patient.LOAD_RUN_ID,
    categorized_patient.SOURCE_FILE,
    categorized_patient.INGESTED_AT,
    categorized_patient.SOURCE_ROW_HASH,
    categorized_patient.VALIDATION_STATUS,
    categorized_patient.VALIDATION_RULE_IDS,
    categorized_patient.VALIDATION_MESSAGES
FROM CLEANSTAR.RAW.CATEGORIZED_PATIENT AS categorized_patient
WHERE categorized_patient.LOAD_RUN_ID = %s
  AND categorized_patient.VALIDATION_STATUS IN ('CLEAN', 'WARNING');
