# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-26. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=2123 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=2123 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2164 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -8.39 | 0.000 | -0.047 | 0.007 | — | — |
| Accountant CPA | +0.74 | 0.515 | +0.018 | 0.589 | +1.05 | 0.126 |
| Issuer-current | +2.29 | 0.015 | +0.124 | 0.175 | +2.41 | 0.000 |
| Issuer-former | (sep.) | 0.906 | -0.013 | 0.001 | +2.16 | 0.001 |
| Investment prof. | +0.08 | 0.945 | +0.003 | 0.891 | -0.07 | 0.928 |
| Academic | +0.83 | 0.486 | +0.194 | 0.189 | +1.02 | 0.162 |
| Industry pract. | +0.50 | 0.648 | +0.009 | 0.755 | +0.37 | 0.593 |
| Legal pract. | +1.59 | 0.242 | +0.100 | 0.356 | +1.04 | 0.377 |
| Trade assoc. | +1.86 | 0.115 | +0.346 | 0.112 | +1.37 | 0.198 |
| Student | +2.44 | 0.031 | +0.107 | 0.370 | +1.51 | 0.174 |
| log(words+1) | +0.83 | 0.000 | +0.014 | 0.003 | +0.84 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 2123 | -107.86 | 0.206 |
| LPM   | 2123   | (OLS) | R²=0.081, adj-R²=0.077 |
| Ordinal logit | 2164 | -273.34 | 0.194 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -273.34
- Multinomial logit LL: -266.88
- LR = 2 × (-266.88 − -273.34) = 12.92, df = 10, p = 0.2283

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2283 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 1 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
