-- Pre-cleaning summary for one LOAD_RUN_ID; read-only.
-- Duplicate rows exclude ingestion metadata. Missing IDs mean NULL or empty text,
-- matching Northstar; whitespace-only IDs are not counted as missing here.
WITH CURRENT_LOAD AS (
    SELECT *
    FROM CLEANSTAR.RAW.ENCOUNTER_INFO_RAW
    WHERE LOAD_RUN_ID = %s
)
SELECT
    COUNT(*) AS row_count,
    (SELECT COALESCE(SUM(occurrence - 1), 0) AS duplicate_count
    FROM (
        SELECT COUNT(*) AS occurrence
        FROM CURRENT_LOAD
        GROUP BY ENCOUNTER_ID, START_DATETIME, END_DATETIME, PATIENT_ID, ORGANIZATION_ID, PROVIDER_ID, 
                ENCOUNTER_CLASS, ENCOUNTER_CODE, ENCOUNTER_DESCRIPTION, DIAGNOSIS_CODE, DIAGNOSIS_DESCRIPTION, BASE_ENCOUNTER_COST
        HAVING COUNT(*) > 1) AS duplicate_rows) AS duplicate_rows,
    COUNT(TRIM(ENCOUNTER_ID)) - COUNT(DISTINCT TRIM(ENCOUNTER_ID)) AS duplicate_encounter_ids,
    COALESCE(SUM(CASE WHEN PATIENT_ID IS NULL OR PATIENT_ID = '' THEN 1 ELSE 0 END), 0) AS missing_patient_ids,
    COALESCE(SUM(CASE WHEN PROVIDER_ID IS NULL OR PROVIDER_ID = '' THEN 1 ELSE 0 END), 0) AS missing_provider_ids,
    COALESCE(SUM(CASE WHEN ENCOUNTER_ID IS NULL OR ENCOUNTER_ID = '' THEN 1 ELSE 0 END), 0) AS missing_encounter_ids
FROM CURRENT_LOAD;
