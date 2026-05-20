# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-20. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=249 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=249 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=273 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -5.64 | 0.000 | -0.032 | 0.359 | — | — |
| Accountant CPA | +1.39 | 0.229 | +0.065 | 0.458 | +1.39 | 0.055 |
| Issuer-current | +1.85 | 0.140 | +0.160 | 0.403 | +2.02 | 0.002 |
| Issuer-former | (sep.) | 1.000 | -0.029 | 0.031 | +0.67 | 0.553 |
| Investment prof. | (sep.) | 1.000 | -0.033 | 0.047 | (sep.) | 0.959 |
| Academic | +2.17 | 0.239 | +0.425 | 0.224 | +2.16 | 0.020 |
| Industry pract. | (sep.) | 1.000 | -0.032 | 0.047 | -0.56 | 0.624 |
| Student | +3.49 | 0.023 | +0.466 | 0.211 | +3.21 | 0.094 |
| log(words+1) | +0.46 | 0.166 | +0.014 | 0.174 | +0.61 | 0.001 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 249 | -31.11 | 0.196 |
| LPM   | 249   | (OLS) | R²=0.132, adj-R²=0.104 |
| Ordinal logit | 273 | -94.52 | 0.212 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -94.52
- Multinomial logit LL: -89.18
- LR = 2 × (-89.18 − -94.52) = 10.68, df = 8, p = 0.2204

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.2204 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
