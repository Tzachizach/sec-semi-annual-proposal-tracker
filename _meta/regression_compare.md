# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-08. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=777 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=777 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=802 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.25 | nan | -0.026 | 0.212 | — | — |
| Accountant CPA | +1.58 | nan | +0.048 | 0.431 | +1.76 | nan |
| Issuer-current | +2.38 | nan | +0.147 | 0.349 | +2.70 | nan |
| Issuer-former | (sep.) | nan | -0.015 | 0.015 | +2.13 | nan |
| Investment prof. | (sep.) | nan | -0.016 | 0.022 | (sep.) | nan |
| Academic | +1.83 | nan | +0.215 | 0.300 | +2.16 | nan |
| Industry pract. | (sep.) | nan | -0.017 | 0.025 | -0.37 | nan |
| Legal pract. | (sep.) | nan | +0.992 | 0.000 | (sep.) | nan |
| Trade assoc. | +0.00 | nan | +0.000 | 0.089 | +0.00 | nan |
| Student | +3.46 | nan | +0.315 | 0.260 | +2.68 | nan |
| log(words+1) | +0.64 | nan | +0.009 | 0.114 | +0.78 | nan |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 777 | -47.65 | 0.231 |
| LPM   | 777   | (OLS) | R²=0.149, adj-R²=0.139 |
| Ordinal logit | 802 | -128.13 | 0.261 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -128.13
- Multinomial logit LL: -121.82
- LR = 2 × (-121.82 − -128.13) = 12.62, df = 10, p = 0.2454

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2454 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.', 'Legal pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
