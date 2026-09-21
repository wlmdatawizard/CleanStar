-- Run after schemas.sql with CREATE FILE FORMAT privileges in CLEANSTAR.RAW.
-- Load source columns into VARCHAR columns to preserve their text values.
-- IF NOT EXISTS leaves an existing file format unchanged.
CREATE FILE FORMAT IF NOT EXISTS CLEANSTAR.RAW.CSV_FORMAT
    TYPE = CSV
    COMPRESSION = AUTO
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    ESCAPE = NONE
    ESCAPE_UNENCLOSED_FIELD = NONE
    TRIM_SPACE = FALSE
    EMPTY_FIELD_AS_NULL = FALSE
    NULL_IF = ()
    REPLACE_INVALID_CHARACTERS = FALSE
    ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE
    COMMENT = 'Parse source CSV files without trimming or converting values to NULL';
