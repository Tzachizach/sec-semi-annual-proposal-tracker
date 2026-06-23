# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-23. Three specs on the same predictor set, different outcomes._

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
| Constant | -7.07 | 0.000 | -0.019 | 0.139 | — | — |
| Accountant CPA | +1.21 | 0.264 | +0.024 | 0.486 | +1.28 | 0.052 |
| Issuer-current | +2.09 | 0.057 | +0.066 | 0.381 | +2.47 | 0.000 |
| Issuer-former | (sep.) | 0.990 | -0.010 | 0.001 | +2.15 | 0.001 |
| Investment prof. | (sep.) | 0.997 | -0.012 | 0.002 | -0.04 | 0.971 |
| Academic | +1.81 | 0.203 | +0.172 | 0.321 | +2.38 | 0.001 |
| Industry pract. | +0.85 | 0.429 | +0.015 | 0.586 | +0.73 | 0.273 |
| Legal pract. | +2.63 | 0.019 | +0.113 | 0.340 | +1.66 | 0.135 |
| Trade assoc. | +2.48 | 0.099 | +0.304 | 0.259 | +1.54 | 0.262 |
| Student | +2.56 | 0.022 | +0.112 | 0.344 | +1.55 | 0.161 |
| log(words+1) | +0.54 | 0.023 | +0.007 | 0.052 | +0.68 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1996 | -102.73 | 0.118 |
| LPM   | 1996   | (OLS) | R²=0.042, adj-R²=0.037 |
| Ordinal logit | 2037 | -268.99 | 0.152 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -268.99
- Multinomial logit LL: -260.79
- LR = 2 × (-260.79 − -268.99) = 16.40, df = 10, p = 0.0888

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0888 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
