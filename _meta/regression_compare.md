# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-05. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=659 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=659 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=684 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.86 | 0.000 | -0.025 | 0.257 | — | — |
| Accountant CPA | +1.52 | 0.174 | +0.050 | 0.438 | +1.70 | nan |
| Issuer-current | +2.42 | 0.051 | +0.177 | 0.339 | +2.72 | nan |
| Issuer-former | (sep.) | 1.000 | -0.016 | 0.014 | +2.00 | nan |
| Investment prof. | (sep.) | 1.000 | -0.017 | 0.021 | (sep.) | nan |
| Academic | +1.82 | 0.227 | +0.213 | 0.305 | +2.15 | nan |
| Industry pract. | (sep.) | 1.000 | -0.020 | 0.029 | -0.28 | nan |
| Legal pract. | (sep.) | 0.999 | +0.990 | 0.000 | (sep.) | nan |
| Student | +3.34 | 0.012 | +0.313 | 0.264 | +2.56 | nan |
| log(words+1) | +0.58 | 0.055 | +0.010 | 0.130 | +0.72 | nan |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 659 | -46.48 | 0.225 |
| LPM   | 659   | (OLS) | R²=0.151, adj-R²=0.139 |
| Ordinal logit | 684 | -125.21 | 0.251 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -125.21
- Multinomial logit LL: -118.98
- LR = 2 × (-118.98 − -125.21) = 12.46, df = 9, p = 0.1886

Under H0 (proportional odds holds), LR follows χ²(9). p = 0.1886 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.', 'Legal pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
