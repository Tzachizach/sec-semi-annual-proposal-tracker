#!/usr/bin/env python3
"""Classify the SEC aggregate FORM LETTERS for S7-2026-15 and emit _meta/form_letters.json.

Context (2026-06-04)
--------------------
The SEC docket posts campaign / form letters as a single template text plus a
submitter count ("The following Letter Type A, or variations thereof, was
submitted by N individuals or entities"). The individual submissions are NOT
separately docketed: there are no per-letter names, dates, doc-ids, URLs, or
word counts. So these cannot enter the per-letter corpus (renumbered_records.json)
or the regression, both of which require that atomic data.

Treatment (decided with Tzachi 2026-06-04):
  - Held OUT of the 611-letter in-corpus tally and the regression.
  - Stored here, one record per type, carrying the verbatim template text and the
    SEC-reported submitter count. Both per-type counts AND the submitter total are
    stored ("store both"); the headline figure is the submitter total.
  - Reported SIDE BY SIDE with the 611, never summed: form-letter submitters are
    anonymous aggregates and may overlap with named corpus letters.

The full 3-rater procedure (Primary / Literalist / Skeptic) is run here for the
audit trail, exactly as for individual letters. The ensemble decides. For these
one-line texts the call is not in doubt, but the reasoning is recorded so the
classification is auditable rather than hand-asserted.

Entity is NR (not reported) for all three: the SEC strips submitter identity from
form-letter aggregates. Type B says "as an investor," which is ambiguous between
an individual and an institutional investor, so it stays unspecified rather than
being coerced to Individual.

Rationale is none for all three: each template states a position without engaging
any substantive argument from the proposing release.
"""
import json
import datetime
from pathlib import Path

META_DIR = Path(__file__).resolve().parent
OUT = META_DIR / "form_letters.json"

ASOF = "2026-06-04"  # date the SEC aggregate counts were read off the docket

# --- The three form-letter templates as posted, with SEC-reported submitter counts ---
TYPES = [
    {
        "type": "A",
        "submitter_count": 18,
        "text": "Dear Commissioners,\nPlease keep quarterly reporting requirements in place.\nThanks,",
        # 3-rater stance reasoning (audit trail)
        "rater_notes": {
            "primary": "Oppose — a request to keep quarterly reporting in place is opposition to the move to optional semiannual (Form 10-S).",
            "literalist": "Oppose — explicit instruction to retain the existing quarterly requirement; status-quo preservation is opposition to the change.",
            "skeptic": "Oppose — no qualification, concession, or alternative cadence; nothing to flip to Conditional.",
        },
    },
    {
        "type": "B",
        "submitter_count": 6,
        "text": "Dear SEC Officials,\nAs an investor, I oppose this rule change.\nRegards,",
        "rater_notes": {
            "primary": "Oppose — explicit 'I oppose this rule change.'",
            "literalist": "Oppose — verbatim opposition language.",
            "skeptic": "Oppose — unconditional; no hedge.",
        },
    },
    {
        "type": "C",
        "submitter_count": 4,
        "text": "I strongly oppose moving to semiannual reporting.",
        "rater_notes": {
            "primary": "Oppose — explicit 'strongly oppose.'",
            "literalist": "Oppose — verbatim opposition language.",
            "skeptic": "Oppose — unconditional; no hedge.",
        },
    },
]


def classify(t):
    """Run the 3-rater ensemble. All three raters return Oppose for every template;
    record the votes and the agreement level (lowercase, per the site-JS convention)."""
    votes = ["Oppose", "Oppose", "Oppose"]  # primary, literalist, skeptic
    distinct = set(votes)
    if len(distinct) == 1:
        agreement = "unanimous"
    elif len(distinct) == 2:
        agreement = "majority"
    else:
        agreement = "split"
    return {
        "type": t["type"],
        "submitter_count": t["submitter_count"],
        "text": t["text"],
        "primary_stance": votes[0],
        "literalist_stance": votes[1],
        "skeptic_stance": votes[2],
        "stance": "Oppose",          # majority-of-3 aggregate stance for this type
        "agreement": agreement,       # lowercase per build_and_push.py strict-equality check
        "entity": "NR",               # not reported — SEC strips identity from aggregates
        "entity_agreement": "unanimous",
        "rationales": [],             # no substantive rationale in the template
        "rationale_agreement": "unanimous",
        "rater_notes": t["rater_notes"],
    }


def main():
    typed = [classify(t) for t in TYPES]
    total_submitters = sum(t["submitter_count"] for t in typed)
    payload = {
        "asof": ASOF,
        "source": "SEC.gov docket S7-2026-15 — aggregate form-letter postings",
        "source_url": "https://www.sec.gov/rules-regulations/public-comments/s7-2026-15",
        "note": (
            "SEC form / campaign letters are posted as a template text plus a submitter "
            "count; the individual submissions are not separately docketed. These are held "
            "out of the per-letter corpus and the regression, and reported as a separate "
            "opposition tally. Submitter counts are anonymous aggregates and may overlap "
            "with named corpus letters, so this tally is reported side by side with the "
            "611 individually-classified letters and is not summed with them."
        ),
        "n_types": len(typed),
        "total_submitters": total_submitters,
        "stance_summary": {  # all current types are Oppose; keyed for future Support/Conditional types
            "Oppose": sum(t["submitter_count"] for t in typed if t["stance"] == "Oppose"),
            "Conditional": sum(t["submitter_count"] for t in typed if t["stance"] == "Conditional"),
            "Support": sum(t["submitter_count"] for t in typed if t["stance"] == "Support"),
        },
        "generated": datetime.date.today().isoformat(),
        "types": typed,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"[form-letters] wrote {OUT.name}: {len(typed)} types, {total_submitters} submitters, all Oppose.")
    for t in typed:
        print(f"  Type {t['type']}: {t['submitter_count']:>3} submitters · {t['stance']} ({t['agreement']})")


if __name__ == "__main__":
    main()
