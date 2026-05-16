# SEC S7-2026-15 — Public comment letter tracker

A live tracker for the public comment letters submitted on the SEC's proposed rule **S7-2026-15** (Optional Semiannual Reporting by Public Companies). The proposal would let public companies switch from quarterly (Form 10-Q) to semi-annual financial reporting (a new Form 10-S). The 60-day comment period opened in May 2026.

**Live site:** <https://tzachizach.github.io/sec-semi-annual-proposal-tracker/>

This project is produced by [Professor Tzachi Zach](https://fisher.osu.edu/people/zach.7) at The Ohio State University Fisher College of Business as a public service. The two goals beyond the tracker itself: I hope it will encourage discussion among accounting academics about the proposal, and it is quite interesting to test how well language-model classifiers handle regulatory text at scale.

---

## What the site shows

At every page load, the dashboard renders:

- Headline counts of Oppose / Conditional / Support letters, with percentages
- Letters per day, stacked by stance
- Stance totals as a horizontal bar
- Letter counts by entity type and by word-count bucket
- A three-specification regression panel — Logit, Ordinal Logit, and Linear Probability Model — testing whether stance varies systematically with commenter type or letter length
- The 20-code rationale taxonomy anchored on the SEC's proposing release, with per-code citation counts and a stacked-by-stance breakdown
- A searchable, date-grouped table of every letter, with per-row stance and entity agreement badges and the rationale codes the letter invoked

---

## Methodology in one paragraph

Every letter is classified three different ways for stance (Support / Oppose / Conditional), three different ways for entity bucket (Individual / Accountant / Issuer-current / Issuer-former / Investment professional / Industry practitioner / Academic researcher / Student), and three different ways for rationale codes (multi-label across 20 SEC-anchored argument families). Each of these is a separate Claude Opus 4.7 call with a different rubric prompt — Primary / Literalist / Skeptic for stance, Primary / Self-described / Letterhead for entity, Primary / Literalist / Inclusive for rationale. The headline shown on the site is the **majority vote** across the three raters in each ensemble. Agreement statistics (Fleiss' κ, per-code Cohen's κ, pairwise κ) are reported in the methodology accordions on the site. The same three stance / entity / rationale rubrics also ran through ChatGPT-5.5 as an independent second ensemble for cross-model validation. The framework follows Carlson and Burbano (*SMJ* 2026) and Liu (*CHB* 2026).

---

## How the pipeline runs

The repository runs itself, twice daily. A GitHub Actions cron at 14:00 UTC and 23:00 UTC (10 AM and 7 PM ET) executes `_scripts/daily_fetch.py`, which:

1. Pulls the SEC docket index (`/rules-regulations/public-comments/s7-2026-15`)
2. Compares URLs against `_meta/renumbered_records.json`
3. Fetches each new letter (HTML or PDF), writes a placeholder record with stance, entity, and rationales all set to "Unclassified"
4. Saves PDF letters to `_meta/pdf_letters/`
5. Re-runs the regression comparison
6. Rebuilds the public site
7. Commits and pushes back to `main` as `sec-tracker-bot`

The public site filters out the Unclassified placeholders — the visible table only shows fully-classified letters. Classification happens in a Cowork session in the Claude desktop app: Claude reads the new placeholders, runs the three ensembles on each, integrates the results into `renumbered_records.json` and the `Letters/` store, and a manual `python3 _scripts/build_and_push.py` refreshes the live site.

---

## Repository layout

```
.
├── public_site/                Production HTML — served by GitHub Pages
│   ├── index.html              The dashboard
│   ├── data.json               Same data as a separate JSON file
│   ├── bodies.json             Letter bodies for the (dev-only) voting modal
│   └── rationale-taxonomy.html The 20-code taxonomy reference page
├── Letters/                    Canonical letter store, one .md per letter
├── Letters_<N>_for_models/     Leakage-free mirror for cross-model runs
├── _meta/                      Methodology docs, datasets, audit notes
│   ├── renumbered_records.json The canonical dataset
│   ├── regression_compare.json Logit / Ordinal / LPM coefficients
│   ├── methodology.md
│   ├── entity_methodology.md
│   ├── rationale_methodology.md
│   ├── rationale_taxonomy.md
│   ├── carlson_burbano_audit.md
│   ├── liu_audit.md
│   └── pdf_letters/            PDFs of substantive long-form letters
├── _scripts/                   Build + fetch + regression scripts
│   ├── daily_fetch.py          SEC index parser + letter fetcher
│   ├── build_and_push.py       Build the dashboard, push via Contents API
│   ├── build_letters_for_models.py
│   ├── run_regression_compare.py
│   └── sync_from_github.sh     Pull repo state back to a local Dropbox folder
├── .github/workflows/
│   └── daily-fetch.yml         Cron at 14:00 UTC and 23:00 UTC
└── STATUS.md                   Project log and to-do list
```

---

## Citation

If you use the data or the methodology, please cite:

> Zach, T. (2026). *SEC S7-2026-15 public comment letter tracker.* Fisher College of Business, The Ohio State University. <https://tzachizach.github.io/sec-semi-annual-proposal-tracker/>

---

## References

- Carlson, J., & Burbano, V. C. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. *Strategic Management Journal*, 47(3), 699–725. DOI: 10.1002/smj.70023
- Liu, J. (2026). Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation. *Computers in Human Behavior*, 181, 108988. DOI: 10.1016/j.chb.2026.108988

---

## Feedback

Comments, suggestions, or corrections: <zach.7@osu.edu>, or use the feedback widget on the live site.

---

*Last updated: 2026-05-16.*
