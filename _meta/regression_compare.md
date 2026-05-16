# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-16. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=164 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=164 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=182 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -5.16 | 0.005 | -0.029 | 0.573 | — | — |
| Accountant CPA | (sep.) | 0.962 | -0.032 | 0.058 | +0.85 | 0.325 |
| Issuer-current | +1.69 | 0.185 | +0.154 | 0.429 | +1.82 | 0.011 |
| Issuer-former | (sep.) | 0.957 | -0.036 | 0.058 | +0.61 | 0.597 |
| Investment prof. | (sep.) | 0.977 | -0.038 | 0.076 | (sep.) | 0.956 |
| Academic | +2.14 | 0.265 | +0.418 | 0.239 | +1.02 | 0.363 |
| Industry pract. | (sep.) | 0.983 | -0.043 | 0.099 | (sep.) | 0.961 |
| Student | +3.29 | 0.033 | +0.460 | 0.222 | +3.01 | 0.131 |
| log(words+1) | +0.40 | 0.294 | +0.015 | 0.323 | +0.72 | 0.001 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 164 | -22.42 | 0.225 |
| LPM   | 164   | (OLS) | R²=0.160, adj-R²=0.116 |
| Ordinal logit | 182 | -69.34 | 0.209 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -69.34
- Multinomial logit LL: -65.54
- LR = 2 × (-65.54 − -69.34) = 7.61, df = 8, p = 0.4728

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.4728 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Industry pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
