"""
Every test here is a bug that was actually in this repo. They are
regression tests, not decoration.
"""

from pathlib import Path

import pandas as pd
import pytest

from etl.quality import (
    CUSTOMERS,
    ORDERS,
    PRODUCTS,
    REJECT_COL,
    Column,
    Schema,
    normalise_columns,
    validate,
)

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / name, comment="#", skipinitialspace=True)


# --- the header-eating bug --------------------------------------------

def test_leading_comment_line_does_not_become_the_header():
    """
    customers.csv opens with '# Intentional added messy data for practice'.
    Without comment='#', pandas made that the only column and swallowed the
    real headers into the index. It did not raise. It loaded garbage.
    """
    df = read("customers.csv")
    assert "customerid" in normalise_columns(df).columns
    assert df.shape[1] == 4, f"expected 4 columns, got {df.shape[1]}"


def test_raw_read_without_comment_arg_is_broken():
    """Proof the bug was real, so nobody 'simplifies' the fix away."""
    df = pd.read_csv(RAW / "customers.csv")
    assert df.shape[1] == 1  # the bug: one absurd column


# --- path casing ------------------------------------------------------

def test_data_dir_is_lowercase():
    """Code used Path(...)/'Data'/'raw'. Fine on Windows, fails on CI."""
    assert RAW.exists(), f"{RAW} not found"
    assert RAW.parent.name == "data"


# --- row accounting ---------------------------------------------------

def test_no_row_is_silently_dropped():
    for fn, schema in [("customers.csv", CUSTOMERS), ("products.csv", PRODUCTS),
                       ("orders.csv", ORDERS)]:
        r = validate(read(fn), schema)
        assert r.balanced, (
            f"{r.table}: {r.rows_in} in but {r.rows_loaded} loaded "
            f"+ {r.rows_rejected} quarantined"
        )


def test_planted_messy_rows_are_all_caught():
    """The three rows deliberately planted in customers.csv."""
    r = validate(read("customers.csv"), CUSTOMERS)
    assert r.rows_rejected == 3
    reasons = set(r.rejects[REJECT_COL])
    assert "missing_required: email" in reasons   # Bob
    assert "duplicate: customerid" in reasons     # Rahul, twice
    assert "missing_required: city" in reasons    # Priya


def test_clean_rows_survive():
    r = validate(read("customers.csv"), CUSTOMERS)
    assert r.rows_loaded == 4
    assert r.clean["customerid"].is_unique


# --- type coercion ----------------------------------------------------

def test_price_column_casing_does_not_explode():
    """convert_price did df['price'] on a frame with column 'Price' -> KeyError."""
    r = validate(read("products.csv"), PRODUCTS)
    assert r.rows_loaded == 5
    assert str(r.clean["price"].dtype) == "Float64"


def test_bad_numbers_are_quarantined_not_raised():
    df = pd.DataFrame({
        "orderid": [1, 2], "customerid": [1, 1],
        "productid": [1, 1], "quantity": ["two", 3],
    })
    r = validate(df, ORDERS)
    assert r.rows_rejected == 1
    assert r.rejects[REJECT_COL].iloc[0].startswith("bad_int")
    assert r.balanced


def test_missing_column_quarantines_whole_frame_rather_than_guessing():
    df = pd.DataFrame({"orderid": [1], "customerid": [1]})
    r = validate(df, ORDERS)
    assert r.rows_loaded == 0
    assert "schema_mismatch" in r.rejects[REJECT_COL].iloc[0]
    assert r.balanced


def test_negative_quantity_rejected():
    df = pd.DataFrame({
        "orderid": [1], "customerid": [1], "productid": [1], "quantity": [-5],
    })
    r = validate(df, ORDERS)
    assert r.rows_rejected == 1
    assert "below_min" in r.rejects[REJECT_COL].iloc[0]


# --- column normalisation --------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("Customer Name", "customer_name"),
    ("  Email  ", "email"),
    ("Product-ID", "product_id"),
])
def test_column_names_normalise(raw, expected):
    df = pd.DataFrame({raw: [1]})
    assert normalise_columns(df).columns[0] == expected


def test_fillna_unknown_does_not_corrupt_numeric_columns():
    """
    The old handle_missing_values did df.fillna('Unknown') across the whole
    frame, turning numeric columns into object dtype.
    """
    df = pd.DataFrame({
        "orderid": [1, 2], "customerid": [1, None],
        "productid": [1, 1], "quantity": [1, 1],
    })
    r = validate(df, ORDERS)
    assert str(r.clean["customerid"].dtype) == "Int64"
    assert r.rows_rejected == 1
