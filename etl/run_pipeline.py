"""
Runs the ETL pipeline: extract -> validate -> quarantine rejects -> load -> report.

Every input row ends up either in its PostgreSQL table or in
data/quarantine/<table>_rejects.csv with a reason. The run fails if those two
numbers do not add up to the number of rows read.
"""
import sys
from pathlib import Path

from etl import quality
from etl.extractor import extract_customers, extract_orders, extract_products
from etl.loader import load_dataframe
from etl.logger import logger

ROOT = Path(__file__).resolve().parent.parent
QUARANTINE_DIR = ROOT / "data" / "quarantine"
REPORT_PATH = ROOT / "reports" / "latest_run.md"

STEPS = [
    (extract_customers, quality.CUSTOMERS),
    (extract_products, quality.PRODUCTS),
    (extract_orders, quality.ORDERS),
]


def main(engine=None) -> list[quality.Result]:
    logger.info("Starting ETL pipeline...")
    results: list[quality.Result] = []
    try:
        for extract, schema in STEPS:
            result = quality.validate(extract(), schema)
            results.append(result)

            stale = QUARANTINE_DIR / f"{schema.table}_rejects.csv"
            if result.rows_rejected == 0 and stale.exists():
                stale.unlink()  # don't leave rejects from an earlier run lying around
            quality.quarantine(result, QUARANTINE_DIR)

            load_dataframe(result.clean, schema.table, engine=engine)
            print(f"{schema.table:10} in={result.rows_in:3} loaded={result.rows_loaded:3} "
                  f"quarantined={result.rows_rejected:3}")
    except Exception:
        logger.exception("ETL pipeline failed")
        raise

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(quality.report(results) + "\n", encoding="utf-8")

    unbalanced = [r.table for r in results if not r.balanced]
    if unbalanced:
        raise RuntimeError(f"Row accounting failed for: {', '.join(unbalanced)}")

    logger.info("ETL pipeline completed.")
    return results


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # non-zero exit so CI fails loudly
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        sys.exit(1)
