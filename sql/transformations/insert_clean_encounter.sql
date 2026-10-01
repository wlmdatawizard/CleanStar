-- Insert prepared, typed values from categorized_encounter.sql.
-- Parameter: LOAD_RUN_ID. Use the same pipeline session.
-- Run both destination inserts once per load, together in a transaction.
-- These statements append rows; rerunning them would insert duplicates.
INSERT INTO CLEANSTAR.CLEAN.ENCOUNTER_INFO_CLEAN (
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
    categorized_encounter.ENCOUNTER_ID,
    categorized_encounter.START_DATETIME,
    categorized_encounter.END_DATETIME,
    categorized_encounter.PATIENT_ID,
    categorized_encounter.ORGANIZATION_ID,
    categorized_encounter.PROVIDER_ID,
    categorized_encounter.ENCOUNTER_CLASS,
    categorized_encounter.ENCOUNTER_CODE,
    categorized_encounter.ENCOUNTER_DESCRIPTION,
    categorized_encounter.DIAGNOSIS_CODE,
    categorized_encounter.DIAGNOSIS_DESCRIPTION,
    categorized_encounter.BASE_ENCOUNTER_COST,
    categorized_encounter.LOAD_RUN_ID,
    categorized_encounter.SOURCE_FILE,
    categorized_encounter.INGESTED_AT,
    categorized_encounter.SOURCE_ROW_HASH,
    categorized_encounter.VALIDATION_STATUS,
    categorized_encounter.VALIDATION_RULE_IDS,
    categorized_encounter.VALIDATION_MESSAGES
FROM CLEANSTAR.RAW.CATEGORIZED_ENCOUNTER AS categorized_encounter
WHERE categorized_encounter.LOAD_RUN_ID = %s
  AND categorized_encounter.VALIDATION_STATUS IN ('CLEAN', 'WARNING');
