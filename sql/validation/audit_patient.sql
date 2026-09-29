-- Pre-cleaning summary for one LOAD_RUN_ID; read-only.
-- Duplicate rows exclude ingestion metadata. Missing IDs mean NULL or empty text,
-- matching Northstar; whitespace-only IDs are not counted as missing here.
WITH CURRENT_LOAD AS (
    SELECT *
    FROM CLEANSTAR.RAW.PATIENT_INFO_RAW
    WHERE LOAD_RUN_ID = %s
)
SELECT
    COUNT(*) AS row_count,
    (SELECT COALESCE(SUM(occurrence - 1), 0) AS duplicate_count
            FROM (
                SELECT COUNT(*) AS occurrence
                FROM CURRENT_LOAD
                GROUP BY PATIENT_ID, BIRTHDATE, FIRST_NAME, MIDDLE_INITIAL, LAST_NAME, 
                        SUFFIX, GENDER, ADDRESS, CITY, STATE, ZIP, PHONE, PAYER_ID, 
                        INSURANCE_PLAN_NAME, MEMBER_ID, GROUP_NUMBER, RELATIONSHIP_TO_INSURED, 
                        COVERAGE_START_DATE, COVERAGE_END_DATE, COVERAGE_STATUS
                HAVING COUNT(*) > 1) AS duplicate_rows) AS duplicate_rows,
    COUNT(TRIM(PATIENT_ID)) - COUNT(DISTINCT TRIM(PATIENT_ID)) AS duplicate_patient_ids,
    COALESCE(SUM(CASE WHEN PATIENT_ID IS NULL OR PATIENT_ID = '' THEN 1 ELSE 0 END), 0) AS missing_patient_ids
FROM CURRENT_LOAD;
