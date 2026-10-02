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
The setup scripts are run separately: roles, warehouse, database, schemas, file
format, stage, all three table scripts, then grants. Use the roles specified in
the setup scripts. The pipeline does not provision infrastructure.

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

## Offline checks

```powershell
python -B -m unittest discover -s tests -v
```

These tests check sequencing, transaction handling, reports, and cleanup using
simulated cursors. They do not establish that the pipeline works against a live
Snowflake account.
