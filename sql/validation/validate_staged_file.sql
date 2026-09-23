-- Connector parameters: temporary table name, then exact staged filename.
-- Validation returns parsing errors without inserting rows.
COPY INTO IDENTIFIER(%s)
FROM @CLEANSTAR.RAW.RAW_STAGE
FILES = (%s)
FILE_FORMAT = (FORMAT_NAME = 'CLEANSTAR.RAW.CSV_FORMAT')
VALIDATION_MODE = 'RETURN_ALL_ERRORS';
