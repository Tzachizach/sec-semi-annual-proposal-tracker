#!/usr/bin/env python3
"""2026-05-31 (Tzachi's call): swap the canonical Andrew Parker record.

Andrew Parker submitted twice. #99 (HTML, submission 774528, doc-id 2367854) was
classified Conditional. He then filed an amended, ~60%-longer PDF (#462, submission
774547, same doc-id 2367854) that reads as a firmer Oppose. Tzachi's decision:
keep the amended #462 as the canonical Andrew Parker (Oppose, via
_classify_345_462.py) and hold the original #99 out as the duplicate.

This patch marks #99 "Duplicate" (held out of the public snapshot, rater stats,
and regression) while preserving its body and rater fields for the record. Run
AFTER _classify_345_462.py (which sets #462 to its Oppose classification).
"""
import json
from pathlib import Path

RECORDS = Path(__file__).resolve().parent.parent / "_meta" / "renumbered_records.json"

def main():
    recs = json.loads(RECORDS.read_text())
    by = {r["n"]: r for r in recs}
    r99 = by[99]
    # Preserve the original rater calls in a note, then hold the record out.
    r99["majority_stance"] = "Duplicate"
    r99["stance"] = "Duplicate"
    r99["summary"] = ("Duplicate (original version) of Andrew Parker's comment — superseded by his "
                      "amended, longer PDF at #462, which Tzachi kept as the canonical record (Oppose). "
                      "Same doc-id 2367854. Held out of the count so Andrew Parker is not double-counted. "
                      "Original #99 was classified Conditional; the amended #462 firms to Oppose. "
                      + (r99.get("summary", "") or ""))
    # Drop the RFC engagement from #99 (it now lives on the canonical #462).
    r99.pop("rfc_questions", None)
    RECORDS.write_text(json.dumps(recs, indent=2, ensure_ascii=False) + "\n")
    print("[ok] #99 Andrew Parker -> Duplicate (held out); RFC engagement moved to #462.")
    print("     #462 stance:", by[462]["stance"], "| rfc:", bool(by[462].get("rfc_questions")))

if __name__ == "__main__":
    main()
