# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-15. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1171 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1171 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1205 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.93 | 0.000 | -0.019 | 0.254 | — | — |
| Accountant CPA | +1.48 | 0.173 | +0.034 | 0.449 | +1.41 | 0.033 |
| Issuer-current | +2.21 | 0.051 | +0.087 | 0.371 | +2.37 | 0.000 |
| Issuer-former | (sep.) | 0.999 | -0.011 | 0.006 | +2.05 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.013 | 0.013 | (sep.) | 0.999 |
| Academic | +1.75 | 0.242 | +0.170 | 0.324 | +1.79 | 0.024 |
| Industry pract. | +1.10 | 0.316 | +0.023 | 0.520 | +0.30 | 0.713 |
| Legal pract. | +3.57 | 0.003 | +0.239 | 0.275 | +2.65 | 0.029 |
| Trade assoc. | (sep.) | 1.000 | -0.018 | 0.027 | (sep.) | 0.980 |
| Student | +3.23 | 0.009 | +0.235 | 0.288 | +2.10 | 0.091 |
| log(words+1) | +0.53 | 0.058 | +0.007 | 0.126 | +0.74 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1171 | -68.78 | 0.143 |
| LPM   | 1171   | (OLS) | R²=0.055, adj-R²=0.047 |
| Ordinal logit | 1205 | -193.14 | 0.178 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -193.14
- Multinomial logit LL: -186.15
- LR = 2 × (-186.15 − -193.14) = 13.96, df = 10, p = 0.1747

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1747 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Trade assoc.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Trade assoc.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
