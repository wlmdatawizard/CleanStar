-- Run after database.sql with a role that can create schemas in CLEANSTAR.
-- IF NOT EXISTS leaves existing schemas and their contents unchanged.
CREATE SCHEMA IF NOT EXISTS CLEANSTAR.RAW
    COMMENT = 'Source data loaded before validation and transformation';

CREATE SCHEMA IF NOT EXISTS CLEANSTAR.CLEAN
    COMMENT = 'Validated and transformed data';

CREATE SCHEMA IF NOT EXISTS CLEANSTAR.QUARANTINE
    COMMENT = 'Data held for review after failing validation';
