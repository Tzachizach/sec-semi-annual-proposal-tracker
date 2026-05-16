#!/usr/bin/env python3
"""
Build a leakage-free copy of the letter corpus for cross-model classification runs.

Reads:   Letters/                    (canonical letter store, includes classification metadata)
Writes:  Letters_<N>_for_models/     (cleaned copies, stripped of classification leaks)
         Letters_<N>_for_models.zip  (zipped copy of the above for chat uploads)

The "canonical" Letters/ files carry header lines like:
  - **Stance:** Oppose
  - **Entity:** Accountant (CPA)
  - **Rationales:** IP, FR, IA
  - **Role/Affiliation:** CPA, retail investor
These are derived from our own classifications and bias any model we ask to classify
the same letters (confirmed empirically on the 2026-05-14 ChatGPT-5.5 S1 run, which
produced κ = 1.000 against Claude-Primary because GPT transcribed the leaked label).

This script strips those leak lines and keeps everything else (H1, Date, Source/URL,
the letter body, the SEC-quoted material).

Run from the project root:
    python3 _scripts/build_letters_for_models.py

Rerun whenever Letters/ changes (new letters arrive, reclassification, etc.).
"""
import os
import re
import shutil
import zipfile
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(PROJECT_ROOT, "Letters")

# Lines starting with "- Stance" / "- **Stance:**" / "* Stance:" / etc. for any of
# the listed classification keys. Case-insensitive. The list deliberately includes
# Role and Role/Affiliation because that string is a Tzachi-curated role summary
# derived from the letter body — keeping it would prime entity classification.
LEAK_RE = re.compile(
    r"^\s*[-*]\s*\*{0,2}\s*(Stance|Entity|Rationales?|Role(?:/Affiliation)?)\b.*$",
    re.IGNORECASE,
)


def main() -> int:
    if not os.path.isdir(SRC):
        print(f"[error] Letters/ not found at {SRC}", file=sys.stderr)
        return 1

    md_files = sorted(f for f in os.listdir(SRC) if f.endswith(".md"))
    n_letters = len(md_files)
    dst_name = f"Letters_{n_letters}_for_models"
    dst = os.path.join(PROJECT_ROOT, dst_name)
    zip_path = os.path.join(PROJECT_ROOT, f"{dst_name}.zip")

    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)

    total_stripped = 0
    for fname in md_files:
        with open(os.path.join(SRC, fname)) as fh:
            lines = fh.readlines()
        kept = []
        for ln in lines:
            if LEAK_RE.match(ln):
                total_stripped += 1
                continue
            kept.append(ln)
        with open(os.path.join(dst, fname), "w") as fh:
            fh.writelines(kept)

    # Build the zip
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in md_files:
            zf.write(os.path.join(dst, fname), arcname=fname)

    print(f"[build] Wrote {dst_name}/ ({n_letters} letters, {total_stripped} leak lines stripped)")
    print(f"[build] Wrote {os.path.basename(zip_path)}")
    print(f"[done] Upload {os.path.basename(zip_path)} alongside the cross-model prompts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
