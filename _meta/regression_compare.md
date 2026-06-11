# SEC S7-2026-15 — regression spec comparison

_Last run: 2026-06-11. Three specs on the same predictor set, different outcomes._

## Specifications

| Spec | Outcome | Sample | Estimator |
|---|---|---|---|
| Logit (baseline) | Support=1 / Oppose=0 | N=841 | MLE logit |
| LPM (OLS) | Support=1 / Oppose=0 | N=841 | OLS, HC1 robust SE |
| Ordinal logit | Oppose=0 < Conditional=1 < Support=2 | N=866 | proportional-odds logit |

Predictors in all three: 7 entity dummies (reference Individual) + log(words+1).

## Side-by-side coefficients

| Variable | Logit β | Logit p | LPM β | LPM p | Ord. β | Ord. p |
|---|---:|---:|---:|---:|---:|---:|
| Constant | -7.34 | nan | -0.024 | 0.219 | — | — |
| Accountant CPA | +1.63 | nan | +0.046 | 0.425 | +1.81 | nan |
| Issuer-current | +2.48 | nan | +0.149 | 0.342 | +2.79 | nan |
| Issuer-former | (sep.) | nan | -0.013 | 0.015 | +2.23 | nan |
| Investment prof. | (sep.) | nan | -0.014 | 0.023 | (sep.) | nan |
| Academic | +1.93 | nan | +0.218 | 0.295 | +2.24 | nan |
| Industry pract. | (sep.) | nan | -0.015 | 0.024 | -0.29 | nan |
| Legal pract. | (sep.) | nan | +0.993 | 0.000 | (sep.) | nan |
| Trade assoc. | +0.00 | nan | -0.000 | 0.055 | +0.00 | nan |
| Student | +3.55 | nan | +0.317 | 0.257 | +2.75 | nan |
| log(words+1) | +0.63 | nan | +0.009 | 0.120 | +0.79 | nan |

## Fit statistics

| Spec | N | LL | McFadden R² / R² |
|---|---:|---:|---:|
| Logit | 841 | -48.37 | 0.231 |
| LPM   | 841   | (OLS) | R²=0.149, adj-R²=0.139 |
| Ordinal logit | 866 | -129.96 | 0.262 |

## Proportional-odds assumption (LR test)

Compared the ordinal logit (restricted, single slope vector) against an unrestricted multinomial logit with the same predictors.

- Ordinal logit LL: -129.96
- Multinomial logit LL: -123.62
- LR = 2 × (-123.62 − -129.96) = 12.69, df = 10, p = 0.2416

Under H0 (proportional odds holds), LR follows χ²(10). p = 0.2416 → do not reject proportional-odds. Note: small-N artifact warning — the LR test has low power with the current Support count.

## Notes on separation

Binary specs (Logit, LPM): 4 entity buckets carry zero Support letters and are flagged separated: ['Issuer-former', 'Investment prof.', 'Industry pract.', 'Legal pract.'].
Ordinal spec: separation is defined differently — a bucket with all letters in one ordinal class. 
Buckets with single-class variation only: ['Investment prof.', 'Legal pract.'].

## Reproducibility

Source data: `_meta/renumbered_records.json`.
Estimators: `statsmodels` Logit / OLS (HC1) / OrderedModel / MNLogit.
