-- Run with SYSADMIN or another role with CREATE WAREHOUSE privileges.
-- IF NOT EXISTS leaves an existing warehouse and its settings unchanged.
CREATE WAREHOUSE IF NOT EXISTS CLEANSTAR_WH
    WAREHOUSE_TYPE = STANDARD
    WAREHOUSE_SIZE = XSMALL
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Compute for CleanStar data loading and processing';
