-- Categorize prepared billing claims inside Snowflake; no data returned to Python.
-- Parameters: unique categorized claims temporary table name, prepared temporary table name,
-- then LOAD_RUN_ID. Use the same session as prepare_claims.sql.
-- Raw fingerprints detect exact source duplicates; normalized IDs detect conflicts.
-- Quarantine takes precedence over deduplication. Claims have no warning-only rules.
-- Missing optional values are allowed; supplied values that fail conversion are not.
-- CLM-007 checks the original amount so rounding cannot hide a small negative value.
CREATE TEMPORARY TABLE IDENTIFIER(%s) AS
WITH CURRENT_LOAD AS (
    SELECT * FROM IDENTIFIER(%s)
    WHERE LOAD_RUN_ID = %s
),
RANKED_ROWS AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY SOURCE_ROW_HASH
            ORDER BY INGESTED_AT, SOURCE_FILE, CLAIM_ID
        ) AS DUPLICATE_NUMBER
    FROM CURRENT_LOAD
),
CURRENT_CONFLICTS AS (
    SELECT CLAIM_ID
    FROM CURRENT_LOAD
    WHERE CLAIM_ID IS NOT NULL
    GROUP BY CLAIM_ID
    HAVING COUNT(DISTINCT SOURCE_ROW_HASH) > 1
),
HISTORICAL_DUPLICATES AS (
    SELECT DISTINCT source.SOURCE_ROW_HASH
    FROM CURRENT_LOAD AS source
    WHERE EXISTS (
        SELECT 1 FROM CLEANSTAR.CLEAN.BILLING_CLAIMS_CLEAN AS clean
        WHERE clean.SOURCE_ROW_HASH = source.SOURCE_ROW_HASH
          AND clean.LOAD_RUN_ID <> source.LOAD_RUN_ID
    )
),
HISTORICAL_CONFLICTS AS (
    SELECT DISTINCT source.CLAIM_ID, source.SOURCE_ROW_HASH
    FROM CURRENT_LOAD AS source
    WHERE EXISTS (
        SELECT 1 FROM CLEANSTAR.CLEAN.BILLING_CLAIMS_CLEAN AS clean
        WHERE clean.CLAIM_ID = source.CLAIM_ID
          AND clean.SOURCE_ROW_HASH <> source.SOURCE_ROW_HASH
          AND clean.LOAD_RUN_ID <> source.LOAD_RUN_ID
    )
),
HISTORY_FLAGS AS (
    SELECT source.*,
        (conflict.CLAIM_ID IS NOT NULL) AS CURRENT_CONFLICT,
        (duplicate.SOURCE_ROW_HASH IS NOT NULL) AS HISTORICAL_DUPLICATE,
        (history.CLAIM_ID IS NOT NULL) AS HISTORICAL_CONFLICT
    FROM RANKED_ROWS AS source
    LEFT JOIN CURRENT_CONFLICTS AS conflict ON source.CLAIM_ID = conflict.CLAIM_ID
    LEFT JOIN HISTORICAL_DUPLICATES AS duplicate
        ON source.SOURCE_ROW_HASH = duplicate.SOURCE_ROW_HASH
    LEFT JOIN HISTORICAL_CONFLICTS AS history
        ON source.CLAIM_ID = history.CLAIM_ID
       AND source.SOURCE_ROW_HASH = history.SOURCE_ROW_HASH
),
RULE_FLAGS AS (
    SELECT *,
        IFF(DUPLICATE_NUMBER > 1, TRUE, FALSE) AS RULE_CLM_001,
        IFF(CURRENT_CONFLICT, TRUE, FALSE) AS RULE_CLM_002,
        IFF(CLAIM_ID IS NULL, TRUE, FALSE) AS RULE_CLM_003,
        IFF(PATIENT_ID IS NULL, TRUE, FALSE) AS RULE_CLM_004,
        IFF(ENCOUNTER_ID IS NULL, TRUE, FALSE) AS RULE_CLM_005,
        IFF(CLAIM_AMOUNT_CONVERSION_FAILED, TRUE, FALSE) AS RULE_CLM_006,
        IFF(TRY_TO_DOUBLE(NULLIF(TRIM(RAW_CLAIM_AMOUNT), '')) < 0, TRUE, FALSE) AS RULE_CLM_007,
        IFF(HISTORICAL_DUPLICATE, TRUE, FALSE) AS RULE_CLM_008,
        IFF(HISTORICAL_CONFLICT, TRUE, FALSE) AS RULE_CLM_009,
        IFF(PATIENT_BIRTHDATE_CONVERSION_FAILED, TRUE, FALSE) AS RULE_CLM_010,
        IFF(SERVICE_START_DATETIME_CONVERSION_FAILED, TRUE, FALSE) AS RULE_CLM_011,
        IFF(SERVICE_END_DATETIME_CONVERSION_FAILED, TRUE, FALSE) AS RULE_CLM_012,
        IFF(CLAIM_CREATED_DATETIME_CONVERSION_FAILED, TRUE, FALSE) AS RULE_CLM_013,
        IFF(VALIDATION_ERROR_COUNT_CONVERSION_FAILED, TRUE, FALSE) AS RULE_CLM_014
    FROM HISTORY_FLAGS
)
SELECT *,
    CASE
        WHEN RULE_CLM_002
             OR RULE_CLM_003
             OR RULE_CLM_004
             OR RULE_CLM_005
             OR RULE_CLM_006
             OR RULE_CLM_007
             OR RULE_CLM_009
             OR RULE_CLM_010
             OR RULE_CLM_011
             OR RULE_CLM_012
             OR RULE_CLM_013
             OR RULE_CLM_014
            THEN 'QUARANTINED'
        WHEN RULE_CLM_001 OR RULE_CLM_008 THEN 'DEDUPLICATED'
        ELSE 'CLEAN'
    END AS VALIDATION_STATUS,
    NULLIF(ARRAY_TO_STRING(ARRAY_CONSTRUCT_COMPACT(
            IFF(RULE_CLM_001, 'CLM-001', NULL),
            IFF(RULE_CLM_002, 'CLM-002', NULL),
            IFF(RULE_CLM_003, 'CLM-003', NULL),
            IFF(RULE_CLM_004, 'CLM-004', NULL),
            IFF(RULE_CLM_005, 'CLM-005', NULL),
            IFF(RULE_CLM_006, 'CLM-006', NULL),
            IFF(RULE_CLM_007, 'CLM-007', NULL),
            IFF(RULE_CLM_008, 'CLM-008', NULL),
            IFF(RULE_CLM_009, 'CLM-009', NULL),
            IFF(RULE_CLM_010, 'CLM-010', NULL),
            IFF(RULE_CLM_011, 'CLM-011', NULL),
            IFF(RULE_CLM_012, 'CLM-012', NULL),
            IFF(RULE_CLM_013, 'CLM-013', NULL),
            IFF(RULE_CLM_014, 'CLM-014', NULL)
    ), ', '), '') AS VALIDATION_RULE_IDS,
    NULLIF(ARRAY_TO_STRING(ARRAY_CONSTRUCT_COMPACT(
            IFF(RULE_CLM_001, 'Exact duplicate row within current load', NULL),
            IFF(RULE_CLM_002, 'ID is reused by conflicting records within current load', NULL),
            IFF(RULE_CLM_003, 'Claim ID is required', NULL),
            IFF(RULE_CLM_004, 'Patient ID is required', NULL),
            IFF(RULE_CLM_005, 'Encounter ID is required', NULL),
            IFF(RULE_CLM_006, 'Claim amount must be numeric', NULL),
            IFF(RULE_CLM_007, 'Claim amount must not be negative', NULL),
            IFF(RULE_CLM_008, 'Exact record already exists in CLEAN from an earlier load', NULL),
            IFF(RULE_CLM_009, 'ID conflicts with a CLEAN record from an earlier load', NULL),
            IFF(RULE_CLM_010, 'Patient birthdate must be a valid date', NULL),
            IFF(RULE_CLM_011, 'Service start must be a valid timestamp', NULL),
            IFF(RULE_CLM_012, 'Service end must be a valid timestamp', NULL),
            IFF(RULE_CLM_013, 'Claim created time must be a valid timestamp', NULL),
            IFF(RULE_CLM_014, 'Validation error count must be a representable integer', NULL)
    ), '; '), '') AS VALIDATION_MESSAGES
FROM RULE_FLAGS;
