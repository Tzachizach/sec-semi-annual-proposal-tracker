# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-11. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=967 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=967 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=998 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.41 | nan | -0.025 | 0.170 | — | — |
| Accountant CPA | +1.67 | nan | +0.041 | 0.426 | +1.60 | 0.018 |
| Issuer-current | +2.31 | nan | +0.097 | 0.367 | +2.49 | 0.000 |
| Issuer-former | (sep.) | nan | -0.011 | 0.013 | +2.23 | 0.001 |
| Investment prof. | (sep.) | nan | -0.013 | 0.022 | (sep.) | 0.999 |
| Academic | +2.07 | nan | +0.219 | 0.293 | +2.24 | 0.006 |
| Industry pract. | +1.16 | nan | +0.024 | 0.513 | +0.38 | 0.639 |
| Legal pract. | (sep.) | nan | +0.994 | 0.000 | (sep.) | 1.000 |
| Trade assoc. | (sep.) | nan | -0.020 | 0.030 | (sep.) | 0.924 |
| Student | +3.68 | nan | +0.318 | 0.255 | +2.66 | 0.057 |
| log(words+1) | +0.62 | nan | +0.008 | 0.095 | +0.74 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 967 | -54.04 | 0.216 |
| LPM   | 967   | (OLS) | R²=0.134, adj-R²=0.125 |
| Ordinal logit | 998 | -161.24 | 0.221 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -161.24
- Multinomial logit LL: -155.73
- LR = 2 × (-155.73 − -161.24) = 11.01, df = 10, p = 0.3564

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.3564 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Legal pract.', 'Trade assoc.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.', 'Trade assoc.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
