# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-25. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=2119 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=2119 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2160 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -8.30 | 0.000 | -0.044 | 0.011 | — | — |
| Accountant CPA | +0.80 | 0.482 | +0.019 | 0.581 | +1.06 | 0.124 |
| Issuer-current | +2.30 | 0.014 | +0.124 | 0.173 | +2.42 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.013 | 0.001 | +2.16 | 0.001 |
| Investment prof. | +0.24 | 0.830 | +0.007 | 0.791 | +0.09 | 0.906 |
| Academic | +0.52 | 0.712 | +0.116 | 0.426 | +1.02 | 0.182 |
| Industry pract. | +0.52 | 0.636 | +0.009 | 0.740 | +0.39 | 0.572 |
| Legal pract. | +1.65 | 0.222 | +0.101 | 0.354 | +1.06 | 0.368 |
| Trade assoc. | +1.92 | 0.103 | +0.348 | 0.110 | +1.40 | 0.191 |
| Student | +2.45 | 0.030 | +0.108 | 0.368 | +1.52 | 0.173 |
| log(words+1) | +0.81 | 0.000 | +0.013 | 0.004 | +0.84 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 2119 | -106.58 | 0.189 |
| LPM   | 2119   | (OLS) | R²=0.071, adj-R²=0.066 |
| Ordinal logit | 2160 | -271.53 | 0.188 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -271.53
- Multinomial logit LL: -264.13
- LR = 2 × (-264.13 − -271.53) = 14.79, df = 10, p = 0.1398

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1398 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 1 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
