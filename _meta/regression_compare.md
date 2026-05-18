# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-18. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=181 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=181 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=202 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -5.41 | 0.003 | -0.030 | 0.511 | — | — |
| Accountant CPA | (sep.) | 0.959 | -0.027 | 0.054 | +0.75 | 0.370 |
| Issuer-current | +1.75 | 0.172 | +0.157 | 0.420 | +2.10 | 0.001 |
| Issuer-former | (sep.) | 0.955 | -0.033 | 0.061 | +0.72 | 0.534 |
| Investment prof. | (sep.) | 0.978 | -0.036 | 0.081 | (sep.) | 0.964 |
| Academic | +2.12 | 0.271 | +0.421 | 0.234 | +2.45 | 0.016 |
| Industry pract. | (sep.) | 0.982 | -0.041 | 0.102 | (sep.) | 0.966 |
| Student | +3.38 | 0.029 | +0.463 | 0.218 | +3.16 | 0.097 |
| log(words+1) | +0.44 | 0.250 | +0.015 | 0.291 | +0.52 | 0.007 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 181 | -22.77 | 0.232 |
| LPM   | 181   | (OLS) | R²=0.162, adj-R²=0.123 |
| Ordinal logit | 202 | -75.31 | 0.224 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -75.31
- Multinomial logit LL: -70.90
- LR = 2 × (-70.90 − -75.31) = 8.81, df = 8, p = 0.3585

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.3585 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Industry pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
