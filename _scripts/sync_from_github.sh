#!/bin/bash
#
# Mac-side mirror — pull the dataset back from GitHub after the daily Action ran.
#
# The GitHub Action commits new letters, refreshed renumbered_records.json, the
# rebuilt public_site/, and the regression comparison files. This script brings
# those changes back to the local Dropbox folder so Excel, regression, and any
# manual Cowork classification can pick up where the Action left off.
#
# Usage:
#   bash _scripts/sync_from_github.sh
#
# Can be wired into launchd / a daily macOS reminder, or run on demand before a
# Cowork session.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

REPO_RAW="https://raw.githubusercontent.com/tzachizach/sec-semi-annual-proposal-tracker/main"

# --- 1. Files we always pull back -----------------------------------------------------
# These live on `main` after every Action run and are the source of truth for the
# next Cowork session.
files=(
  "_meta/renumbered_records.json"
  "_meta/regression_compare.json"
  "_meta/regression_compare.md"
  "public_site/index.html"
  "public_site/data.json"
  "public_site/bodies.json"
  "public_site/rationale-taxonomy.html"
)

echo "[sync] Pulling ${#files[@]} canonical files from GitHub main..."
for f in "${files[@]}"; do
  url="${REPO_RAW}/${f}"
  tmp="$(mktemp)"
  if curl -fsSL "$url" -o "$tmp"; then
    mv "$tmp" "$f"
    echo "  ok    $f"
  else
    echo "  FAIL  $f  ($url)"
    rm -f "$tmp"
  fi
done

# --- 2. Letters/ — pull any new NN_*.md files the Action added ------------------------
# Strategy: read the GitHub Contents API for the Letters/ folder, diff against local,
# fetch missing files. Cheap and avoids a full git clone.
echo "[sync] Checking Letters/ folder for new files..."

python3 <<'PY'
import json, os, sys, urllib.request

API = "https://api.github.com/repos/tzachizach/sec-semi-annual-proposal-tracker/contents/Letters?ref=main"

try:
    with urllib.request.urlopen(API, timeout=30) as resp:
        data = json.load(resp)
except Exception as e:
    print(f"[sync] Letters/ tree fetch failed: {e}", file=sys.stderr)
    sys.exit(0)

if not isinstance(data, list):
    print("[sync] Unexpected Letters/ tree response; skipping.", file=sys.stderr)
    sys.exit(0)

local_files = set(os.listdir("Letters")) if os.path.isdir("Letters") else set()
remote_files = {item["name"]: item["download_url"] for item in data if item.get("type") == "file"}
missing = [name for name in remote_files if name not in local_files]

if not missing:
    print("[sync] Letters/ already in sync.")
    sys.exit(0)

print(f"[sync] {len(missing)} new letter file(s) to pull.")
for name in missing:
    url = remote_files[name]
    dest = os.path.join("Letters", name)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp, open(dest, "wb") as fh:
            fh.write(resp.read())
        print(f"  pulled  {name}")
    except Exception as e:
        print(f"  FAIL    {name}  ({e})")
PY

echo "[done] Sync complete."

# --- 3. Optional next step ------------------------------------------------------------
# If any of the new Letters/ files have stance == "Unclassified" in
# renumbered_records.json, those are the ones a Cowork session should classify.
UNCLASSIFIED_COUNT=$(python3 -c "
import json
recs = json.load(open('_meta/renumbered_records.json'))
print(sum(1 for r in recs if r.get('stance') == 'Unclassified'))
")
if [ "${UNCLASSIFIED_COUNT}" -gt "0" ]; then
  echo
  echo "[notice] ${UNCLASSIFIED_COUNT} letter(s) awaiting Claude classification."
  echo "         Open Cowork and ask Claude to run the 3-rater ensemble on them."
fi
