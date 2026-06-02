# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-02. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=455 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=455 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=480 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.24 | 0.000 | -0.039 | 0.127 | — | — |
| Accountant CPA | +1.59 | 0.162 | +0.058 | 0.434 | +1.71 | 0.016 |
| Issuer-current | +2.09 | 0.097 | +0.169 | 0.369 | +2.42 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.021 | 0.018 | +1.87 | 0.031 |
| Investment prof. | (sep.) | 1.000 | -0.023 | 0.029 | (sep.) | 0.975 |
| Academic | +1.50 | 0.366 | +0.276 | 0.289 | +2.06 | 0.018 |
| Industry pract. | (sep.) | 1.000 | -0.028 | 0.035 | -0.57 | 0.615 |
| Student | +3.06 | 0.024 | +0.306 | 0.280 | +2.25 | 0.109 |
| log(words+1) | +0.71 | 0.027 | +0.014 | 0.070 | +0.75 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 455 | -38.42 | 0.201 |
| LPM   | 455   | (OLS) | R²=0.094, adj-R²=0.077 |
| Ordinal logit | 480 | -111.33 | 0.239 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -111.33
- Multinomial logit LL: -105.44
- LR = 2 × (-105.44 − -111.33) = 11.79, df = 8, p = 0.1609

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.1609 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
