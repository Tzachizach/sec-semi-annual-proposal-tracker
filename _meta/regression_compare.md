# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-02. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=461 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=461 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=486 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.22 | 0.000 | -0.039 | 0.128 | — | — |
| Accountant CPA | +1.61 | 0.157 | +0.058 | 0.431 | +1.73 | 0.015 |
| Issuer-current | +2.11 | 0.092 | +0.169 | 0.367 | +2.45 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.021 | 0.018 | +1.88 | 0.029 |
| Investment prof. | (sep.) | 1.000 | -0.023 | 0.029 | (sep.) | 0.983 |
| Academic | +1.54 | 0.351 | +0.277 | 0.288 | +2.09 | 0.017 |
| Industry pract. | (sep.) | 1.000 | -0.027 | 0.035 | -0.54 | 0.632 |
| Student | +3.08 | 0.023 | +0.307 | 0.279 | +2.28 | 0.105 |
| log(words+1) | +0.70 | 0.028 | +0.014 | 0.070 | +0.74 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 461 | -38.53 | 0.201 |
| LPM   | 461   | (OLS) | R²=0.094, adj-R²=0.078 |
| Ordinal logit | 486 | -111.63 | 0.239 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -111.63
- Multinomial logit LL: -105.76
- LR = 2 × (-105.76 − -111.63) = 11.74, df = 8, p = 0.1632

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.1632 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
