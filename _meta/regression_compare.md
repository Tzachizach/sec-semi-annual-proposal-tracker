# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-19. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=238 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=238 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=261 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.02 | 0.000 | -0.036 | 0.320 | — | — |
| Accountant CPA | +1.57 | 0.183 | +0.069 | 0.433 | +1.48 | 0.043 |
| Issuer-current | +1.99 | 0.119 | +0.164 | 0.392 | +2.22 | 0.001 |
| Issuer-former | (sep.) | 1.000 | -0.025 | 0.055 | +0.76 | 0.500 |
| Investment prof. | (sep.) | 1.000 | -0.029 | 0.076 | (sep.) | 0.935 |
| Academic | +2.22 | 0.242 | +0.429 | 0.220 | +2.45 | 0.018 |
| Industry pract. | (sep.) | 1.000 | -0.028 | 0.077 | -0.46 | 0.687 |
| Student | +3.66 | 0.019 | +0.470 | 0.208 | +3.35 | 0.086 |
| log(words+1) | +0.50 | 0.156 | +0.014 | 0.189 | +0.61 | 0.001 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 238 | -27.04 | 0.227 |
| LPM   | 238   | (OLS) | R²=0.150, adj-R²=0.121 |
| Ordinal logit | 261 | -87.17 | 0.227 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -87.17
- Multinomial logit LL: -82.60
- LR = 2 × (-82.60 − -87.17) = 9.14, df = 8, p = 0.3309

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.3309 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): the same 4 entity buckets carry zero Support letters and are flagged separated — Accountant CPA, Issuer-former, Investment professional, Industry practitioner.
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
