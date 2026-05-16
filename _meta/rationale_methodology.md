# Rationale classification methodology — S7-2026-15 comment-letter tracker

## Why three raters

Rationale coding is a **multi-label** problem: each letter can invoke any subset of the 20 codes in `_meta/rationale_taxonomy.md`. Some codes are surface-readable (NR, LE — usually obvious from the text). Others require inference about what the writer's framing implies (IP vs IA, US vs MF, RI vs CC). A single LLM pass collapses both into one decision and hides the inferential judgment.

To bracket the reasonable range, we run three independent LLM passes with deliberately different rubric priors, then aggregate. This mirrors the stance and entity ensembles already on the project (see `_meta/methodology.md` and `_meta/entity_methodology.md`).

The accounting and management-research literature on LLM annotation — Carlson & Burbano (*SMJ* 2026); Liu (*Computers in Human Behavior* 2026); Tornberg (2024); the *Frontiers in Social Psychology* 2025 validation paper — recommends this design: multiple prompt variants, per-label agreement, uncertainty reporting. The direct accounting-research precedent on classifying SEC comment letters is Bochkay, Brown, Leone & Tucker (*Review of Accounting Studies* 2021).

## The three rubrics (all LLM passes on Claude Opus 4.7)

**Rater 1 — Primary (balanced).** Reads each letter holistically and codes the rationale families the writer *substantively argues*. Codes a family if the writer makes the argument, even if they don't use the SEC's canonical framing. This is the rater that has been running since the tracker launched and underlies the existing `rationales_primary` field.

**Rater 2 — Literalist (conservative default).** Codes a family **only** when the letter's text explicitly invokes that family's framing. Requires surface evidence — words, phrases, or unmistakable conceptual moves that map directly to the code. If the connection is by inference, the code is dropped. Will produce shorter code lists; tends to under-code commenter-distinctive families (IP, US, RI) where they appear by implication only.

**Rater 3 — Inclusive (expansive default).** Codes a family whenever the writer **plausibly invokes** it — including allusive references, one-line gestures, and arguments the writer relies on but doesn't fully develop. Will produce longer code lists; tends to over-code (especially IP, IA, MF) where canonical concepts are alluded to without full development.

The three rubrics deliberately bracket the inferential spectrum. Literalist and Inclusive are opposing priors; letters where they agree are robust, and letters where they disagree are the genuinely-hard inferential cases.

## Aggregation

Per (letter, code) pair, the **majority vote** rule: a code is in the letter's `rationales_majority` list if ≥ 2 of the 3 raters assign it. The `rationales` field exposed publicly is `rationales_majority`.

This is the standard aggregation for multi-label annotation. It is not "majority of any one letter's rationale set" — that's the wrong unit. The unit is the (letter, code) pair.

## Agreement statistics (N = 137)

**Per-letter set-level agreement:**
- 75 unanimous (all three raters produce the same code set) — 54.7%
- 54 majority (≥ 2 raters produce the same code set) — 39.4%
- 8 split (all three raters produce different code sets) — 5.8%

**Per-code Cohen's κ** (binary code-present vs code-absent across 137 letters, mean of pairwise):

| Code | mean κ | Frequencies (P, L, I) | Notes |
|---|---:|---:|---|
| ICc | 1.00 | 6, 6, 6 | Perfect agreement; surface-readable |
| CC | 1.00 | 0, 0, 0 | No commenter cites — natural ceiling |
| ICs | 1.00 | 3, 3, 3 | Perfect agreement |
| US | 0.94 | 19, 20, 22 | Strong |
| FR | 0.93 | 35, 37, 41 | Strong |
| AL | 0.92 | 18, 20, 22 | Strong |
| IA | 0.90 | 34, 34, 41 | Strong |
| OP | 0.88 | 6, 5, 7 | Strong |
| LE | 0.88 | 5, 7, 7 | Strong |
| NR | 0.88 | 10, 10, 7 | Strong |
| EX | 0.86 | 7, 6, 9 | Strong |
| ST | 0.86 | 13, 16, 19 | Strong |
| IP | 0.85 | 91, 88, 99 | Strong (most-cited code) |
| MF | 0.85 | 23, 25, 33 | Strong |
| AU | 0.81 | 7, 7, 12 | Strong; Inclusive picks up CPA-letter implicit AU |
| CB | 0.78 | 16, 19, 28 | Strong; Inclusive picks up cost-mentions |
| RI | 0.75 | 9, 12, 18 | Moderate; the most inferential commenter-distinctive code |
| CMP | 0.71 | 6, 6, 12 | Moderate; Inclusive picks up granularity-by-implication |
| SG | 0.33 | 0, 0, 1 | Floor (SEC-engaged code, commenters rarely cite) |
| OV | 0.22 | 0, 1, 2 | Floor (SEC-engaged code, commenters rarely cite) |

**Mean per-code κ across pairs: 0.818** — substantial agreement, comparable to the 0.8+ range that recent LLM-annotation validation studies report for best-prompt agreement against expert consensus (e.g., the *Frontiers in Social Psychology* 2025 paper reports 94% F1 with expert consensus on best-performing prompts).

## Diagnostic value

A high-κ code (e.g., ICc, US, FR, AL) is one all three raters agree on — likely a surface-readable or canonical code where the text speaks for itself. A lower-κ code (RI, CMP) is one where the raters split — likely an inferential code where reasonable LLM readings can diverge.

The per-code κ table makes the inferential structure of the taxonomy visible to readers. The two codes at floor (SG, OV) are codes the SEC engages in its own economic analysis but no commenter actually cites — they are correctly absent in nearly every reading.

## Model sensitivity caveat

All three raters are independent passes of **Claude Opus 4.7** with three different rubric system prompts. This is an **intra-model multi-prompt ensemble** — it measures variance across rubric priors holding the model constant. Agreement statistics here are conditional on the model, not robust across model families.

A model-family-robust agreement signal would require running the same three rubrics through at least one other model family (GPT-4-class, Gemini, or Llama) and comparing. That work is parked as a methodological follow-up; see STATUS.md §6.7. Carlson & Burbano (*SMJ* 2026) recommend multi-model ensembles where feasible.

The takeaway from the literature comparison: the 0.818 κ here is what a careful single-model multi-prompt ensemble can achieve on a hard multi-label policy-text task; it's not a substitute for cross-model validation, but it is a substantial improvement over single-pass classification.

## Reproducibility

Outputs (all under `_meta/`):
- `rationale_primary.json` — canonical primary classifications, stable across re-runs
- `rationale_rater_literalist.json` — LLM Literalist call + evidence string per letter
- `rationale_rater_inclusive.json` — LLM Inclusive call + evidence string per letter
- `rationale_three_rater.json` — merged with majority + per-letter agreement flag + per-code κ table
- `renumbered_records.json` — each record carries `rationales_primary`, `rationales_literalist`, `rationales_inclusive`, `rationales_majority` (= the public `rationales`), and `rationale_agreement` ("unanimous" / "majority" / "split")

Run `python3 _scripts/aggregate_rationale_ensemble.py` to recompute the majority + κ from the three rater files.

The 20-code taxonomy is in `_meta/rationale_taxonomy.md`. Source references for the multi-prompt-ensemble approach are in `_meta/methodology_papers/INDEX.md`.

## Future direction: human–LLM annotation comparison

A research project parked for follow-up: extend the dev-mirror voting widget to let crowd raters tag letters with rationale codes, producing parallel human and LLM annotations on the same letters. The comparison would address a thin literature on regulatory-text annotation, where the existing precedents (CHI 2024 GPT-4-vs-MTurk; Capturing Perspectives of Crowdsourced Annotators) do not sit at the intersection of (multi-label policy-text classification) × (LLM ensemble) × (crowd annotator perspective).
