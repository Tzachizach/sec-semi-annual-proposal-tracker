# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-18. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1786 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1786 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1826 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.98 | 0.000 | -0.020 | 0.148 | — | — |
| Accountant CPA | +1.22 | 0.257 | +0.026 | 0.486 | +1.31 | 0.044 |
| Issuer-current | +2.12 | 0.056 | +0.078 | 0.377 | +2.48 | 0.000 |
| Issuer-former | (sep.) | 0.999 | -0.011 | 0.001 | +2.19 | 0.001 |
| Investment prof. | (sep.) | 1.000 | -0.013 | 0.002 | +0.09 | 0.931 |
| Academic | +1.70 | 0.233 | +0.170 | 0.326 | +2.07 | 0.007 |
| Industry pract. | +0.96 | 0.370 | +0.019 | 0.552 | +0.86 | 0.201 |
| Legal pract. | +2.72 | 0.016 | +0.130 | 0.330 | +1.79 | 0.111 |
| Trade assoc. | +2.70 | 0.055 | +0.306 | 0.259 | +1.87 | 0.158 |
| Student | +2.67 | 0.018 | +0.130 | 0.333 | +1.71 | 0.127 |
| log(words+1) | +0.54 | 0.025 | +0.007 | 0.053 | +0.67 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1786 | -100.53 | 0.120 |
| LPM   | 1786   | (OLS) | R²=0.044, adj-R²=0.039 |
| Ordinal logit | 1826 | -262.02 | 0.145 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -262.02
- Multinomial logit LL: -253.79
- LR = 2 × (-253.79 − -262.02) = 16.46, df = 10, p = 0.0873

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0873 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
