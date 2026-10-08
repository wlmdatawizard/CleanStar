PUT %s
    @CLEANSTAR.RAW.RAW_STAGE
    AUTO_COMPRESS = TRUE
    OVERWRITE = TRUE;

-- Keep PUT first so the Python connector recognizes this as a file transfer.
-- Python supplies one absolute local file URI through the connector parameter.
-- Compression preserves CSV contents and produces the .csv.gz name in RAW_LOADS.
-- As in Northstar, a changed file may replace the same filename on the stage.
