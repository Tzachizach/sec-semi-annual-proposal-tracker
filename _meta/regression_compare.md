# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-31. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=284 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=284 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=309 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.51 | 0.000 | -0.055 | 0.133 | — | — |
| Accountant CPA | +1.35 | 0.242 | +0.062 | 0.475 | +1.44 | 0.047 |
| Issuer-current | +1.62 | 0.194 | +0.151 | 0.433 | +1.97 | 0.003 |
| Issuer-former | (sep.) | 1.000 | -0.034 | 0.015 | +1.36 | 0.116 |
| Investment prof. | (sep.) | 1.000 | -0.037 | 0.028 | (sep.) | 0.929 |
| Academic | +1.11 | 0.491 | +0.246 | 0.337 | +1.68 | 0.054 |
| Industry pract. | (sep.) | 0.998 | -0.044 | 0.029 | -0.99 | 0.380 |
| Student | +3.42 | 0.031 | +0.459 | 0.223 | +3.21 | 0.098 |
| log(words+1) | +0.66 | 0.032 | +0.021 | 0.063 | +0.69 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 284 | -34.62 | 0.200 |
| LPM   | 284   | (OLS) | R²=0.112, adj-R²=0.086 |
| Ordinal logit | 309 | -102.18 | 0.215 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -102.18
- Multinomial logit LL: -96.89
- LR = 2 × (-96.89 − -102.18) = 10.58, df = 8, p = 0.2266

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.2266 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
