# Loader module for the ETL pipeline: writes a validated DataFrame to PostgreSQL.
import re

import pandas as pd
from sqlalchemy import inspect, text

from etl.exceptions import LoadError
from etl.logger import logger

_SAFE_TABLE_NAME = re.compile(r"^[a-z_][a-z0-9_]*$")


def load_dataframe(df: pd.DataFrame, table_name: str, engine=None) -> int:
    """
    Replace the contents of a table with the given rows (full refresh).

    The delete and the insert run in one transaction, so a failed load leaves
    the previous data in place, and running the pipeline twice leaves the same
    row counts (idempotent). The table is created on the first run.

    Args:
        df: Clean rows to load.
        table_name: Target table (lowercase letters, digits, underscores).
        engine: SQLAlchemy engine; defaults to the one configured from .env.
    Returns:
        Number of rows loaded.
    """
    if not _SAFE_TABLE_NAME.match(table_name):
        raise LoadError(f"Invalid table name: {table_name!r}")
    if engine is None:
        from etl.db import engine  # imported lazily so unit tests need no database config

    logger.info(f"Loading {len(df)} rows into {table_name}...")
    try:
        with engine.begin() as conn:
            if inspect(conn).has_table(table_name):
                conn.execute(text(f'DELETE FROM "{table_name}"'))
            df.to_sql(name=table_name, con=conn, if_exists="append", index=False)
    except Exception as e:
        logger.error(f"Error loading DataFrame into table '{table_name}': {e}")
        raise LoadError(f"Loading {table_name} failed: {e}") from e

    logger.info(f"Loaded {len(df)} rows into {table_name}")
    return len(df)
