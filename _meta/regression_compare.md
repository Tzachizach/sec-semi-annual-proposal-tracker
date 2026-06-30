# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-30. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=2125 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=2125 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=2166 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -8.31 | 0.000 | -0.045 | 0.008 | — | — |
| Accountant CPA | +0.79 | 0.484 | +0.019 | 0.586 | +1.07 | 0.118 |
| Issuer-current | +2.29 | 0.015 | +0.124 | 0.174 | +2.43 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.013 | 0.001 | +2.16 | 0.001 |
| Investment prof. | +0.09 | 0.934 | +0.004 | 0.881 | -0.05 | 0.953 |
| Academic | +0.55 | 0.646 | +0.164 | 0.221 | +0.82 | 0.263 |
| Industry pract. | +0.51 | 0.639 | +0.009 | 0.749 | +0.40 | 0.567 |
| Legal pract. | +1.64 | 0.224 | +0.101 | 0.355 | +1.06 | 0.369 |
| Trade assoc. | +1.91 | 0.104 | +0.347 | 0.111 | +1.42 | 0.183 |
| Student | +2.45 | 0.030 | +0.108 | 0.369 | +1.52 | 0.170 |
| log(words+1) | +0.81 | 0.000 | +0.014 | 0.003 | +0.83 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 2125 | -108.47 | 0.202 |
| LPM   | 2125   | (OLS) | R²=0.079, adj-R²=0.074 |
| Ordinal logit | 2166 | -274.74 | 0.190 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -274.74
- Multinomial logit LL: -268.44
- LR = 2 × (-268.44 − -274.74) = 12.58, df = 10, p = 0.2479

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2479 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 1 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
