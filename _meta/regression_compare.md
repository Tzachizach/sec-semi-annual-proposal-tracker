# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-21. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=262 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=262 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=287 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -5.91 | 0.000 | -0.039 | 0.268 | — | — |
| Accountant CPA | +1.43 | 0.216 | +0.066 | 0.454 | +1.43 | 0.049 |
| Issuer-current | +1.84 | 0.142 | +0.159 | 0.406 | +2.03 | 0.002 |
| Issuer-former | (sep.) | 1.000 | -0.029 | 0.028 | +1.36 | 0.116 |
| Investment prof. | (sep.) | 1.000 | -0.032 | 0.041 | (sep.) | 0.991 |
| Academic | +1.61 | 0.319 | +0.264 | 0.311 | +1.82 | 0.036 |
| Industry pract. | (sep.) | 1.000 | -0.034 | 0.045 | -0.70 | 0.537 |
| Student | +3.52 | 0.023 | +0.465 | 0.213 | +3.25 | 0.094 |
| log(words+1) | +0.51 | 0.112 | +0.016 | 0.129 | +0.64 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 262 | -31.56 | 0.194 |
| LPM   | 262   | (OLS) | R²=0.116, adj-R²=0.088 |
| Ordinal logit | 287 | -97.76 | 0.212 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -97.76
- Multinomial logit LL: -92.91
- LR = 2 × (-92.91 − -97.76) = 9.71, df = 8, p = 0.2862

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.2862 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
