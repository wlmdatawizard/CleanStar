-- Pre-cleaning summary for one LOAD_RUN_ID; read-only.
-- Duplicate rows exclude ingestion metadata. Missing IDs mean NULL or empty text,
-- matching Northstar; whitespace-only IDs are not counted as missing here.
WITH CURRENT_LOAD AS (
    SELECT *
    FROM CLEANSTAR.RAW.PROVIDER_INFO_RAW
    WHERE LOAD_RUN_ID = %s
)
SELECT
    COUNT(*) AS row_count,
    (SELECT COALESCE(SUM(occurrence - 1), 0) AS duplicate_count
            FROM (
                SELECT COUNT(*) AS occurrence
                FROM CURRENT_LOAD
                GROUP BY PROVIDER_ID, ORGANIZATION_ID, PROVIDER_NAME, SPECIALTY, NPI
                HAVING COUNT(*) > 1) AS duplicate_rows) AS duplicate_rows,
    COUNT(TRIM(PROVIDER_ID)) - COUNT(DISTINCT TRIM(PROVIDER_ID)) AS duplicate_provider_ids,
    COALESCE(SUM(CASE WHEN PROVIDER_ID IS NULL OR PROVIDER_ID = '' THEN 1 ELSE 0 END), 0) AS missing_provider_ids
FROM CURRENT_LOAD;
