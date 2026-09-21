"""Open Snowflake connections using CleanStar's settings."""

import snowflake.connector
from cleanstar.config import load_settings


def get_snowflake_connection():
    """Open a connection; the caller is responsible for closing it."""
    settings = load_settings()

    return snowflake.connector.connect(
        user=settings["user"],
        password=settings["password"],
        account=settings["account"],
        warehouse=settings["warehouse"],
        database=settings["database"],
        schema=settings["schema"],
        role=settings["role"],
    )
