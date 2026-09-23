-- Python fills the source column lists from RAW_LOADS.
-- Connector parameters: table name, run ID, local source filename,
-- ingestion timestamp (ISO 8601), and exact staged filename.
COPY INTO IDENTIFIER(%s) (
    {target_columns},
    LOAD_RUN_ID, SOURCE_FILE, INGESTED_AT
)
FROM (
    SELECT
        {staged_columns},
        %s,
        %s,
        %s::TIMESTAMP_TZ
    FROM @CLEANSTAR.RAW.RAW_STAGE staged_file
)
FILES = (%s)
FILE_FORMAT = (FORMAT_NAME = 'CLEANSTAR.RAW.CSV_FORMAT')
ON_ERROR = ABORT_STATEMENT
FORCE = FALSE
PURGE = FALSE;
