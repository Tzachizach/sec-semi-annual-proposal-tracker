# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-23. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=2109 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=2109 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2150 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.84 | 0.000 | -0.029 | 0.039 | — | — |
| Accountant CPA | +1.09 | 0.324 | +0.023 | 0.505 | +1.23 | 0.069 |
| Issuer-current | +2.05 | 0.063 | +0.064 | 0.391 | +2.37 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.011 | 0.001 | +2.17 | 0.001 |
| Investment prof. | (sep.) | 0.999 | -0.014 | 0.001 | -0.12 | 0.910 |
| Academic | +1.32 | 0.358 | +0.165 | 0.340 | +1.33 | 0.085 |
| Industry pract. | +0.73 | 0.503 | +0.013 | 0.629 | +0.48 | 0.495 |
| Legal pract. | +1.84 | 0.159 | +0.106 | 0.338 | +1.08 | 0.354 |
| Trade assoc. | +1.50 | 0.291 | +0.212 | 0.324 | +0.42 | 0.745 |
| Student | +2.51 | 0.026 | +0.111 | 0.353 | +1.53 | 0.167 |
| log(words+1) | +0.71 | 0.002 | +0.009 | 0.014 | +0.84 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 2109 | -101.55 | 0.137 |
| LPM   | 2109   | (OLS) | R²=0.041, adj-R²=0.037 |
| Ordinal logit | 2150 | -264.64 | 0.175 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -264.64
- Multinomial logit LL: -255.06
- LR = 2 × (-255.06 − -264.64) = 19.17, df = 10, p = 0.0382

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0382 → reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
