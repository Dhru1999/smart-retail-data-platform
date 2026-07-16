from etl.loader import load_dataframe
import pandas as pd

# Test cases for the data loader

def test_load_dataframe():
    # Create a sample DataFrame for testing
    df = pd.DataFrame({
        "customer_name": ["John Doe", "Jane Smith"],
        "email": ["john.doe@example.com", "jane.smith@example.com"]
    })
    result = load_dataframe(df, "test_table")
    assert result is None  # The function does not return anything, so we check for None
    