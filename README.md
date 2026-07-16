# Smart Retail Data Platform

**A retail ETL pipeline that refuses to load bad data, and tells you exactly what it rejected and why.**

Most ETL demos load a clean CSV into a table and print "success". That's the easy half. The interesting half is what happens when row 3 has no email, row 4 is a duplicate, and row 6 has `Ankit` with the spaces still attached — which is what the sample data in `data/raw/` deliberately contains.

The rule this pipeline is built around:

> **No row disappears quietly.** Every input row either lands in the target table or lands in `data/quarantine/` with a reason attached. Rows in must equal rows loaded plus rows rejected, every run, or the build fails.

## What the last run did

```
| Table       | In | Loaded | Quarantined | Pass rate |
|-------------|---:|-------:|------------:|----------:|
| customers   |  7 |      4 |           3 |       57% |
| products    |  5 |      5 |           0 |      100% |
| orders      |  5 |      5 |           0 |      100% |
| total       | 17 |     14 |           3 |       82% |
```

The three quarantined rows, with reasons:

| customerid | customer_name | email | city | _reject_reason |
|---|---|---|---|---|
| 3 | Bob | | Delhi | `missing_required: email` |
| 4 | Rahul | rahul@gmail.com | Bangalore | `duplicate: customerid` |
| 5 | Priya | priya@gmail.com | | `missing_required: city` |

This table isn't pasted in by hand. It's regenerated on every run and published to the [Actions run summary](../../actions/workflows/pipeline.yml).

## Why the CI badge means something here

Green doesn't mean the tests passed. It means that on the last push, GitHub:

1. Started a **real PostgreSQL 16 container** (not sqlite, not a mock)
2. Ran the pipeline against it end to end
3. Queried the database and **asserted the row counts** — 4 customers, 5 products, 5 orders
4. **Ran the pipeline a second time** and asserted the counts hadn't changed, proving idempotency
5. Uploaded the quarantined rows as a downloadable artifact

If the pipeline loads 0 rows and claims success, the build goes red. That failure mode is not hypothetical — it's the bug this repo started with.

## Architecture

```
data/raw/*.csv
     │
     ▼
 extractor ──── file missing? ──▶ raise ExtractError (loudly)
     │
     ▼
 quality.validate(df, schema)
     │
     ├──▶ clean rows ────▶ loader ────▶ PostgreSQL (upsert on key)
     │
     └──▶ bad rows ──────▶ data/quarantine/*_rejects.csv
                                 │
                                 ▼
                          reports/latest_run.md ──▶ Actions summary
```

Schemas are declarative — a table is a list of `Column(name, dtype, required, unique, min_value)`. Adding a rule is one line, and the reject reason it produces is automatic.

## Run it

```bash
git clone https://github.com/Dhru1999/smart-retail-data-platform
cd smart-retail-data-platform
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # then edit with your Postgres credentials
python -m etl.run_pipeline
```

Tests need no database:

```bash
pytest -q
```

Every test in `tests/` is a regression test for a bug that was genuinely in this repo — a `#` comment line hijacking the CSV header, a `Data/raw` path that only resolved on Windows, `fillna("Unknown")` silently turning an integer column into strings. They're there so those bugs can't come back.

## What I'd do next

- Incremental loads with a watermark column instead of full refresh
- Great Expectations for the validation layer once the rule count outgrows hand-rolled schemas
- dbt for the transform layer, keeping Python for extract and load
- Real volume — 17 rows proves the logic, not the performance

## Stack

Python 3.12 · pandas · SQLAlchemy · PostgreSQL 16 · pytest · GitHub Actions

Licensed MIT.

