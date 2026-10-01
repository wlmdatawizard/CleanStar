-- Insert original source values, including duplicate records from categorized_encounter.sql.
-- Parameter: LOAD_RUN_ID. Use the same pipeline session.
-- Run both destination inserts once per load, together in a transaction.
-- These statements append rows; rerunning them would insert duplicates.
INSERT INTO CLEANSTAR.QUARANTINE.ENCOUNTER_INFO_QUARANTINE (
    ENCOUNTER_ID,
    START_DATETIME,
    END_DATETIME,
    PATIENT_ID,
    ORGANIZATION_ID,
    PROVIDER_ID,
    ENCOUNTER_CLASS,
    ENCOUNTER_CODE,
    ENCOUNTER_DESCRIPTION,
    DIAGNOSIS_CODE,
    DIAGNOSIS_DESCRIPTION,
    BASE_ENCOUNTER_COST,
    LOAD_RUN_ID,
    SOURCE_FILE,
    INGESTED_AT,
    SOURCE_ROW_HASH,
    VALIDATION_STATUS,
    VALIDATION_RULE_IDS,
    VALIDATION_MESSAGES
)
SELECT
    categorized_encounter.RAW_ENCOUNTER_ID,
    categorized_encounter.RAW_START_DATETIME,
    categorized_encounter.RAW_END_DATETIME,
    categorized_encounter.RAW_PATIENT_ID,
    categorized_encounter.RAW_ORGANIZATION_ID,
    categorized_encounter.RAW_PROVIDER_ID,
    categorized_encounter.RAW_ENCOUNTER_CLASS,
    categorized_encounter.RAW_ENCOUNTER_CODE,
    categorized_encounter.RAW_ENCOUNTER_DESCRIPTION,
    categorized_encounter.RAW_DIAGNOSIS_CODE,
    categorized_encounter.RAW_DIAGNOSIS_DESCRIPTION,
    categorized_encounter.RAW_BASE_ENCOUNTER_COST,
    categorized_encounter.LOAD_RUN_ID,
    categorized_encounter.SOURCE_FILE,
    categorized_encounter.INGESTED_AT,
    categorized_encounter.SOURCE_ROW_HASH,
    categorized_encounter.VALIDATION_STATUS,
    categorized_encounter.VALIDATION_RULE_IDS,
    categorized_encounter.VALIDATION_MESSAGES
FROM CLEANSTAR.RAW.CATEGORIZED_ENCOUNTER AS categorized_encounter
WHERE categorized_encounter.LOAD_RUN_ID = %s
  AND categorized_encounter.VALIDATION_STATUS IN ('QUARANTINED', 'DEDUPLICATED');
