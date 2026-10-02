-- Parameters: configured raw table name, then LOAD_RUN_ID.
SELECT COUNT(*) FROM IDENTIFIER(%s) WHERE LOAD_RUN_ID = %s;
