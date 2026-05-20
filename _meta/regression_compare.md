# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-20. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=259 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=259 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=283 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -5.89 | 0.000 | -0.039 | 0.271 | — | — |
| Accountant CPA | +1.42 | 0.218 | +0.066 | 0.455 | +1.42 | 0.050 |
| Issuer-current | +1.84 | 0.142 | +0.159 | 0.407 | +2.02 | 0.002 |
| Issuer-former | (sep.) | 1.000 | -0.029 | 0.028 | +0.70 | 0.538 |
| Investment prof. | (sep.) | 1.000 | -0.032 | 0.041 | (sep.) | 0.938 |
| Academic | +1.61 | 0.318 | +0.263 | 0.311 | +1.81 | 0.037 |
| Industry pract. | (sep.) | 1.000 | -0.032 | 0.044 | -0.56 | 0.622 |
| Student | +3.52 | 0.023 | +0.465 | 0.213 | +3.23 | 0.093 |
| log(words+1) | +0.51 | 0.115 | +0.016 | 0.131 | +0.64 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 259 | -31.54 | 0.193 |
| LPM   | 259   | (OLS) | R²=0.116, adj-R²=0.088 |
| Ordinal logit | 283 | -95.78 | 0.210 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -95.78
- Multinomial logit LL: -91.24
- LR = 2 × (-91.24 − -95.78) = 9.07, df = 8, p = 0.3360

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.3360 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
