"""Open Snowflake connections using CleanStar's settings."""

from time import sleep

import snowflake.connector
from snowflake.connector.errors import Error, DatabaseError, OperationalError
from snowflake.connector.errorcode import (
    ER_CONNECTION_TIMEOUT,
    ER_FAILED_TO_CONNECT_TO_DB,
    ER_RETRYABLE_CODE,
)
from cleanstar.config import load_settings


MAX_CONNECTION_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5


def get_snowflake_connection(setup=False):
    """Retry temporary connection failures; the caller closes the connection.

    The connector may also retry internally during each connect call. These
    limits count our calls, not individual network requests. Authentication and
    configuration errors are not retried. Unknown operational errors propagate.
    """
    # Setup must connect before the project role, warehouse, or database exists.
    settings = load_settings()
    missing = ["SNOWFLAKE_" + name.upper() for name in ("account", "user", "password")
               if not settings.get(name) or not settings[name].strip()]
    if missing:
        raise ValueError("Missing connection settings: " + ", ".join(missing)
                         + ". Check your .env file.")
    connection_settings = {
        "user": settings["user"],
        "password": settings["password"],
        "account": settings["account"],
        "login_timeout": 30,
    }
    if setup:
        connection_settings["role"] = "SECURITYADMIN"
    else:
        connection_settings.update(
            warehouse=settings["warehouse"],
            database=settings["database"],
            schema=settings["schema"],
            role=settings["role"],
        )
    retryable_codes = (ER_CONNECTION_TIMEOUT, ER_FAILED_TO_CONNECT_TO_DB, ER_RETRYABLE_CODE)

    for attempt in range(1, MAX_CONNECTION_ATTEMPTS + 1):
        try:
            return snowflake.connector.connect(**connection_settings)
        except OperationalError as error:
            # Some login/role failures also use OperationalError; do not retry them.
            message = connection_error_message(error)
            if message is not None or error.errno not in retryable_codes:
                print(message or "Snowflake could not open the connection. See the original error below.")
                raise
            if attempt == MAX_CONNECTION_ATTEMPTS:
                print(f"Unable to connect after {attempt} attempts. Check the account "
                      "identifier, network access, and Snowflake availability before trying again.")
                raise
            print(
                f"Connection attempt {attempt} failed (code {error.errno}). "
                f"Check the account identifier and network access. "
                f"Retrying in {RETRY_DELAY_SECONDS} seconds..."
            )
            sleep(RETRY_DELAY_SECONDS)

        except DatabaseError as error:
            print(connection_error_message(error)
                  or "Snowflake rejected the connection. See the original database error below.")
            raise

        except Error as error:
            print(connection_error_message(error)
                  or "Snowflake could not open the connection. See the original error below.")
            raise


def connection_error_message(error):
    """Return guidance for a known login error, or None if its cause is unclear."""
    message = str(error).lower()
    if error.errno == 390100:
        return ("Snowflake rejected the login. Check your username, password, "
                "account, and authentication settings.")
    # Documented Duo MFA codes; 390128 is success and is intentionally excluded.
    if error.errno in (390120, 390121, 390122, 390123, 390124,
                       390125, 390126, 390127, 390129, 390132):
        return ("Snowflake MFA authentication did not complete. Check your "
                "MFA enrollment, approval, or passcode; see the original error.")
    if "role" in message and ("not assigned" in message or "not granted" in message):
        return ("The requested role is unavailable to this user. Check "
                "SNOWFLAKE_ROLE and the user's role grants.")
    if error.errno == 251009 or (
        error.errno == ER_FAILED_TO_CONNECT_TO_DB and not isinstance(error, OperationalError)
    ):
        return ("Unable to reach the Snowflake account. Check the account "
                "identifier, network access, and the original error.")
    return None
