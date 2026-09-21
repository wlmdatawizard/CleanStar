-- Run with SYSADMIN or another role with CREATE DATABASE privileges.
-- Run this script before schemas.sql.
-- IF NOT EXISTS leaves an existing database unchanged.
CREATE DATABASE IF NOT EXISTS CLEANSTAR
    COMMENT = 'Database for CleanStar data loading and processing';
