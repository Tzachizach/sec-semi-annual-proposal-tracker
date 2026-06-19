# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-19. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1828 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1828 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1868 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.00 | 0.000 | -0.019 | 0.155 | — | — |
| Accountant CPA | +1.21 | 0.258 | +0.025 | 0.487 | +1.31 | 0.044 |
| Issuer-current | +2.14 | 0.053 | +0.078 | 0.375 | +2.51 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.011 | 0.001 | +2.07 | 0.002 |
| Investment prof. | (sep.) | 0.998 | -0.013 | 0.002 | +0.03 | 0.980 |
| Academic | +1.73 | 0.226 | +0.171 | 0.325 | +2.10 | 0.007 |
| Industry pract. | +0.95 | 0.375 | +0.018 | 0.555 | +0.85 | 0.202 |
| Legal pract. | +2.74 | 0.015 | +0.131 | 0.329 | +1.81 | 0.106 |
| Trade assoc. | +2.73 | 0.053 | +0.307 | 0.258 | +1.89 | 0.153 |
| Student | +2.47 | 0.028 | +0.112 | 0.348 | +1.48 | 0.180 |
| log(words+1) | +0.54 | 0.026 | +0.007 | 0.057 | +0.66 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1828 | -101.07 | 0.119 |
| LPM   | 1828   | (OLS) | R²=0.043, adj-R²=0.038 |
| Ordinal logit | 1868 | -263.59 | 0.144 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -263.59
- Multinomial logit LL: -255.43
- LR = 2 × (-255.43 − -263.59) = 16.31, df = 10, p = 0.0910

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0910 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
