# Reads data from CSV files in the raw data folder and returns it as Pandas DataFrames.
from pathlib import Path

import pandas as pd

from etl.exceptions import ExtractError
from etl.logger import logger

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def extract_csv(filename: str) -> pd.DataFrame:
    """
    Read a CSV file from the raw data folder.

    comment="#" skips note lines such as the one at the top of customers.csv
    (without it pandas used that line as the header and loaded one garbage
    column). skipinitialspace=True drops the blanks after delimiters.

    Args:
        filename: Name of the CSV file inside data/raw.
    Returns:
        The file as a DataFrame, all values as read (validation happens later).
    """
    file_path = DATA_DIR / filename
    try:
        return pd.read_csv(file_path, comment="#", skipinitialspace=True)
    except FileNotFoundError as e:
        logger.exception(f"File {filename} not found in {DATA_DIR}")
        raise ExtractError(f"File {filename} not found in {DATA_DIR}") from e


def extract_customers() -> pd.DataFrame:
    logger.info("Extracting customer data...")
    return extract_csv("customers.csv")


def extract_products() -> pd.DataFrame:
    logger.info("Extracting product data...")
    return extract_csv("products.csv")


def extract_orders() -> pd.DataFrame:
    logger.info("Extracting order data...")
    return extract_csv("orders.csv")
