# CleanStar

CleanStar is a Python-first recreation of Northstar built for learning Snowflake.

The project will use Python for orchestration and external `.sql` files for
Snowflake roles, warehouses, databases, schemas, stages, grants, ingestion,
validation, transformations, and views.

The workflow is assembled and tested offline. Live Snowflake integration testing
is still required after a dedicated account is created.

## Run the pipeline

Install `requirements.txt` into your Python environment, fill in the Snowflake
credentials in `.env`, and provision the objects before running the pipeline.
Run setup separately, from the CleanStar directory:

```powershell
python setup_cleanstar.py
```

Use a user that can activate SECURITYADMIN and SYSADMIN. Setup connects without
the project database, warehouse, or schema, then runs roles, warehouse, database,
schemas, file format, stage, all three table scripts, and grants. It grants
CLEANSTAR_ROLE to the user running setup. If ingestion uses a different user,
that user also needs the role granted. Set SNOWFLAKE_ROLE=CLEANSTAR_ROLE for
regular pipeline runs.

Setup uses IF NOT EXISTS: rerunning preserves existing objects and data, but
does not update existing table definitions or settings. A failure stops setup
and leaves earlier completed statements in place; fix the reported problem
before rerunning. Setup is not part of every pipeline run.

From the CleanStar directory:

```powershell
python run_cleanstar.py
```

Source CSVs go in the `data` folder. The four filenames must match
`src/cleanstar/data_config.py`.

## Workflow

`run_cleanstar.py` directly calls `pipeline.main()`, which opens a connection, checks setup, uploads
and validates files, loads raw tables, reconciles counts for the current load ID,
runs the baseline audit, and transforms all four datasets. It closes the cursor
and connection on success or failure. The launcher prints a summary and saves it as
`reports/<load_run_id>.txt`.

Snowflake can skip files already loaded (`FORCE = FALSE`). `NO_NEW_ROWS` in the
report means a nonempty source produced no raw rows for this run; it does not
mean the file was freshly processed. Partial count mismatches stop the workflow.

Preparation and categorization use session-local temporary tables. Clean and
quarantine inserts commit together for each dataset. Raw loads and earlier
completed datasets can remain after a later failure. The load ID is printed at startup and original errors propagate; inspect that
load before retrying. This version has no resume or
automatic retry feature. Connection loss during commit can leave its outcome
uncertain. A successful report contains insert counts, not a post-cleaning audit.

Run one pipeline at a time for now: the shared stage uses fixed filenames, and
historical duplicate checks do not coordinate concurrent writers. Session-local
temporary table names themselves do not conflict across connections.

SQL remains in `.sql` files. Python supplies parameters, controls execution, and
formats results. Timestamps without offsets are interpreted as UTC. Setup checks
verify object access and column names, not all types or file-format properties.

## Reset test data

To start a fresh test, run this separately while no pipeline run is active:

```powershell
python reset_cleanstar.py
python run_cleanstar.py
```

The reset empties all 12 raw, clean, and quarantine tables, including records
from every previous load. It preserves table definitions, grants, staged files,
local CSVs, and saved reports. TRUNCATE clears table load metadata so the same
source files can load again. Use the administrative user used for setup, with
access to SECURITYADMIN and SYSADMIN. Errors stop the script; if a reset fails,
some tables may already be empty. Resolve the error and complete the reset
before starting another pipeline run.

## Offline checks

```powershell
python -B -m unittest discover -s tests -v
```

These tests check sequencing, transaction handling, reports, and cleanup using
simulated cursors. They do not establish that the pipeline works against a live
Snowflake account.
