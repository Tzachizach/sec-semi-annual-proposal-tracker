# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-03. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=586 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=586 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=611 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -6.31 | 0.000 | -0.024 | 0.324 | — | — |
| Accountant CPA | +1.58 | 0.156 | +0.059 | 0.426 | +1.83 | 0.009 |
| Issuer-current | +2.23 | 0.069 | +0.173 | 0.352 | +2.56 | 0.000 |
| Issuer-former | (sep.) | 1.000 | -0.019 | 0.008 | +1.98 | 0.020 |
| Investment prof. | (sep.) | 0.999 | -0.021 | 0.014 | (sep.) | 0.985 |
| Academic | +1.99 | 0.205 | +0.288 | 0.275 | +2.24 | 0.009 |
| Industry pract. | (sep.) | 1.000 | -0.024 | 0.023 | -0.35 | 0.757 |
| Student | +3.12 | 0.018 | +0.309 | 0.271 | +2.41 | 0.083 |
| log(words+1) | +0.51 | 0.077 | +0.010 | 0.143 | +0.69 | 0.000 |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 586 | -49.72 | 0.151 |
| LPM   | 586   | (OLS) | R²=0.075, adj-R²=0.062 |
| Ordinal logit | 611 | -126.64 | 0.223 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -126.64
- Multinomial logit LL: -119.37
- LR = 2 × (-119.37 − -126.64) = 14.54, df = 8, p = 0.0686

Under H0 (proportional odds holds), LR follows χ²(8). p = 0.0686 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 3 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
