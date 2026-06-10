# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-10. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=803 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=803 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=828 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.30 | nan | -0.025 | 0.212 | — | — |
| Accountant CPA | +1.62 | nan | +0.048 | 0.426 | +1.80 | nan |
| Issuer-current | +2.41 | nan | +0.148 | 0.346 | +2.73 | nan |
| Issuer-former | (sep.) | nan | -0.014 | 0.015 | +2.16 | nan |
| Investment prof. | (sep.) | nan | -0.015 | 0.023 | (sep.) | nan |
| Academic | +1.85 | nan | +0.216 | 0.298 | +2.18 | nan |
| Industry pract. | (sep.) | nan | -0.016 | 0.024 | -0.37 | nan |
| Legal pract. | (sep.) | nan | +0.992 | 0.000 | (sep.) | nan |
| Trade assoc. | +0.00 | nan | -0.000 | 0.792 | +0.00 | nan |
| Student | +3.49 | nan | +0.316 | 0.259 | +2.71 | nan |
| log(words+1) | +0.64 | nan | +0.009 | 0.115 | +0.79 | nan |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 803 | -47.90 | 0.232 |
| LPM   | 803   | (OLS) | R²=0.149, adj-R²=0.139 |
| Ordinal logit | 828 | -128.76 | 0.262 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -128.76
- Multinomial logit LL: -122.43
- LR = 2 × (-122.43 − -128.76) = 12.67, df = 10, p = 0.2430

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2430 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.', 'Legal pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
