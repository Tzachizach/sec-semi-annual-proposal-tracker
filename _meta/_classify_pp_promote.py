#!/usr/bin/env python3
"""Promote PP (political pressure / regulatory capture) from a §6.6 watch item to a
coded rationale (the 21st code), and tag the 17 confirmed letters.

Context (2026-06-04)
--------------------
PP was carried as a watch item across every classification batch. The tally reached
17 explicit flags, well past the 7-10 promotion threshold, and the narrow definition
held across every read. Decision (with Tzachi): promote PP to a coded rationale.

Narrow definition (unchanged): a letter qualifies only if it argues the rule itself is
politically motivated or serves the powerful / captured regulators — attribution to
political pressure, lobbying, donor influence, partisan/regime alignment, or regulatory
capture. Generic concealment-suspicion, ordinary insiders-vs-retail framing, and generic
motive-questioning do NOT qualify. The candidates that failed this gate (#499, #511, #559,
#589, #590, #620) are documented in HANDOFF_2026-06-03.md and pp_watch_candidates.md §B
and are NOT tagged here.

Rater treatment: for all 17, the political/capture attribution is explicit surface text,
so all three rationale raters (Primary / Literalist / Inclusive) code PP. PP is therefore
added to each rater list and to the majority set, and the rationale_agreement relation is
preserved (adding the same code to all three rater sets does not change set-equality).

This tags ONLY the 17 already-confirmed letters; it does not re-open the corpus-wide scan,
which the watch process has run continuously. PP appears only on Oppose letters.

Safe-write: backs up renumbered_records.json and writes via a temp file + os.replace so a
Dropbox File-Provider lock cannot corrupt the canonical dataset.
"""
import json
import os
import re
import shutil
import datetime
from collections import Counter
from pathlib import Path

META_DIR = Path(__file__).resolve().parent
RECORDS = META_DIR / "renumbered_records.json"

# The 17 confirmed PP letters with their operative quotes (from pp_watch_candidates.md §A
# + the 3 additions documented in HANDOFF_2026-06-03.md).
PP = {
    258: "Full blown corruption in broad daylight... hurtful to 99% of Americans.",
    260: "this rule revision reflects corporate/government cronyism... I don't have powerful attorneys or lobbyists at my disposal.",
    261: "If the sec attempts to do this, it proves how corrupt this country really is!",
    310: "those in charge of protecting us from bad actors, are receiving kickbacks from these same criminals while they point out new targets and shield them from the law.",
    314: "We do not need further corruption to infiltrate our institutions of justice.",
    334: "Another Trump directed cop-out to the rich and influential!",
    346: "the biggest money always gets the biggest opportunities to change the rules... Are you really considering opening a door that will allow corruption by rule and law?",
    358: "Be responsible to the public, not corporate lobbyists.",
    378: "The SEC should not take any action that increases corruption.",
    397: "In a time when corporate and political corruption is at its highest...",
    426: "Rich keep getting richer. What about a government for the common people and not the 1%?",
    451: "Reducing the reporting requirements is reckless at best, and flat out corrupt at worst... stand up for the American people instead of paving the way for financial malfeasance.",
    458: "You were hired to drain the swamp not facilitate it.",
    460: "Stop showing favoritism.",
    601: "we are dealing with the worst corruption ever and SEC wants to protect itself and other corrupt entities.",
    607: "everywhere you see biannual reporting you will find fraud but hey thats the United States way, right. Well at least under a republican administration.",
    616: "The regime is already doing what they can to weaken the US economy, why would you guys volunteer to take the fall for them??",
}

VALID_STANCE = {"Support", "Oppose", "Conditional"}


def majority_rationales(rater_lists):
    counts = Counter()
    for codes in rater_lists:
        for c in codes:
            counts[c] += 1
    return sorted([c for c, n in counts.items() if n >= 2])


def merge_evidence(existing, quote):
    """Drop any prior 'PP-watch...' clause and append a formal PP clause."""
    existing = (existing or "").strip()
    if existing:
        # Remove sentence-segments mentioning the old PP-watch note.
        segs = [s for s in re.split(r"(?<=\.)\s+", existing) if "PP-watch" not in s]
        existing = " ".join(segs).strip()
    pp_clause = f"PP: '{quote}'"
    if not existing:
        return pp_clause
    if not existing.endswith("."):
        existing += "."
    return f"{existing} {pp_clause}"


def main():
    records = json.loads(RECORDS.read_text())
    by_n = {r["n"]: r for r in records}

    # Backup before mutating.
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = META_DIR / f"renumbered_records.backup_pp_{stamp}.json"
    shutil.copy2(RECORDS, backup)

    changed = []
    for n, quote in PP.items():
        if n not in by_n:
            raise SystemExit(f"ERROR: record #{n} not found")
        rec = by_n[n]
        if rec.get("stance") not in VALID_STANCE:
            raise SystemExit(f"ERROR: #{n} has non-corpus stance {rec.get('stance')!r}; PP only tags in-corpus letters")
        if rec.get("stance") != "Oppose":
            print(f"  NOTE: #{n} stance is {rec.get('stance')} (expected Oppose)")

        for fld in ("rationales_primary", "rationales_literalist", "rationales_inclusive"):
            lst = list(rec.get(fld) or [])
            if "PP" not in lst:
                lst.append("PP")
            rec[fld] = lst

        rater_lists = [rec["rationales_primary"], rec["rationales_literalist"], rec["rationales_inclusive"]]
        rec["rationales_majority"] = majority_rationales(rater_lists)
        rec["rationales"] = rec["rationales_majority"]
        cats = [set(x) for x in rater_lists]
        rec["rationale_agreement"] = "unanimous" if cats[0] == cats[1] == cats[2] else "majority"
        rec["rationale_evidence"] = merge_evidence(rec.get("rationale_evidence", ""), quote)
        changed.append(n)

    # Safe write: temp + atomic replace.
    tmp = RECORDS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    os.replace(tmp, RECORDS)

    # Report.
    pp_count = sum(1 for r in records if "PP" in (r.get("rationales") or []))
    pp_oppose = sum(1 for r in records if "PP" in (r.get("rationales") or []) and r.get("stance") == "Oppose")
    print(f"[pp-promote] tagged {len(changed)} letters: {sorted(changed)}")
    print(f"[pp-promote] PP now appears on {pp_count} records ({pp_oppose} Oppose).")
    print(f"[pp-promote] backup written: {backup.name}")
    assert pp_count == 17, f"expected 17 PP records, got {pp_count}"
    assert pp_count == pp_oppose, "PP should appear only on Oppose letters"


if __name__ == "__main__":
    main()
