-- Run after file_format.sql with CREATE STAGE privileges in CLEANSTAR.RAW
-- and access to CLEANSTAR.RAW.CSV_FORMAT.
-- IF NOT EXISTS preserves an existing stage, its settings, and uploaded files.
-- Creating the stage does not upload files; that is a separate PUT operation.


CREATE STAGE IF NOT EXISTS CLEANSTAR.RAW.RAW_STAGE
    FILE_FORMAT = (FORMAT_NAME = 'CLEANSTAR.RAW.CSV_FORMAT')
    COMMENT = 'Internal storage for CleanStar source files before raw table loading';
