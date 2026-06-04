#!/usr/bin/env python3
"""Normalize shorthand entity-label spellings to their canonical bucket names.

Three shorthand variants crept in from a couple of classify scripts; they are the
same buckets as the canonical slash/em-dash forms, not distinct entities:

  Industry practitioner-technologist  ->  Industry practitioner / technologist
  Issuer-current                      ->  Issuer / Corporate — current
  Issuer-former                       ->  Issuer / Corporate — former

Leaving them split mis-buckets a few records in the regression (e.g., Foley & Lardner
#618, a Support letter, falls outside the Industry-practitioner dummy). This normalizes
all entity fields in place so the canonical bucket is used everywhere — the regression,
the entity chart, and the agreement stats. It is a spelling fix, not a reclassification:
the ensemble's bucket choice is unchanged.

Safe-write: backs up renumbered_records.json and writes via temp + os.replace.
"""
import json
import os
import shutil
import datetime
from pathlib import Path

META_DIR = Path(__file__).resolve().parent
RECORDS = META_DIR / "renumbered_records.json"

CANON = {
    "Industry practitioner-technologist": "Industry practitioner / technologist",
    "Issuer-current": "Issuer / Corporate — current",
    "Issuer-former": "Issuer / Corporate — former",
}
FIELDS = ("entity", "entity_primary", "entity_selfdescribed", "entity_letterhead", "entity_majority")


def main():
    records = json.loads(RECORDS.read_text())
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = META_DIR / f"renumbered_records.backup_entitynorm_{stamp}.json"
    shutil.copy2(RECORDS, backup)

    field_changes = 0
    touched = set()
    for r in records:
        for f in FIELDS:
            v = r.get(f)
            if v in CANON:
                r[f] = CANON[v]
                field_changes += 1
                touched.add(r["n"])

    tmp = RECORDS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    os.replace(tmp, RECORDS)

    # Verify no variant labels remain anywhere.
    remaining = sorted({r.get(f) for r in records for f in FIELDS if r.get(f) in CANON})
    print(f"[entity-norm] {field_changes} field value(s) normalized across {len(touched)} record(s): {sorted(touched)}")
    print(f"[entity-norm] backup: {backup.name}")
    assert not remaining, f"variant labels still present: {remaining}"


if __name__ == "__main__":
    main()
