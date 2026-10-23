"""End-to-end run of the pipeline on the sample data in data/raw (SQLite engine)."""
import pytest
from sqlalchemy import create_engine, text

from etl import run_pipeline


@pytest.fixture
def isolated_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(run_pipeline, "QUARANTINE_DIR", tmp_path / "quarantine")
    monkeypatch.setattr(run_pipeline, "REPORT_PATH", tmp_path / "reports" / "latest_run.md")
    return tmp_path


def counts(engine):
    with engine.connect() as c:
        return {t: c.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                for t in ("customers", "products", "orders")}


def test_every_row_is_loaded_or_quarantined(isolated_outputs):
    engine = create_engine("sqlite://")
    results = run_pipeline.main(engine=engine)

    assert all(r.balanced for r in results)
    assert counts(engine) == {"customers": 4, "products": 5, "orders": 5}

    rejects = (isolated_outputs / "quarantine" / "customers_rejects.csv").read_text()
    assert "missing_required: email" in rejects
    assert "missing_required: city" in rejects
    assert "duplicate: customerid" in rejects

    report = (isolated_outputs / "reports" / "latest_run.md").read_text()
    assert "| **total** | **17** | **14** | **3** | **82%** |" in report


def test_second_run_is_idempotent(isolated_outputs):
    engine = create_engine("sqlite://")
    run_pipeline.main(engine=engine)
    run_pipeline.main(engine=engine)
    assert counts(engine) == {"customers": 4, "products": 5, "orders": 5}


def test_whitespace_is_trimmed_before_loading(isolated_outputs):
    engine = create_engine("sqlite://")
    run_pipeline.main(engine=engine)
    with engine.connect() as c:
        name, city = c.execute(text("SELECT customer_name, city FROM customers WHERE customerid = 6")).one()
    assert (name, city) == ("Ankit", "Mumbai")
