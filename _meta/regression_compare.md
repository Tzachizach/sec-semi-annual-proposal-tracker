# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-16. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1323 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1323 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1358 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.70 | 0.000 | -0.017 | 0.264 | — | — |
| Accountant CPA | +1.39 | 0.197 | +0.031 | 0.461 | +1.40 | 0.033 |
| Issuer-current | +2.15 | 0.055 | +0.086 | 0.372 | +2.39 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.011 | 0.002 | +2.06 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.013 | 0.005 | (sep.) | 0.995 |
| Academic | +1.78 | 0.222 | +0.171 | 0.324 | +1.86 | 0.018 |
| Industry pract. | +1.00 | 0.355 | +0.021 | 0.541 | +0.30 | 0.708 |
| Legal pract. | +3.49 | 0.004 | +0.238 | 0.276 | +2.66 | 0.028 |
| Trade assoc. | (sep.) | 0.999 | -0.019 | 0.015 | (sep.) | 0.918 |
| Student | +3.00 | 0.011 | +0.186 | 0.306 | +1.96 | 0.098 |
| log(words+1) | +0.50 | 0.061 | +0.007 | 0.110 | +0.71 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1323 | -79.90 | 0.121 |
| LPM   | 1323   | (OLS) | R²=0.045, adj-R²=0.038 |
| Ordinal logit | 1358 | -211.67 | 0.165 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -211.67
- Multinomial logit LL: -204.28
- LR = 2 × (-204.28 − -211.67) = 14.78, df = 10, p = 0.1403

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1403 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Trade assoc.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Trade assoc.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
