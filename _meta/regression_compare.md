# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-22. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1996 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1996 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2037 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.17 | 0.000 | -0.018 | 0.140 | — | — |
| Accountant CPA | +1.24 | 0.248 | +0.025 | 0.481 | +1.38 | 0.033 |
| Issuer-current | +2.08 | 0.058 | +0.066 | 0.381 | +2.76 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.010 | 0.001 | +2.16 | 0.001 |
| Investment prof. | (sep.) | 0.999 | -0.011 | 0.002 | +0.13 | 0.900 |
| Academic | +1.74 | 0.226 | +0.173 | 0.320 | +2.33 | 0.002 |
| Industry pract. | +0.92 | 0.391 | +0.016 | 0.553 | +0.90 | 0.173 |
| Legal pract. | +2.61 | 0.020 | +0.113 | 0.339 | +1.69 | 0.125 |
| Trade assoc. | +2.76 | 0.051 | +0.308 | 0.255 | +2.09 | 0.114 |
| Student | +2.54 | 0.024 | +0.113 | 0.344 | +1.60 | 0.147 |
| log(words+1) | +0.56 | 0.022 | +0.007 | 0.051 | +0.61 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1996 | -102.65 | 0.119 |
| LPM   | 1996   | (OLS) | R²=0.042, adj-R²=0.037 |
| Ordinal logit | 2037 | -271.29 | 0.145 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -271.29
- Multinomial logit LL: -263.23
- LR = 2 × (-263.23 − -271.29) = 16.13, df = 10, p = 0.0960

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0960 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
