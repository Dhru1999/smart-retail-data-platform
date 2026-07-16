# Test cases for the data transformer

from etl.transformer import (
    clean_column_names,
    remove_duplicates,
    handle_missing_values,
    clean_text
)
import pandas as pd

# Test the clean_column_names function
def test_clean_column_names():
    # Create a sample DataFrame with messy column names
    
    df = pd.DataFrame({
        "customer_name": ["John Doe", "Jane Smith"],
        "email": ["john.doe@example.com", "jane.smith@example.com"],
        "Address": ["123 Main St", "456 Elm St"]
    })
    result = clean_column_names(df)
    assert "customer_name" in result.columns

def test_clean_text():
    # Create a sample DataFrame with messy column names
    df = pd.DataFrame({
        "email": ["JOHN@GMAIL.COM"]
    })
    result = clean_text(df)
    assert result["email"][0] == "john@gmail.com"

def test_remove_duplicates():
    # Create a sample DataFrame with duplicate rows
    df = pd.DataFrame({
        "customer_name": ["John Doe", "Jane Smith", "John Doe"],
        "email": ["john.doe@example.com", "jane.smith@example.com", "john.doe@example.com"]
    })
    result = remove_duplicates(df)
    assert len(result) == 2 
    assert result.duplicated().sum() == 0

def test_handle_missing_values():
    # Create a sample DataFrame with missing values
    df = pd.DataFrame({
        "customer_name": ["John Doe", None],
        "email": ["john.doe@example.com", "jane.smith@example.com"]
    })
    result = handle_missing_values(df)
    assert result["customer_name"][1] == "Unknown"