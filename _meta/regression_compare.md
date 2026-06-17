# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-17. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=1645 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=1645 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=1685 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.23 | 0.000 | -0.022 | 0.116 | — | — |
| Accountant CPA | +1.38 | 0.199 | +0.030 | 0.464 | +1.45 | 0.025 |
| Issuer-current | +2.07 | 0.063 | +0.077 | 0.381 | +2.41 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.011 | 0.001 | +2.13 | 0.002 |
| Investment prof. | (sep.) | 1.000 | -0.013 | 0.002 | +0.02 | 0.983 |
| Academic | +1.50 | 0.303 | +0.168 | 0.332 | +1.96 | 0.012 |
| Industry pract. | +0.90 | 0.404 | +0.019 | 0.565 | +0.77 | 0.252 |
| Legal pract. | +3.55 | 0.003 | +0.239 | 0.275 | +2.72 | 0.025 |
| Trade assoc. | +2.54 | 0.073 | +0.304 | 0.262 | +1.76 | 0.186 |
| Student | +2.63 | 0.021 | +0.129 | 0.336 | +1.66 | 0.138 |
| log(words+1) | +0.61 | 0.016 | +0.008 | 0.043 | +0.69 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 1645 | -93.53 | 0.135 |
| LPM   | 1645   | (OLS) | R²=0.052, adj-R²=0.046 |
| Ordinal logit | 1685 | -252.31 | 0.151 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -252.31
- Multinomial logit LL: -244.44
- LR = 2 × (-244.44 − -252.31) = 15.75, df = 10, p = 0.1072

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.1072 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 2 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: [].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
