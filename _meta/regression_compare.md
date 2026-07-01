# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-07-01. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=2200 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=2200 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2244 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -8.65 | 0.000 | -0.050 | 0.004 | — | — |
| Accountant CPA | +0.66 | 0.562 | +0.018 | 0.599 | +1.31 | 0.022 |
| Issuer-current | +2.20 | 0.022 | +0.123 | 0.177 | +2.39 | 0.000 |
| Issuer-former | (sep.) | 0.951 | -0.013 | 0.001 | +2.16 | 0.001 |
| Investment prof. | -0.11 | 0.924 | +0.000 | 0.983 | -0.16 | 0.836 |
| Academic | +0.14 | 0.901 | +0.124 | 0.264 | +0.58 | 0.418 |
| Industry pract. | +0.40 | 0.714 | +0.008 | 0.773 | +0.35 | 0.618 |
| Legal pract. | +1.24 | 0.356 | +0.084 | 0.389 | +0.73 | 0.529 |
| Trade assoc. | +1.38 | 0.216 | +0.277 | 0.147 | +0.93 | 0.354 |
| Student | +2.39 | 0.034 | +0.107 | 0.373 | +1.50 | 0.176 |
| log(words+1) | +0.89 | 0.000 | +0.015 | 0.002 | +0.87 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 2200 | -113.19 | 0.199 |
| LPM   | 2200   | (OLS) | R²=0.069, adj-R²=0.065 |
| Ordinal logit | 2244 | -288.86 | 0.193 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -288.86
- Multinomial logit LL: -281.61
- LR = 2 × (-281.61 − -288.86) = 14.50, df = 10, p = 0.1515

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1515 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 1 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
