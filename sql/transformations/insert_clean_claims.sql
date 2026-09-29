-- Insert prepared, typed values from categorized_claims.sql.
-- Parameters: categorized claims temporary table name, then LOAD_RUN_ID.
-- Use the same Snowflake session as preparation and categorization.
-- Run both destination inserts once per load, together in a transaction.
-- These statements append rows; rerunning them would insert duplicates.
INSERT INTO CLEANSTAR.CLEAN.BILLING_CLAIMS_CLEAN (
    CLAIM_ID, ENCOUNTER_ID, PATIENT_ID, PROVIDER_ID, ORGANIZATION_ID, PAYER_ID, INSURANCE_PLAN_NAME, MEMBER_ID, GROUP_NUMBER, RELATIONSHIP_TO_INSURED, PATIENT_FIRST_NAME, PATIENT_MIDDLE_INITIAL, PATIENT_LAST_NAME, PATIENT_SUFFIX, PATIENT_BIRTHDATE, PATIENT_GENDER, PATIENT_ADDRESS, PATIENT_CITY, PATIENT_STATE, PATIENT_ZIP, PATIENT_PHONE, SERVICE_START_DATETIME, SERVICE_END_DATETIME, ENCOUNTER_CLASS, PROCEDURE_CODE, PROCEDURE_DESCRIPTION, DIAGNOSIS_CODE, DIAGNOSIS_DESCRIPTION, CLAIM_AMOUNT, PROVIDER_NAME, PROVIDER_NPI, PROVIDER_SPECIALTY, CLAIM_STATUS, CLAIM_CREATED_DATETIME,
    VALIDATION_ERROR_COUNT,
    VALIDATION_ERRORS,
    LOAD_RUN_ID,
    SOURCE_FILE,
    INGESTED_AT,
    SOURCE_ROW_HASH,
    VALIDATION_STATUS,
    VALIDATION_RULE_IDS,
    VALIDATION_MESSAGES
)
SELECT
    categorized_claims.CLAIM_ID, categorized_claims.ENCOUNTER_ID, categorized_claims.PATIENT_ID, categorized_claims.PROVIDER_ID, categorized_claims.ORGANIZATION_ID, categorized_claims.PAYER_ID, categorized_claims.INSURANCE_PLAN_NAME, categorized_claims.MEMBER_ID, categorized_claims.GROUP_NUMBER, categorized_claims.RELATIONSHIP_TO_INSURED, categorized_claims.PATIENT_FIRST_NAME, categorized_claims.PATIENT_MIDDLE_INITIAL, categorized_claims.PATIENT_LAST_NAME, categorized_claims.PATIENT_SUFFIX, categorized_claims.PATIENT_BIRTHDATE, categorized_claims.PATIENT_GENDER, categorized_claims.PATIENT_ADDRESS, categorized_claims.PATIENT_CITY, categorized_claims.PATIENT_STATE, categorized_claims.PATIENT_ZIP, categorized_claims.PATIENT_PHONE, categorized_claims.SERVICE_START_DATETIME, categorized_claims.SERVICE_END_DATETIME, categorized_claims.ENCOUNTER_CLASS, categorized_claims.PROCEDURE_CODE, categorized_claims.PROCEDURE_DESCRIPTION, categorized_claims.DIAGNOSIS_CODE, categorized_claims.DIAGNOSIS_DESCRIPTION, categorized_claims.CLAIM_AMOUNT, categorized_claims.PROVIDER_NAME, categorized_claims.PROVIDER_NPI, categorized_claims.PROVIDER_SPECIALTY, categorized_claims.CLAIM_STATUS, categorized_claims.CLAIM_CREATED_DATETIME,
    categorized_claims.VALIDATION_ERROR_COUNT,
    categorized_claims.VALIDATION_ERRORS,
    categorized_claims.LOAD_RUN_ID,
    categorized_claims.SOURCE_FILE,
    categorized_claims.INGESTED_AT,
    categorized_claims.SOURCE_ROW_HASH,
    categorized_claims.VALIDATION_STATUS,
    categorized_claims.VALIDATION_RULE_IDS,
    categorized_claims.VALIDATION_MESSAGES
FROM IDENTIFIER(%s) AS categorized_claims
WHERE categorized_claims.LOAD_RUN_ID = %s
  AND categorized_claims.VALIDATION_STATUS = 'CLEAN';
