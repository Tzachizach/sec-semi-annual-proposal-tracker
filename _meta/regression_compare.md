# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-22. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1920 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1920 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1961 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.09 | 0.000 | -0.018 | 0.146 | — | — |
| Accountant CPA | +1.25 | 0.245 | +0.026 | 0.479 | +1.39 | 0.032 |
| Issuer-current | +2.04 | 0.062 | +0.065 | 0.384 | +2.73 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.011 | 0.001 | +2.13 | 0.001 |
| Investment prof. | (sep.) | 1.000 | -0.011 | 0.002 | +0.10 | 0.923 |
| Academic | +1.74 | 0.225 | +0.172 | 0.322 | +2.31 | 0.002 |
| Industry pract. | +0.89 | 0.406 | +0.016 | 0.562 | +0.87 | 0.185 |
| Legal pract. | +2.58 | 0.021 | +0.113 | 0.341 | +1.66 | 0.133 |
| Trade assoc. | +2.74 | 0.052 | +0.308 | 0.256 | +2.08 | 0.116 |
| Student | +2.51 | 0.025 | +0.112 | 0.346 | +1.57 | 0.155 |
| log(words+1) | +0.55 | 0.024 | +0.007 | 0.053 | +0.60 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1920 | -102.10 | 0.118 |
| LPM   | 1920   | (OLS) | R²=0.042, adj-R²=0.037 |
| Ordinal logit | 1961 | -269.88 | 0.143 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -269.88
- Multinomial logit LL: -261.84
- LR = 2 × (-261.84 − -269.88) = 16.08, df = 10, p = 0.0974

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.0974 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
