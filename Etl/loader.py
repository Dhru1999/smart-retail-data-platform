import pandas as pd
from db import engine
from logger import log

# function to load a DataFrame into a database table
def load_dataframe(df: pd.DataFrame,table_name: str):
    print("Loading",table_name,"table...")
    """
    Load a DataFrame into a database table.

    Args:
        df (pd.DataFrame): The DataFrame to be loaded into the database.
        table_name (str): The name of the target database table.
    """
    try:
        df.to_sql(
            name = table_name,
            con = engine,
            if_exists = "append",
            index = False
         )
        print("Loaded",table_name,"with total rows:", len(df),"successfully.")
    except Exception as e:
        log(f"Error loading DataFrame into table '{table_name}': {e}")
        raise