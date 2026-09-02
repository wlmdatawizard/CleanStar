import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    account: str | None
    user: str | None
    password: str | None
    role: str | None
    warehouse: str
    database: str
    schema: str


def load_settings():
    load_dotenv()

    return Settings(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "CLEANSTAR_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "CLEANSTAR"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "RAW"),
    )
