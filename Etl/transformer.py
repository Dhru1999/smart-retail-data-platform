# Tranform the data from the source format to the target format
import pandas as pd

# function to clean column names of a DataFrame
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the column names of a DataFrame by removing leading/trailing whitespace,
    converting to lowercase, and replacing spaces with underscores.

    Args:
        df (pd.DataFrame): The input DataFrame with original column names. 
    """
    dfcolumns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    df.columns = dfcolumns
    return df

# function to handle duplicate values in a DataFrame
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame with potential duplicate rows.
    """
    return df.drop_duplicates()

# function to handle missing values in a DataFrame
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in a DataFrame by filling them with appropriate values.

    Args:
        df (pd.DataFrame): The input DataFrame with potential missing values.
    """
    return df.fillna("Unknown")

# function to clean dirty text data in a DataFrame
def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dirty text data in a DataFrame by removing leading/trailing whitespace,
    converting to lowercase, and replacing multiple spaces with a single space.

    Args:
        df (pd.DataFrame): The input DataFrame with dirty text data.
    """
    object_columns = df.select_dtypes(include="object").columns
    for column in object_columns:
        df[column] = (
            df[column].str.strip().str.lower()
        )
    return df

# Main tranformation function
def transform_customer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the customer data by cleaning column names, removing duplicates,
    handling missing values, and cleaning dirty text data.

    Args:
        df (pd.DataFrame): The input DataFrame with customer data.
    """
    df = clean_column_names(df)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = clean_text(df)
    return df

#function to convert price column to float
def convert_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the price column in a DataFrame to float.

    Args:
        df (pd.DataFrame): The input DataFrame with a price column.
    """
    df["price"] = df["price"].astype(float)
    return df