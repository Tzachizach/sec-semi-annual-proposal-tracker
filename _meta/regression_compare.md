# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-16. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1296 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1296 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1331 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.94 | 0.000 | -0.019 | 0.223 | — | — |
| Accountant CPA | +1.45 | 0.181 | +0.032 | 0.454 | +1.41 | 0.032 |
| Issuer-current | +2.21 | 0.050 | +0.087 | 0.370 | +2.40 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.011 | 0.004 | +2.08 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.013 | 0.007 | (sep.) | 0.996 |
| Academic | +1.73 | 0.243 | +0.170 | 0.325 | +1.85 | 0.019 |
| Industry pract. | +1.10 | 0.313 | +0.023 | 0.520 | +0.34 | 0.677 |
| Legal pract. | +3.57 | 0.003 | +0.239 | 0.275 | +2.68 | 0.027 |
| Trade assoc. | (sep.) | 0.961 | -0.018 | 0.018 | (sep.) | 0.920 |
| Student | +3.04 | 0.011 | +0.187 | 0.305 | +1.97 | 0.098 |
| log(words+1) | +0.53 | 0.048 | +0.007 | 0.101 | +0.72 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1296 | -74.73 | 0.133 |
| LPM   | 1296   | (OLS) | R²=0.048, adj-R²=0.041 |
| Ordinal logit | 1331 | -205.69 | 0.171 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -205.69
- Multinomial logit LL: -198.67
- LR = 2 × (-198.67 − -205.69) = 14.04, df = 10, p = 0.1711

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1711 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Trade assoc.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Trade assoc.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
