from pathlib import Path
import pandas as pd
from logger import log

DATA_DTR = Path(__file__).resolve().parent.parent / "Data" / "raw"
# Extractor function for ETL process
#def extract():
    # Simulate exracting new retail data
    # Extracted_data = ["Customers..", "Products...", "Orders..."]
    # for data in Extracted_data:
    #     print(f"Extracting {data}")
def extract_csv(filename: str) -> pd.DataFrame:
    """
    Read a CSV file from the raw data folder
    ARGS: filename : Name of the CSV file
    Returns: Pandas DataFrame.

    """
    file_path = DATA_DTR/filename

    """
    Check validation for file existence
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File{filename} not found in {DATA_DTR}")
        
    return pd.read_csv(file_path)

def extract_customers():
    log("Extracting customer data...")
    return extract_csv("customers.csv")

def extract_products():
    log("Extracting product data...")
    return extract_csv("products.csv")

def extract_orders():
    log("Extracting order data...")
    return extract_csv("orders.csv")

