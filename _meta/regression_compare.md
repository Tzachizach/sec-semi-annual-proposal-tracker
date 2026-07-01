# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-07-01. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=2172 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=2172 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2216 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -8.66 | 0.000 | -0.051 | 0.004 | — | — |
| Accountant CPA | +0.63 | 0.583 | +0.017 | 0.610 | +1.28 | 0.026 |
| Issuer-current | +2.17 | 0.024 | +0.123 | 0.179 | +2.36 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.014 | 0.001 | +2.13 | 0.001 |
| Investment prof. | -0.13 | 0.908 | +0.000 | 0.987 | -0.18 | 0.820 |
| Academic | +0.09 | 0.936 | +0.122 | 0.270 | +0.53 | 0.457 |
| Industry pract. | +0.37 | 0.737 | +0.007 | 0.789 | +0.31 | 0.655 |
| Legal pract. | +1.20 | 0.373 | +0.083 | 0.393 | +0.70 | 0.549 |
| Trade assoc. | +1.34 | 0.232 | +0.275 | 0.150 | +0.88 | 0.379 |
| Student | +2.37 | 0.036 | +0.106 | 0.376 | +1.48 | 0.184 |
| log(words+1) | +0.90 | 0.000 | +0.015 | 0.002 | +0.87 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 2172 | -112.68 | 0.200 |
| LPM   | 2172   | (OLS) | R²=0.069, adj-R²=0.065 |
| Ordinal logit | 2216 | -287.90 | 0.193 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -287.90
- Multinomial logit LL: -280.63
- LR = 2 × (-280.63 − -287.90) = 14.53, df = 10, p = 0.1502

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1502 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 1 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
