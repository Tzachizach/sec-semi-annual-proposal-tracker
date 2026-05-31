# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-05-31. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=430 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=430 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=455 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.94 | 0.000 | -0.039 | 0.132 | — | — |
| Accountant CPA | +1.55 | 0.173 | +0.057 | 0.443 | +1.65 | 0.020 |
| Issuer-current | +2.09 | 0.094 | +0.168 | 0.373 | +2.40 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.022 | 0.017 | +1.81 | 0.036 |
| Investment prof. | (sep.) | 1.000 | -0.025 | 0.029 | (sep.) | 0.996 |
| Academic | +1.59 | 0.320 | +0.275 | 0.292 | +2.09 | 0.016 |
| Industry pract. | (sep.) | 1.000 | -0.029 | 0.034 | -0.56 | 0.621 |
| Student | +3.04 | 0.024 | +0.305 | 0.283 | +2.22 | 0.113 |
| log(words+1) | +0.66 | 0.028 | +0.014 | 0.070 | +0.70 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 430 | -38.18 | 0.196 |
| LPM   | 430   | (OLS) | R²=0.093, adj-R²=0.076 |
| Ordinal logit | 455 | -111.07 | 0.230 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -111.07
- Multinomial logit LL: -105.45
- LR = 2 × (-105.45 − -111.07) = 11.24, df = 8, p = 0.1882

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.1882 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
