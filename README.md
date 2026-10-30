# CleanStar

CleanStar is a Python-first recreation of Northstar built for learning Snowflake.

The project uses Python for orchestration and external `.sql` files for
Snowflake roles, warehouses, databases, schemas, stages, grants, ingestion,
validation, transformations, and views.

The full workflow, including the automatic startup reset, has been run against
Snowflake and refreshed in Power BI. The verified demonstration produced 99,209
raw records, 97,880 clean records, and 1,329 quarantined records.

## Demonstration data and reset design

**CleanStar is a portfolio demonstration using a fixed set of synthetic data in
local CSV files. Each run clears the previous table records so the same inputs
can demonstrate ingestion, validation, and transformation from a fresh state.**

Without this reset, repeatedly loading the same demonstration files would cause
previously accepted records to be classified as duplicates and accumulate in
quarantine. Resetting keeps the report focused on one complete demonstration
run. Duplicate records within the source files are still detected and reported.
The reset is an intentional demonstration convenience, not a requirement caused
by CSV files or synthetic data.

**This is not the default design we would use for an ongoing production pipeline.**
A production design would choose its load strategy based on source and business
requirements: typically retain raw history and run audit records, ingest new or
changed data incrementally, and handle retries without creating duplicate
results (idempotence). Updates might use merges, while already-processed inputs
could be skipped. A full refresh can also be appropriate for some datasets, but
would require an explicit replacement and recovery strategy rather than clearing
all raw, clean, and quarantine history before every run.

CleanStar's current database tables retain only the latest attempted run; a
failed reset or load can leave empty or partially populated tables. Saved text
reports remain on disk, but are not a substitute for retained source and audit
history. This tradeoff keeps the portfolio demonstration simple and repeatable.

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

`run_cleanstar.py` directly calls `pipeline.main()`, which first clears all 12
raw, clean, and quarantine tables using the reset SQL and a separate administrative
connection. It then opens the pipeline connection, checks setup, uploads
and validates files, loads raw tables, reconciles counts for the current load ID,
runs the baseline audit, and transforms all four datasets. It closes the cursor
and connection on success or failure. The launcher prints a summary and saves it as
`reports/<load_run_id>.txt`.

The startup reset clears prior records and COPY load metadata, allowing the same
source files to load again. The COPY statement still uses `FORCE = FALSE`.
Snowflake can skip files already loaded within a run. `NO_NEW_ROWS` in the
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

**Every pipeline run automatically removes all existing records from the 12
CleanStar pipeline tables before reading or loading source files.** Run only one
pipeline at a time. Previous database runs are not retained, and a failure does
not restore the previous data. Refresh Power BI after a successful run.

To clear records without running ingestion, use:

```powershell
python reset_cleanstar.py
```

The reset empties all 12 raw, clean, and quarantine tables, including records
from every previous load. It preserves table definitions, grants, staged files,
local CSVs, and saved reports. TRUNCATE clears table load metadata so the same
source files can load again. Both the pipeline startup reset and standalone reset require the administrative
user used for setup, with
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
