import os
from dotenv import load_dotenv


def load_settings():
    load_dotenv()

    return {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "CLEANSTAR_WH"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "CLEANSTAR"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", "RAW"),
    }
