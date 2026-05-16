#!/usr/bin/env python3
"""
Compare three regression specifications on the SEC S7-2026-15 dataset:

  1. Logit         — Support(1) / Oppose(0). Conditional dropped. Matches the headline result.
  2. LPM (OLS)     — Support(1) / Oppose(0). Conditional dropped. HC1 robust SE.
  3. Ordinal logit — Oppose(0) < Conditional(1) < Support(2). Full N=159 sample.

All three use the same predictors: 7 entity dummies (reference = Individual) + log(words+1).

The script also runs an LR test of the proportional-odds assumption by comparing the
ordinal logit to an unrestricted multinomial logit.

Usage:
    python3 _scripts/run_regression_compare.py
"""
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.discrete.discrete_model import Logit, MNLogit
    from statsmodels.miscmodels.ordinal_model import OrderedModel
    from scipy import stats
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e}\n"
        "Install with: pip install --break-system-packages statsmodels pandas numpy scipy\n"
    )
    sys.exit(2)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
RECORDS = PROJECT_DIR / "_meta" / "renumbered_records.json"
OUT = PROJECT_DIR / "_meta" / "regression_compare.md"
OUT_JSON = PROJECT_DIR / "_meta" / "regression_compare.json"

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
    return "ent_" + (
        entity.replace(" ", "_")
        .replace("/", "")
        .replace("(", "")
        .replace(")", "")
        .replace("__", "_")
        .strip("_")
    )


def short(entity):
    if entity == "Individual": return "Individual (ref)"
    if entity == "Accountant (CPA)": return "Accountant CPA"
    if entity == "Issuer / Corporate — current": return "Issuer-current"
    if entity == "Issuer / Corporate — former": return "Issuer-former"
    if entity == "Investment professional": return "Investment prof."
    if entity == "Academic researcher": return "Academic"
    if entity == "Industry practitioner / technologist": return "Industry pract."
    if entity == "Student": return "Student"
    return entity


def build_frame(records):
    rows = []
    for r in records:
        s = r["stance"]
        if s not in ("Support", "Conditional", "Oppose"):
            continue
        rows.append({
            "ord": {"Oppose": 0, "Conditional": 1, "Support": 2}[s],
            "support": 1 if s == "Support" else 0,
            "stance": s,
            "entity": r.get("entity", ""),
            "words": r.get("words", 0),
        })
    df = pd.DataFrame(rows)
    df["log_words"] = np.log(df["words"].clip(lower=1) + 1)
    for e in ENTITY_ORDER:
        if e != REF:
            df[col_name(e)] = (df["entity"] == e).astype(int)
    return df


def fmt_coef(c, se, p, sep=False):
    if sep or not np.isfinite(c) or abs(c) > 50 or se > 1e3:
        return f"{c:+.2f}", "(huge)", f"{p:.3f}", "(separated)"
    return f"{c:+.3f}", f"{se:.3f}", f"{p:.3f}", ""


def fit_logit(df, X_cols):
    sub = df[df["stance"].isin(("Support", "Oppose"))].copy()
    X = sm.add_constant(sub[X_cols])
    y = sub["support"]
    try:
        res = Logit(y, X).fit(disp=False, maxiter=200)
    except Exception:
        res = Logit(y, X).fit(method="bfgs", disp=False, maxiter=500)
    # data-level separation check
    separated = set()
    for c in X_cols:
        if c == "log_words": continue
        bucket_y = sub.loc[sub[c] == 1, "support"]
        if len(bucket_y) > 0 and (bucket_y.sum() == 0 or bucket_y.sum() == len(bucket_y)):
            separated.add(c)
    return res, sub, separated


def fit_lpm(df, X_cols):
    sub = df[df["stance"].isin(("Support", "Oppose"))].copy()
    X = sm.add_constant(sub[X_cols])
    y = sub["support"]
    res = sm.OLS(y, X).fit(cov_type="HC1")
    # same separation diagnostic just for reference
    separated = set()
    for c in X_cols:
        if c == "log_words": continue
        bucket_y = sub.loc[sub[c] == 1, "support"]
        if len(bucket_y) > 0 and (bucket_y.sum() == 0 or bucket_y.sum() == len(bucket_y)):
            separated.add(c)
    return res, sub, separated


def fit_ordinal(df, X_cols):
    sub = df.copy()
    X = sub[X_cols]
    y = sub["ord"]
    try:
        res = OrderedModel(y, X, distr="logit").fit(method="bfgs", disp=False, maxiter=500)
    except Exception as e:
        sys.stderr.write(f"Ordinal logit BFGS failed: {e}\n")
        res = OrderedModel(y, X, distr="logit").fit(method="lbfgs", disp=False, maxiter=1000)
    # separation: bucket has variation only in one ordinal class
    separated = set()
    for c in X_cols:
        if c == "log_words": continue
        bucket_y = sub.loc[sub[c] == 1, "ord"]
        if len(bucket_y) > 0 and bucket_y.nunique() == 1:
            separated.add(c)
    return res, sub, separated


def fit_mnlogit(df, X_cols):
    sub = df.copy()
    X = sm.add_constant(sub[X_cols])
    y = sub["ord"]
    try:
        res = MNLogit(y, X).fit(method="bfgs", disp=False, maxiter=1000)
    except Exception:
        res = MNLogit(y, X).fit(method="lbfgs", disp=False, maxiter=2000)
    return res, sub


def lr_test_po(ord_res, mn_res, p_predictors):
    """LR test of proportional-odds assumption: ordinal vs multinomial logit."""
    ll_r = ord_res.llf
    ll_u = mn_res.llf
    lr = 2 * (ll_u - ll_r)
    df_ = p_predictors  # difference in parameters
    pval = 1 - stats.chi2.cdf(lr, df_)
    return lr, df_, pval


def write_md(lines):
    OUT.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT.relative_to(PROJECT_DIR)}")


def main():
    records = json.loads(RECORDS.read_text())
    df = build_frame(records)
    X_cols = [col_name(e) for e in ENTITY_ORDER if e != REF] + ["log_words"]

    print(f"Loaded {len(records)} records → {len(df)} usable rows")
    print(f"  Oppose={(df['ord']==0).sum()}, Conditional={(df['ord']==1).sum()}, Support={(df['ord']==2).sum()}")

    # --- 1. Logit ---
    logit_res, logit_sub, logit_sep = fit_logit(df, X_cols)
    n_logit = int(len(logit_sub))
    print(f"\nLogit: N={n_logit}, McFadden R²={logit_res.prsquared:.3f}")
    print(f"  separated: {[c for c in logit_sep]}")

    # --- 2. LPM ---
    lpm_res, lpm_sub, lpm_sep = fit_lpm(df, X_cols)
    n_lpm = int(len(lpm_sub))
    print(f"\nLPM:   N={n_lpm}, R²={lpm_res.rsquared:.3f}, adj-R²={lpm_res.rsquared_adj:.3f}")
    print(f"  separated buckets (same as logit): {[c for c in lpm_sep]}")

    # --- 3. Ordinal logit ---
    ord_res, ord_sub, ord_sep = fit_ordinal(df, X_cols)
    n_ord = int(len(ord_sub))
    # statsmodels' OrderedModel does not expose prsquared. Compute McFadden R²
    # against the empirical marginal-distribution null: LL_null = Σ n_k log(p_k).
    n_total = len(ord_sub)
    ll_null = 0.0
    for k in (0, 1, 2):
        n_k = int((ord_sub["ord"] == k).sum())
        if n_k > 0:
            ll_null += n_k * np.log(n_k / n_total)
    mcfadden_ord = 1 - (ord_res.llf / ll_null)
    print(f"\nOrdinal: N={n_ord}, McFadden R²={mcfadden_ord:.3f}")
    print(f"  separated (single ordinal class only): {[c for c in ord_sep]}")

    # --- 4. LR test of proportional odds ---
    mn_res, _ = fit_mnlogit(df, X_cols)
    lr, df_lr, p_lr = lr_test_po(ord_res, mn_res, p_predictors=len(X_cols))
    print(f"\nLR test of proportional odds: LR={lr:.2f}, df={df_lr}, p={p_lr:.4f}")
    print(f"  ordinal LL={ord_res.llf:.2f}, multinomial LL={mn_res.llf:.2f}")

    # ----------------------------------------------------------------
    # Markdown report
    # ----------------------------------------------------------------
    import datetime
    today = datetime.date.today().isoformat()

    lines = [
        "# SEC S7-2026-15 — regression spec comparison",
        "",
        f"_Last run: {today}. Three specs on the same predictor set, different outcomes._",
        "",
        "## Specifications",
        "",
        "| Spec | Outcome | Sample | Estimator |",
        "|---|---|---|---|",
        f"| Logit (baseline) | Support=1 / Oppose=0 | N={n_logit} | MLE logit |",
        f"| LPM (OLS) | Support=1 / Oppose=0 | N={n_lpm} | OLS, HC1 robust SE |",
        f"| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N={n_ord} | proportional-odds logit |",
        "",
        "Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).",
        "",
        "## Side-by-side coefficients",
        "",
        "| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    def coef_row(var, label):
        # logit
        if var in logit_res.params.index:
            lb = logit_res.params[var]
            lp = logit_res.pvalues[var]
            lsep = var in logit_sep
            lbs = "(sep.)" if lsep else f"{lb:+.2f}"
            lps = f"{lp:.3f}"
        else:
            lbs, lps = "—", "—"
        # lpm
        if var in lpm_res.params.index:
            mb = lpm_res.params[var]
            mp = lpm_res.pvalues[var]
            mbs = f"{mb:+.3f}"
            mps = f"{mp:.3f}"
        else:
            mbs, mps = "—", "—"
        # ordinal
        if var in ord_res.params.index:
            ob = ord_res.params[var]
            op = ord_res.pvalues[var]
            osep = var in ord_sep
            obs = "(sep.)" if osep else f"{ob:+.2f}"
            ops = f"{op:.3f}"
        else:
            obs, ops = "—", "—"
        return f"| {label} | {lbs} | {lps} | {mbs} | {mps} | {obs} | {ops} |"

    # Logit has a 'const' parameter, LPM has 'const', ordinal does NOT (cutpoints replace it).
    lines.append(coef_row("const", "Constant"))
    for e in ENTITY_ORDER:
        if e == REF: continue
        lines.append(coef_row(col_name(e), short(e)))
    lines.append(coef_row("log_words", "log(words+1)"))

    # Ordinal cutpoints — statsmodels stores transformed cutpoints; use res.transform_threshold_params
    # to recover the cumulative thresholds on the logit scale.
    try:
        thresholds = ord_res.transform_threshold_params(ord_res.params[-2:])
        lines.append("")
        lines.append(f"**Ordinal cutpoints (logit scale):** "
                     f"Oppose | Conditional = {thresholds[1]:.2f}, "
                     f"Conditional | Support = {thresholds[2]:.2f}")
    except Exception:
        pass

    lines += [
        "",
        "## Fit statistics",
        "",
        "| Spec | N | LL | McFadden R² / R² |",
        "|---|---:|---:|---:|",
        f"| Logit | {n_logit} | {logit_res.llf:.2f} | {logit_res.prsquared:.3f} |",
        f"| LPM   | {n_lpm}   | (OLS) | R²={lpm_res.rsquared:.3f}, adj-R²={lpm_res.rsquared_adj:.3f} |",
        f"| Ordinal logit | {n_ord} | {ord_res.llf:.2f} | {mcfadden_ord:.3f} |",
        "",
        "## Proportional-odds assumption (LR test)",
        "",
        f"Compared the ordinal logit (restricted, single slope vector) against an unrestricted "
        f"multinomial logit with the same predictors.",
        f"",
        f"- Ordinal logit LL: {ord_res.llf:.2f}",
        f"- Multinomial logit LL: {mn_res.llf:.2f}",
        f"- LR = 2 × ({mn_res.llf:.2f} − {ord_res.llf:.2f}) = {lr:.2f}, df = {df_lr}, p = {p_lr:.4f}",
        f"",
        f"Under H0 (proportional odds holds), LR follows χ²({df_lr}). "
        f"p = {p_lr:.4f} → "
        + ("reject proportional-odds." if p_lr < 0.05 else "do not reject proportional-odds.")
        + " Note: small-N artifact warning — the LR test has low power with the current Support count.",
        "",
        "## Notes on separation",
        "",
        "Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.",
        "Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. ",
        f"Buckets with single-class variation only: {[short(e) for e in ENTITY_ORDER if e != REF and col_name(e) in ord_sep]}.",
        "",
        "## Reproducibility",
        "",
        "Source data: `_meta/renumbered_records.json`.",
        "Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.",
    ]

    write_md(lines)

    # ----------------------------------------------------------------
    # JSON dump for build_and_push.py to consume
    # ----------------------------------------------------------------
    def spec_block(res, separated, is_lpm=False, is_ord=False):
        out = {"by_var": {}}
        for var in res.params.index:
            c = float(res.params[var])
            se = float(res.bse[var])
            p = float(res.pvalues[var])
            sep = var in separated
            out["by_var"][var] = {
                "coef": c, "se": se, "p": p, "separated": bool(sep),
            }
        return out

    # ordinal cutpoints: last two params are the threshold transform
    try:
        from statsmodels.miscmodels.ordinal_model import OrderedModel
        # Reconstruct the model object for transform_threshold_params
        ord_X = ord_sub[X_cols]
        ord_y = ord_sub["ord"]
        ord_model = OrderedModel(ord_y, ord_X, distr="logit")
        cuts = ord_model.transform_threshold_params(ord_res.params[-2:].values).tolist()
        # cuts is length K+1 with -inf at [0] and +inf at end conceptually; statsmodels returns [-inf, c1, c2]
        # We want the two finite thresholds.
        cuts_finite = [float(c) for c in cuts if np.isfinite(c)]
    except Exception:
        cuts_finite = []

    json_out = {
        "as_of": today,
        "n_records": int(len(records)),
        "logit": {
            "n": int(n_logit),
            "ll": float(logit_res.llf),
            "mcfadden": float(logit_res.prsquared),
            "n_support": int((logit_sub["support"] == 1).sum()),
            "n_oppose": int((logit_sub["support"] == 0).sum()),
            **spec_block(logit_res, logit_sep),
        },
        "lpm": {
            "n": int(n_lpm),
            "r2": float(lpm_res.rsquared),
            "adj_r2": float(lpm_res.rsquared_adj),
            "cov_type": "HC1",
            **spec_block(lpm_res, lpm_sep, is_lpm=True),
        },
        "ordinal": {
            "n": int(n_ord),
            "ll": float(ord_res.llf),
            "mcfadden": float(mcfadden_ord),
            "n_oppose": int((ord_sub["ord"] == 0).sum()),
            "n_conditional": int((ord_sub["ord"] == 1).sum()),
            "n_support": int((ord_sub["ord"] == 2).sum()),
            "cutpoints": cuts_finite,
            **spec_block(ord_res, ord_sep, is_ord=True),
        },
        "po_lr_test": {
            "lr": float(lr),
            "df": int(df_lr),
            "p": float(p_lr),
            "ordinal_ll": float(ord_res.llf),
            "multinomial_ll": float(mn_res.llf),
        },
        # canonical variable order for the build script
        "var_order": ["const"] + [col_name(e) for e in ENTITY_ORDER if e != REF] + ["log_words"],
        "labels": {
            "const": "Constant",
            "log_words": "log(words+1)",
            **{col_name(e): short(e) for e in ENTITY_ORDER if e != REF},
        },
    }
    OUT_JSON.write_text(json.dumps(json_out, indent=2))
    print(f"Wrote {OUT_JSON.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
