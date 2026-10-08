-- Run with SECURITYADMIN, which can create roles and manage grants.
USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS CLEANSTAR_ROLE
    COMMENT = 'Run CleanStar ingestion, validation, and transformation';

-- SYSADMIN inherits this role, not the other way around.
GRANT ROLE CLEANSTAR_ROLE TO ROLE SYSADMIN;

-- grants.sql assigns the role to the setup user after compute is available.

-- The infrastructure scripts that follow run as SYSADMIN.
USE ROLE SYSADMIN;
