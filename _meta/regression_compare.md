# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-17. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1494 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1494 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1532 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.12 | 0.000 | -0.024 | 0.115 | — | — |
| Accountant CPA | +1.27 | 0.236 | +0.029 | 0.483 | +1.36 | 0.037 |
| Issuer-current | +2.04 | 0.069 | +0.085 | 0.382 | +2.37 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.012 | 0.001 | +2.05 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.015 | 0.002 | (sep.) | 0.943 |
| Academic | +1.39 | 0.339 | +0.165 | 0.339 | +1.81 | 0.021 |
| Industry pract. | +0.80 | 0.463 | +0.017 | 0.596 | +0.67 | 0.324 |
| Legal pract. | +3.45 | 0.004 | +0.237 | 0.278 | +2.66 | 0.027 |
| Trade assoc. | +2.44 | 0.086 | +0.301 | 0.266 | +1.61 | 0.229 |
| Student | +2.52 | 0.026 | +0.128 | 0.342 | +1.56 | 0.166 |
| log(words+1) | +0.61 | 0.016 | +0.009 | 0.041 | +0.71 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1494 | -92.07 | 0.133 |
| LPM   | 1494   | (OLS) | R²=0.052, adj-R²=0.046 |
| Ordinal logit | 1532 | -238.98 | 0.159 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -238.98
- Multinomial logit LL: -231.09
- LR = 2 × (-231.09 − -238.98) = 15.78, df = 10, p = 0.1062

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1062 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
