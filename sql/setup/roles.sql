-- Run with SECURITYADMIN, which can create roles and manage grants.
USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS CLEANSTAR_ROLE
    COMMENT = 'Run CleanStar ingestion, validation, and transformation';

-- SYSADMIN inherits this role, not the other way around.
GRANT ROLE CLEANSTAR_ROLE TO ROLE SYSADMIN;

-- Assign the project role to the user running this setup.
-- Execute these statements in the same connection so the variable is available.
SET cleanstar_setup_user = CURRENT_USER();
GRANT ROLE CLEANSTAR_ROLE TO USER IDENTIFIER($cleanstar_setup_user);

-- The infrastructure scripts that follow run as SYSADMIN.
USE ROLE SYSADMIN;
