# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-02. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=496 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=496 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=521 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.39 | 0.000 | -0.039 | 0.120 | — | — |
| Accountant CPA | +1.67 | 0.141 | +0.059 | 0.422 | +1.80 | 0.012 |
| Issuer-current | +2.16 | 0.086 | +0.171 | 0.363 | +2.49 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.019 | 0.018 | +1.95 | 0.024 |
| Investment prof. | (sep.) | 1.000 | -0.022 | 0.030 | (sep.) | 0.975 |
| Academic | +1.54 | 0.353 | +0.279 | 0.285 | +2.11 | 0.016 |
| Industry pract. | (sep.) | 1.000 | -0.026 | 0.037 | -0.51 | 0.652 |
| Student | +3.14 | 0.020 | +0.308 | 0.277 | +2.33 | 0.098 |
| log(words+1) | +0.73 | 0.024 | +0.013 | 0.068 | +0.76 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 496 | -38.91 | 0.205 |
| LPM   | 496   | (OLS) | R²=0.094, adj-R²=0.079 |
| Ordinal logit | 521 | -112.66 | 0.245 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -112.66
- Multinomial logit LL: -106.71
- LR = 2 × (-106.71 − -112.66) = 11.89, df = 8, p = 0.1560

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.1560 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
