# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-18. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=203 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=203 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=224 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -5.66 | 0.002 | -0.031 | 0.461 | — | — |
| Accountant CPA | (sep.) | 0.963 | -0.024 | 0.058 | +0.88 | 0.295 |
| Issuer-current | +1.85 | 0.148 | +0.161 | 0.405 | +2.20 | 0.001 |
| Issuer-former | (sep.) | 0.954 | -0.030 | 0.065 | +0.84 | 0.468 |
| Investment prof. | (sep.) | 0.979 | -0.032 | 0.085 | (sep.) | 0.968 |
| Academic | +2.17 | 0.262 | +0.427 | 0.226 | +2.53 | 0.014 |
| Industry pract. | (sep.) | 0.982 | -0.037 | 0.105 | (sep.) | 0.969 |
| Student | +3.50 | 0.024 | +0.466 | 0.212 | +3.29 | 0.087 |
| log(words+1) | +0.46 | 0.219 | +0.014 | 0.269 | +0.54 | 0.005 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 203 | -23.27 | 0.236 |
| LPM   | 203   | (OLS) | R²=0.163, adj-R²=0.129 |
| Ordinal logit | 224 | -76.80 | 0.233 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -76.80
- Multinomial logit LL: -72.29
- LR = 2 × (-72.29 − -76.80) = 9.01, df = 8, p = 0.3412

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.3412 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Industry pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
