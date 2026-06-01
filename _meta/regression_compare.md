# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-01. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=429 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=429 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=454 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.17 | 0.000 | -0.041 | 0.126 | — | — |
| Accountant CPA | +1.52 | 0.182 | +0.057 | 0.446 | +1.64 | 0.021 |
| Issuer-current | +2.01 | 0.110 | +0.167 | 0.376 | +2.36 | 0.000 |
| Issuer-former | (sep.) | 0.941 | -0.022 | 0.017 | +1.80 | 0.038 |
| Investment prof. | (sep.) | 0.985 | -0.026 | 0.030 | (sep.) | 0.977 |
| Academic | +1.42 | 0.391 | +0.273 | 0.294 | +1.99 | 0.022 |
| Industry pract. | (sep.) | 0.989 | -0.030 | 0.035 | -0.64 | 0.574 |
| Student | +2.99 | 0.027 | +0.304 | 0.284 | +2.18 | 0.120 |
| log(words+1) | +0.71 | 0.026 | +0.015 | 0.068 | +0.74 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 429 | -37.99 | 0.200 |
| LPM   | 429   | (OLS) | R²=0.094, adj-R²=0.076 |
| Ordinal logit | 454 | -110.18 | 0.236 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -110.18
- Multinomial logit LL: -104.30
- LR = 2 × (-104.30 − -110.18) = 11.76, df = 8, p = 0.1623

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.1623 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
