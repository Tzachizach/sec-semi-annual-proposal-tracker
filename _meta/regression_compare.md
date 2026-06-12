# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-12. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1077 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1077 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1109 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.75 | 0.000 | -0.019 | 0.272 | — | — |
| Accountant CPA | +1.47 | 0.175 | +0.035 | 0.451 | +1.47 | 0.027 |
| Issuer-current | +2.14 | 0.059 | +0.086 | 0.375 | +2.41 | 0.000 |
| Issuer-former | (sep.) | 0.999 | -0.011 | 0.006 | +2.14 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.014 | 0.012 | (sep.) | 0.952 |
| Academic | +1.75 | 0.237 | +0.169 | 0.327 | +1.92 | 0.016 |
| Industry pract. | +1.04 | 0.346 | +0.022 | 0.535 | +0.36 | 0.657 |
| Legal pract. | +4.60 | 0.002 | +0.488 | 0.173 | +4.26 | 0.009 |
| Trade assoc. | (sep.) | 0.959 | -0.019 | 0.026 | (sep.) | 0.896 |
| Student | +3.18 | 0.010 | +0.234 | 0.290 | +2.13 | 0.085 |
| log(words+1) | +0.51 | 0.067 | +0.007 | 0.131 | +0.69 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1077 | -67.20 | 0.149 |
| LPM   | 1077   | (OLS) | R²=0.071, adj-R²=0.063 |
| Ordinal logit | 1109 | -183.12 | 0.182 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -183.12
- Multinomial logit LL: -176.46
- LR = 2 × (-176.46 − -183.12) = 13.32, df = 10, p = 0.2061

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2061 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Trade assoc.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Trade assoc.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
