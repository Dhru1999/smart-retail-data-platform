"""
Schema validation with quarantine.

The rule: no row disappears quietly. A row either lands in the target table
or lands in data/quarantine/ with a reason attached. The pipeline's job is
not to load data, it is to account for every row it was given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

REJECT_COL = "_reject_reason"


@dataclass(frozen=True)
class Column:
    name: str
    dtype: str = "string"        # string | int | float
    required: bool = False       # null/blank -> reject
    unique: bool = False         # duplicate value -> reject (keeps first)
    min_value: float | None = None


@dataclass(frozen=True)
class Schema:
    table: str
    columns: list[Column]
    key: str | None = None       # dedupe on full-row duplicates too

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.columns]


@dataclass
class Result:
    table: str
    clean: pd.DataFrame
    rejects: pd.DataFrame
    rows_in: int
    reasons: dict[str, int] = field(default_factory=dict)

    @property
    def rows_loaded(self) -> int:
        return len(self.clean)

    @property
    def rows_rejected(self) -> int:
        return len(self.rejects)

    @property
    def balanced(self) -> bool:
        """Every row in is accounted for. This is the invariant that matters."""
        return self.rows_in == self.rows_loaded + self.rows_rejected


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(r"[ \-]+", "_", regex=True)
    )
    return df


def _coerce(s: pd.Series, dtype: str) -> tuple[pd.Series, pd.Series]:
    """Returns (coerced, failed_mask). Never raises on bad values."""
    if dtype == "string":
        return s.astype("string").str.strip(), pd.Series(False, index=s.index)
    num = pd.to_numeric(s, errors="coerce")
    failed = num.isna() & s.notna() & (s.astype("string").str.strip() != "")
    if dtype == "int":
        return num.astype("Int64"), failed
    return num.astype("Float64"), failed


def validate(df: pd.DataFrame, schema: Schema) -> Result:
    df = normalise_columns(df)
    rows_in = len(df)

    missing = [c for c in schema.names if c not in df.columns]
    if missing:
        # Structural failure. Quarantine the whole frame rather than guess.
        rejects = df.copy()
        rejects[REJECT_COL] = f"schema_mismatch: missing {', '.join(missing)}"
        return Result(schema.table, df.head(0), rejects, rows_in,
                      {"schema_mismatch": rows_in})

    df = df[schema.names]
    reasons = pd.Series("", index=df.index, dtype="string")

    def flag(mask: pd.Series, why: str) -> None:
        hit = mask & (reasons == "")
        reasons.loc[hit] = why

    for col in schema.columns:
        s = df[col.name]
        if col.dtype == "string":
            s = s.astype("string").str.strip()
            df[col.name] = s.replace("", pd.NA)
        else:
            coerced, failed = _coerce(s, col.dtype)
            flag(failed, f"bad_{col.dtype}: {col.name}")
            df[col.name] = coerced

        if col.required:
            flag(df[col.name].isna(), f"missing_required: {col.name}")
        if col.min_value is not None and col.dtype != "string":
            flag(df[col.name] < col.min_value, f"below_min: {col.name}")
        if col.unique:
            flag(df[col.name].duplicated(keep="first"), f"duplicate: {col.name}")

    flag(df.duplicated(keep="first"), "duplicate_row")

    bad = reasons != ""
    rejects = df[bad].copy()
    rejects[REJECT_COL] = reasons[bad]
    clean = df[~bad].copy()

    counts = rejects[REJECT_COL].value_counts().to_dict() if len(rejects) else {}
    return Result(schema.table, clean, rejects, rows_in, counts)


def quarantine(result: Result, out_dir: Path) -> Path | None:
    if result.rows_rejected == 0:
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{result.table}_rejects.csv"
    result.rejects.to_csv(path, index=False)
    return path


def report(results: list[Result]) -> str:
    """Markdown, written for GITHUB_STEP_SUMMARY."""
    total_in = sum(r.rows_in for r in results)
    total_ok = sum(r.rows_loaded for r in results)
    total_bad = sum(r.rows_rejected for r in results)

    lines = [
        "## Data quality report",
        "",
        "| Table | In | Loaded | Quarantined | Pass rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in results:
        rate = f"{100 * r.rows_loaded / r.rows_in:.0f}%" if r.rows_in else "n/a"
        lines.append(
            f"| `{r.table}` | {r.rows_in} | {r.rows_loaded} | {r.rows_rejected} | {rate} |"
        )
    rate = f"{100 * total_ok / total_in:.0f}%" if total_in else "n/a"
    lines.append(f"| **total** | **{total_in}** | **{total_ok}** | **{total_bad}** | **{rate}** |")

    if total_bad:
        lines += ["", "### Why rows were rejected", "", "| Reason | Rows |", "|---|---:|"]
        agg: dict[str, int] = {}
        for r in results:
            for why, n in r.reasons.items():
                agg[why] = agg.get(why, 0) + n
        for why, n in sorted(agg.items(), key=lambda kv: -kv[1]):
            lines.append(f"| `{why}` | {n} |")

    unbalanced = [r.table for r in results if not r.balanced]
    lines += ["", "---", ""]
    lines.append(
        f"**Row accounting:** every input row landed somewhere ({total_ok} loaded + {total_bad} quarantined = {total_in} in)."
        if not unbalanced
        else f"**ROW ACCOUNTING FAILED** for: {', '.join(unbalanced)}. Rows went missing."
    )
    return "\n".join(lines)


# --- Schemas for the retail dataset ------------------------------------

CUSTOMERS = Schema(
    table="customers",
    columns=[
        Column("customerid", "int", required=True, unique=True),
        Column("customer_name", "string", required=True),
        Column("email", "string", required=True),
        Column("city", "string", required=True),
    ],
)

PRODUCTS = Schema(
    table="products",
    columns=[
        Column("productid", "int", required=True, unique=True),
        Column("productname", "string", required=True),
        Column("category", "string", required=True),
        Column("price", "float", required=True, min_value=0),
    ],
)

ORDERS = Schema(
    table="orders",
    columns=[
        Column("orderid", "int", required=True, unique=True),
        Column("customerid", "int", required=True),
        Column("productid", "int", required=True),
        Column("quantity", "int", required=True, min_value=1),
    ],
)
