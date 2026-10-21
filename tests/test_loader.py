import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from etl.exceptions import LoadError
from etl.loader import load_dataframe


@pytest.fixture
def engine():
    # SQLite stands in for PostgreSQL here; CI also runs the pipeline against a real Postgres.
    return create_engine("sqlite://")


def count(engine, table):
    with engine.connect() as c:
        return c.execute(text(f"SELECT count(*) FROM {table}")).scalar()


def test_load_creates_table_and_returns_row_count(engine):
    df = pd.DataFrame({"customer_name": ["John Doe", "Jane Smith"]})
    assert load_dataframe(df, "customers", engine=engine) == 2
    assert count(engine, "customers") == 2


def test_loading_twice_does_not_duplicate_rows(engine):
    df = pd.DataFrame({"id": [1, 2, 3]})
    load_dataframe(df, "orders", engine=engine)
    load_dataframe(df, "orders", engine=engine)
    assert count(engine, "orders") == 3


def test_reload_replaces_previous_contents(engine):
    load_dataframe(pd.DataFrame({"id": [1, 2, 3]}), "orders", engine=engine)
    load_dataframe(pd.DataFrame({"id": [9]}), "orders", engine=engine)
    assert count(engine, "orders") == 1


@pytest.mark.parametrize("bad", ["Orders", "orders; DROP TABLE x", "", "1orders"])
def test_rejects_unsafe_table_names(engine, bad):
    with pytest.raises(LoadError):
        load_dataframe(pd.DataFrame({"id": [1]}), bad, engine=engine)
