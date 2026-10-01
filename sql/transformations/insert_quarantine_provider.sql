-- Insert original source values, including duplicate records from categorized_provider.sql.
-- Parameter: LOAD_RUN_ID. Use the same pipeline session.
-- Run both destination inserts once per load, together in a transaction.
-- These statements append rows; rerunning them would insert duplicates.
INSERT INTO CLEANSTAR.QUARANTINE.PROVIDER_INFO_QUARANTINE (
    PROVIDER_ID,
    ORGANIZATION_ID,
    PROVIDER_NAME,
    SPECIALTY,
    NPI,
    LOAD_RUN_ID,
    SOURCE_FILE,
    INGESTED_AT,
    SOURCE_ROW_HASH,
    VALIDATION_STATUS,
    VALIDATION_RULE_IDS,
    VALIDATION_MESSAGES
)
SELECT
    categorized_provider.RAW_PROVIDER_ID,
    categorized_provider.RAW_ORGANIZATION_ID,
    categorized_provider.RAW_PROVIDER_NAME,
    categorized_provider.RAW_SPECIALTY,
    categorized_provider.RAW_NPI,
    categorized_provider.LOAD_RUN_ID,
    categorized_provider.SOURCE_FILE,
    categorized_provider.INGESTED_AT,
    categorized_provider.SOURCE_ROW_HASH,
    categorized_provider.VALIDATION_STATUS,
    categorized_provider.VALIDATION_RULE_IDS,
    categorized_provider.VALIDATION_MESSAGES
FROM CLEANSTAR.RAW.CATEGORIZED_PROVIDER AS categorized_provider
WHERE categorized_provider.LOAD_RUN_ID = %s
  AND categorized_provider.VALIDATION_STATUS IN ('QUARANTINED', 'DEDUPLICATED');
