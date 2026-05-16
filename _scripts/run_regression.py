#!/usr/bin/env python3
"""
Run the logit regression on the current dataset and overwrite _meta/regression_results.md.

Outcome:  Support = 1, Oppose = 0  (Conditional and PDF dropped)
Predictors: 5 entity-type dummies (reference = Individual investor) + log(words+1).

Usage:
    python3 _scripts/run_regression.py

Requires: statsmodels, pandas, numpy.  pip install --break-system-packages statsmodels pandas numpy
"""
import datetime
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.discrete.discrete_model import Logit
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e}\n"
        "Install with: pip install --break-system-packages statsmodels pandas numpy\n"
    )
    sys.exit(2)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
RECORDS = PROJECT_DIR / "_meta" / "renumbered_records.json"
OUT = PROJECT_DIR / "_meta" / "regression_results.md"

ENTITY_ORDER = [
    "Individual",
    "Accountant (CPA)",
    "Issuer / Corporate — current",
    "Issuer / Corporate — former",
    "Investment professional",
    "Academic researcher",
    "Industry practitioner / technologist",
    "Student",
]
REF = "Individual"


def col_name(entity):
    return "ent_" + entity.replace(" ", "_").replace("/", "").replace("(", "").replace(")", "").replace("__", "_").strip("_")


def main():
    records = json.loads(RECORDS.read_text())
    rows = [
        {"support": 1 if r["stance"] == "Support" else 0, "entity": r.get("entity", ""), "words": r.get("words", 0)}
        for r in records if r["stance"] in ("Support", "Oppose")
    ]
    df = pd.DataFrame(rows)
    df["log_words"] = np.log(df["words"].clip(lower=1) + 1)
    for e in ENTITY_ORDER:
        if e != REF:
            df[col_name(e)] = (df["entity"] == e).astype(int)

    X_cols = [col_name(e) for e in ENTITY_ORDER if e != REF] + ["log_words"]
    X = sm.add_constant(df[X_cols])
    y = df["support"]
    n = int(len(df))
    n_supp = int(y.sum())
    n_oppose = n - n_supp

    # Try default Newton optimizer; fall back to BFGS if Hessian is singular
    # (separation in multiple categories can make the Newton step unstable).
    try:
        res = Logit(y, X).fit(disp=False, maxiter=200)
    except Exception:
        res = Logit(y, X).fit(method="bfgs", disp=False, maxiter=500)

    odds = np.exp(res.params)
    ci_low = np.exp(res.conf_int()[0])
    ci_high = np.exp(res.conf_int()[1])

    today = datetime.date.today().isoformat()

    lines = [
        "# SEC S7-2026-15 — regression results",
        "",
        f"_Last run: {today}. Will update as the docket grows._",
        "",
        "## Specification",
        "",
        "- **Outcome:** binary indicator, 1 if letter is Support, 0 if Oppose.",
        f"- **Sample:** {n} letters classified as either Oppose ({n_oppose}) or Support ({n_supp}). Conditional letters and PDF-only letters dropped.",
        "- **Independent variables:**",
        "  - 7 entity-type dummies (reference: Individual).",
        "  - `log(words+1)` — natural log of letter word count.",
        "",
        "## Logit results",
        "",
        "| Variable | Coef | SE | p-value | Odds ratio | 95% CI for OR |",
        "|---|---:|---:|---:|---:|---|",
    ]

    label_for = {
        "const": "Constant",
        "log_words": "log(words+1)",
    }
    for e in ENTITY_ORDER:
        if e != REF:
            label_for[col_name(e)] = e

    # Detect perfect-separation buckets directly from the data — a bucket with 0 Support
    # or 0 Oppose in the regression sample is separated. SE inflation is unreliable when
    # the optimizer is BFGS rather than Newton, so use the data check.
    separated_cols = set()
    for e in ENTITY_ORDER:
        if e == REF: continue
        col = col_name(e)
        if col not in df.columns: continue
        bucket_y = df.loc[df[col] == 1, "support"]
        if len(bucket_y) > 0 and (bucket_y.sum() == 0 or bucket_y.sum() == len(bucket_y)):
            separated_cols.add(col)

    for var in res.params.index:
        coef = res.params[var]
        se = res.bse[var]
        p = res.pvalues[var]
        oratio = odds[var]
        lo, hi = ci_low[var], ci_high[var]
        # If complete separation, SE will be massive — also flag if data-level check finds it.
        massive = (var in separated_cols) or se > 1e3 or not np.isfinite(coef) or abs(coef) > 50
        if massive:
            lines.append(
                f"| {label_for.get(var, var)} | {coef:+.2f} | (huge) | {p:.3f} | ≈ 0 | (separated) |"
            )
        else:
            ci_str = f"[{lo:.2f}, {hi:.2f}]"
            lines.append(
                f"| {label_for.get(var, var)} | {coef:+.2f} | {se:.2f} | {p:.3f} | {oratio:.2f} | {ci_str} |"
            )

    lines += [
        "",
        f"**Fit:** McFadden pseudo-R² = {res.prsquared:.3f}, N = {n}.",
        "",
        "## Interpretation",
        "",
        "Run `python3 _scripts/run_regression.py` again after new letters are added to refresh the numbers above.",
        "Reading the coefficients: positive values increase the odds of Support relative to Oppose. The reference category for entity dummies is Individual.",
        "",
        "## Reproducibility",
        "",
        "Source data: `_meta/renumbered_records.json`.",
        "Estimation: `statsmodels.discrete.discrete_model.Logit`, default optimizer.",
    ]

    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT.relative_to(PROJECT_DIR)}")
    print(f"  N={n}, Support={n_supp}, Oppose={n_oppose}, pseudo-R²={res.prsquared:.3f}")


if __name__ == "__main__":
    main()
