# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-07-01. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=2169 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=2169 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2213 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -8.66 | 0.000 | -0.051 | 0.004 | — | — |
| Accountant CPA | +0.62 | 0.586 | +0.017 | 0.611 | +1.27 | 0.027 |
| Issuer-current | +2.16 | 0.024 | +0.123 | 0.179 | +2.36 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.014 | 0.001 | +2.13 | 0.002 |
| Investment prof. | -0.13 | 0.905 | +0.000 | 0.989 | -0.18 | 0.817 |
| Academic | +0.09 | 0.940 | +0.122 | 0.271 | +0.53 | 0.461 |
| Industry pract. | +0.36 | 0.740 | +0.007 | 0.791 | +0.31 | 0.659 |
| Legal pract. | +1.19 | 0.375 | +0.083 | 0.393 | +0.69 | 0.551 |
| Trade assoc. | +1.33 | 0.234 | +0.275 | 0.150 | +0.88 | 0.381 |
| Student | +2.36 | 0.037 | +0.106 | 0.376 | +1.47 | 0.185 |
| log(words+1) | +0.90 | 0.000 | +0.015 | 0.001 | +0.87 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 2169 | -112.64 | 0.200 |
| LPM   | 2169   | (OLS) | R²=0.069, adj-R²=0.065 |
| Ordinal logit | 2213 | -287.80 | 0.193 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -287.80
- Multinomial logit LL: -280.53
- LR = 2 × (-280.53 − -287.80) = 14.53, df = 10, p = 0.1501

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1501 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 1 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
