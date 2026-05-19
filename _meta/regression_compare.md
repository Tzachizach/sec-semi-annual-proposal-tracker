# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-19. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=227 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=227 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=250 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.01 | 0.000 | -0.039 | 0.309 | — | — |
| Accountant CPA | +1.50 | 0.202 | +0.067 | 0.444 | +1.41 | 0.054 |
| Issuer-current | +1.91 | 0.136 | +0.161 | 0.403 | +2.14 | 0.001 |
| Issuer-former | (sep.) | 1.000 | -0.027 | 0.055 | +0.69 | 0.540 |
| Investment prof. | (sep.) | 1.000 | -0.031 | 0.077 | (sep.) | 0.914 |
| Academic | +2.10 | 0.269 | +0.423 | 0.226 | +2.36 | 0.024 |
| Industry pract. | (sep.) | 1.000 | -0.031 | 0.081 | -0.51 | 0.659 |
| Student | +3.59 | 0.022 | +0.467 | 0.212 | +3.28 | 0.094 |
| log(words+1) | +0.52 | 0.145 | +0.015 | 0.183 | +0.62 | 0.001 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 227 | -26.77 | 0.227 |
| LPM   | 227   | (OLS) | R²=0.150, adj-R²=0.119 |
| Ordinal logit | 250 | -86.21 | 0.226 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -86.21
- Multinomial logit LL: -81.61
- LR = 2 × (-81.61 − -86.21) = 9.20, df = 8, p = 0.3256

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.3256 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
