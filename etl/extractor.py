# Reads data from CSV files in the raw data folder and returns it as Pandas DataFrames.
from pathlib import Path
from etl.logger import logger
import pandas as pd
from etl.exceptions import ExtractError

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

def extract_csv(filename: str) -> pd.DataFrame:
    """
    Read a CSV file from the raw data folder
    ARGS: filename : Name of the CSV file
    Returns: Pandas DataFrame.
    """
    file_path = DATA_DIR / filename
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError as e:
        logger.exception(f"File {filename} not found in {DATA_DIR}")
        raise ExtractError(f"File {filename} not found in {DATA_DIR}") from e
    except Exception as e:
        logger.exception(f"Failed to read {filename} from {DATA_DIR}")
        raise ExtractError(f"Failed to read {filename} from {DATA_DIR}") from e

def extract_customers():
    logger.info("Extracting customer data...")
    return extract_csv("customers.csv")

def extract_products():
    logger.info("Extracting product data...")
    return extract_csv("products.csv")

def extract_orders():
    logger.info("Extracting order data...")
    return extract_csv("orders.csv")

