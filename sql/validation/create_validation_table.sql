-- Python replaces {column_definitions} with trusted, quoted source columns.
-- The connector supplies the unique temporary table name.
-- No ingestion metadata: this structure must match the CSV fields exactly.
CREATE TEMPORARY TABLE IDENTIFIER(%s) (
    {column_definitions}
);
