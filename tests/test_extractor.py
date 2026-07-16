from etl.extractor import extract_csv, DATA_DIR
from etl.exceptions import ExtractError
import pandas as pd
import pytest

# Test cases for the data extractor
def test_extract_CSV():
    # Create a sample CSV file inside the raw data folder extract_csv reads from
    test_csv_name = "test_data.csv"
    test_csv_path = DATA_DIR / test_csv_name
    test_csv_path.parent.mkdir(parents=True, exist_ok=True)
    test_data = pd.DataFrame({
        "customer_name": ["John Doe", "Jane Smith"],
        "email": ["john.doe@example.com", "jane.smith@example.com"]
    })
    test_data.to_csv(test_csv_path, index=False)
    try:
        result = extract_csv(test_csv_name)
        assert len(result) == 2
    finally:
        test_csv_path.unlink()

def test_extract_csv_missing_file_raises():
    with pytest.raises(ExtractError):
        extract_csv("does_not_exist.csv")