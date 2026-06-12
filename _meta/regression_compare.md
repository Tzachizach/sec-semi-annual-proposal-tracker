# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-12. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1015 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1015 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1046 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.14 | 0.000 | -0.020 | 0.252 | — | — |
| Accountant CPA | +1.70 | 0.123 | +0.039 | 0.421 | +1.61 | 0.017 |
| Issuer-current | +2.40 | 0.038 | +0.098 | 0.359 | +2.55 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.010 | 0.015 | +2.23 | 0.001 |
| Investment prof. | (sep.) | 1.000 | -0.012 | 0.028 | (sep.) | 0.966 |
| Academic | +1.81 | 0.238 | +0.171 | 0.322 | +1.99 | 0.013 |
| Industry pract. | +1.26 | 0.261 | +0.025 | 0.493 | +0.46 | 0.569 |
| Legal pract. | +4.81 | 0.001 | +0.490 | 0.172 | +4.39 | 0.008 |
| Trade assoc. | (sep.) | 1.000 | -0.017 | 0.046 | (sep.) | 0.907 |
| Student | +3.34 | 0.008 | +0.236 | 0.287 | +2.20 | 0.077 |
| log(words+1) | +0.55 | 0.063 | +0.007 | 0.146 | +0.70 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1015 | -56.91 | 0.182 |
| LPM   | 1015   | (OLS) | R²=0.084, adj-R²=0.075 |
| Ordinal logit | 1046 | -167.17 | 0.201 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -167.17
- Multinomial logit LL: -161.03
- LR = 2 × (-161.03 − -167.17) = 12.28, df = 10, p = 0.2666

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2666 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Trade assoc.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Trade assoc.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
