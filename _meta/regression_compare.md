# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-04. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=618 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=618 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=643 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.22 | 0.000 | -0.021 | 0.370 | — | — |
| Accountant CPA | +1.76 | 0.115 | +0.061 | 0.406 | +1.91 | 0.007 |
| Issuer-current | +2.45 | 0.047 | +0.177 | 0.340 | +2.66 | 0.000 |
| Issuer-former | (sep.) | 0.980 | -0.017 | 0.020 | +1.91 | 0.023 |
| Investment prof. | (sep.) | 0.993 | -0.018 | 0.028 | (sep.) | 0.890 |
| Academic | +2.33 | 0.137 | +0.294 | 0.267 | +2.37 | 0.006 |
| Industry pract. | +1.18 | 0.299 | +0.039 | 0.514 | +0.53 | 0.539 |
| Student | +3.32 | 0.012 | +0.313 | 0.264 | +2.51 | 0.070 |
| log(words+1) | +0.45 | 0.111 | +0.009 | 0.196 | +0.66 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 618 | -49.93 | 0.156 |
| LPM   | 618   | (OLS) | R²=0.077, adj-R²=0.065 |
| Ordinal logit | 643 | -127.36 | 0.227 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -127.36
- Multinomial logit LL: -120.29
- LR = 2 × (-120.29 − -127.36) = 14.14, df = 8, p = 0.0782

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.0782 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
