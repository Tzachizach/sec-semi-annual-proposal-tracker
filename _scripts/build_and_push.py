#!/usr/bin/env python3
"""
Build the public dashboard and push to GitHub.

Reads:   _meta/renumbered_records.json   (the canonical dataset)
Writes:  public_site/index.html          (fully baked HTML with embedded data)
         public_site/data.json           (same data, separately, for future automation)

Pushes both files to: https://github.com/<GITHUB_USER>/<GITHUB_REPO>

Token: read from _meta/.github_token (a file with just the PAT, no quotes, no newline padding).
       The file is in .gitignore so it never reaches GitHub.

Run manually:  python3 _scripts/build_and_push.py
The 2 AM scheduled task runs this automatically after updating the dataset.
"""
import argparse
import base64
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ---- Configuration ---------------------------------------------------------

GITHUB_USER = "tzachizach"
GITHUB_REPO = "sec-semi-annual-proposal-tracker"
GITHUB_BRANCH = "main"

# Resolve project paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

META_DIR = PROJECT_DIR / "_meta"
RECORDS_PATH = META_DIR / "renumbered_records.json"
FORM_LETTERS_PATH = META_DIR / "form_letters.json"
TOKEN_PATH = META_DIR / ".github_token"
SUPABASE_CREDS_PATH = META_DIR / ".supabase_credentials"
GOATCOUNTER_PATH = META_DIR / ".goatcounter_code"
LETTERS_DIR = PROJECT_DIR / "Letters"

PUBLIC_DIR = PROJECT_DIR / "public_site"
PUBLIC_HTML = PUBLIC_DIR / "index.html"
PUBLIC_JSON = PUBLIC_DIR / "data.json"
PUBLIC_BODIES = PUBLIC_DIR / "bodies.json"

# Dev mirror — never pushed. Used to preview unreleased features (voting widget, etc.).
PUBLIC_DEV_DIR = PROJECT_DIR / "public_site_dev"
PUBLIC_DEV_HTML = PUBLIC_DEV_DIR / "index.html"
PUBLIC_DEV_JSON = PUBLIC_DEV_DIR / "data.json"
PUBLIC_DEV_BODIES = PUBLIC_DEV_DIR / "bodies.json"

# Controlled by --dev CLI flag; default off so launchd-driven runs only update production.
BUILD_DEV_MIRROR = False

# Files to upload (path on GitHub  ->  local path).
#
# The first four are the public site itself. `_meta/renumbered_records.json` is
# the canonical dataset: it MUST also be pushed so the Cowork classification
# work survives the next Action run. Without this, daily_fetch.py reads the
# stale GitHub copy on its next run and the subsequent sync overwrites the
# Mac-side classifications with placeholders. See STATUS log 2026-05-18 evening.
FILES_TO_PUSH = {
    "index.html": PUBLIC_HTML,
    "data.json": PUBLIC_JSON,
    "bodies.json": PUBLIC_BODIES,
    "rationale-taxonomy.html": PUBLIC_DIR / "rationale-taxonomy.html",
    "_meta/renumbered_records.json": RECORDS_PATH,
    # SEC aggregate form-letter tally (template text + submitter counts). Held out of the
    # 611 per-letter corpus and the regression; rendered as a separate side-by-side panel.
    "_meta/form_letters.json": FORM_LETTERS_PATH,
    # Build scripts the GitHub Action runs. These MUST be pushed too, otherwise the
    # Action rebuilds the live site with a stale copy of build_and_push.py and reverts
    # local presentation work (amber Conditional color, longest-letters accordion,
    # off-topic filtering / in-corpus count). See STATUS log 2026-05-20.
    "_scripts/build_and_push.py": SCRIPT_DIR / "build_and_push.py",
    "_scripts/run_regression_compare.py": SCRIPT_DIR / "run_regression_compare.py",
    "_scripts/build_letters_for_models.py": SCRIPT_DIR / "build_letters_for_models.py",
}


def load_form_letters():
    """Load _meta/form_letters.json — the SEC aggregate form-letter tally.

    Returns the parsed dict, or None if the file is absent (in which case the
    site renders without the form-letter panel). These are held out of the
    per-letter corpus and the regression; see _meta/_classify_form_letters.py.
    """
    if not FORM_LETTERS_PATH.exists():
        return None
    try:
        return json.loads(FORM_LETTERS_PATH.read_text())
    except (ValueError, OSError):
        return None


def load_supabase_creds():
    """Return (url, anon_key) tuple, or (None, None) if file missing."""
    if not SUPABASE_CREDS_PATH.exists():
        return None, None
    url, key = None, None
    for line in SUPABASE_CREDS_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k == "SUPABASE_URL":
                url = v
            elif k == "SUPABASE_ANON_KEY":
                key = v
    return url, key


def load_goatcounter_snippet():
    """Return a <script> tag for GoatCounter, or '' if no code file present.

    The file should contain either:
      - just the GoatCounter subdomain code (e.g. `tzachizach`), OR
      - the full <script> tag that GoatCounter provides on its setup page.
    """
    if not GOATCOUNTER_PATH.exists():
        return ""
    raw = GOATCOUNTER_PATH.read_text().strip()
    if not raw:
        return ""
    if raw.startswith("<script"):
        return raw
    # Assume bare code → construct the standard snippet
    code = raw.split()[0].strip()
    return (
        f'<script data-goatcounter="https://{code}.goatcounter.com/count" '
        f'async src="//gc.zgo.at/count.js"></script>'
    )


def load_letter_bodies():
    """Read Letters/NN_*.md, strip the YAML header, return {n: body_text}."""
    if not LETTERS_DIR.exists():
        return {}
    out = {}
    for path in sorted(LETTERS_DIR.glob("*.md")):
        name = path.name
        # filename like "01_..._<lid>.md" or "78_..._<lid>.md"
        m = re.match(r"^(\d+)_", name)
        if not m:
            continue
        n = int(m.group(1))
        text = path.read_text(errors="replace")
        # Skip header — split on first "---" line
        if "---" in text:
            text = text.split("---", 1)[1]
        out[n] = text.strip()
    return out

# ---- HTML template ---------------------------------------------------------

HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>SEC Semi-Annual Reporting Proposal Tracker (S7-2026-15)</title>
<meta name="description" content="Public tracker for comment letters submitted on SEC proposed rule S7-2026-15 (Optional Semiannual Reporting by Public Companies)." />
<style>
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 24px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  background: #ffffff; color: #1a1a1a; line-height: 1.5; font-size: 14px;
  max-width: 880px; margin-left: auto; margin-right: auto;
}
h1 { font-size: 24px; font-weight: 500; margin: 0 0 4px; }
h2 { font-size: 16px; font-weight: 500; margin: 0 0 12px; }
.lede { color: #555; font-size: 13px; margin: 0 0 16px; }
.meta { color: #777; font-size: 12px; margin: 0 0 24px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 24px; }
.card { background: #f7f5ef; border-radius: 8px; padding: 16px; min-height: 90px; }
.card .label { font-size: 12px; color: #666; margin: 0 0 6px; }
.card .value { font-size: 28px; font-weight: 500; margin: 0; line-height: 1; }
.card .pct { font-size: 12px; color: #777; margin: 4px 0 0; }
.card.support .value { color: #3b6d11; }
.card.oppose .value { color: #993c1d; }
.card.conditional .value { color: #a8830d; }
.section { margin-bottom: 28px; }
.chart-wrap { position: relative; width: 100%; height: 240px; }
.chart-wrap.short { height: 200px; }
.legend { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: #555; margin: 0 0 12px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.swatch { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
.stance-list { list-style: none; padding: 0; margin: 12px 0 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; }
.stance-list li { display: flex; justify-content: space-between; align-items: baseline; padding: 8px 12px; background: #fafaf7; border-radius: 6px; font-size: 13px; }
.stance-list .lbl { display: inline-flex; align-items: center; gap: 8px; }
.stance-list .num { font-variant-numeric: tabular-nums; color: #555; }
.stance-list .num strong { color: #1a1a1a; font-weight: 500; }
.row { display: grid; grid-template-columns: 36px 90px 1fr 110px 60px;
  align-items: baseline; gap: 12px; padding: 10px 12px;
  border: 0.5px solid rgba(0,0,0,0.1); border-radius: 8px; font-size: 13px;
  margin-bottom: 6px; }
.row .num { color: #888; font-variant-numeric: tabular-nums; }
.row .date { color: #666; font-variant-numeric: tabular-nums; }
.row .name a { color: #1a1a1a; font-weight: 500; text-decoration: none; }
.row .name a:hover { text-decoration: underline; }
.row .role { color: #777; font-size: 12px; display: block; margin-top: 2px; }
.row .words { color: #555; font-variant-numeric: tabular-nums; font-size: 12px; text-align: right; }
.row .pill { font-size: 11px; padding: 2px 8px; border-radius: 999px; text-align: center; font-weight: 500; white-space: nowrap; }
.pill.Oppose { background: #FCEBEB; color: #791F1F; }
.pill.Support { background: #EAF3DE; color: #27500A; }
.pill.Conditional { background: #fcf2c0; color: #6b4f0a; }
.pill.PDF { background: #F1EFE8; color: #444441; }
.longest-row { display: grid; grid-template-columns: 36px 70px 1.2fr 100px 56px 1.4fr;
  align-items: baseline; gap: 12px; padding: 10px 12px;
  border: 0.5px solid rgba(0,0,0,0.1); border-radius: 8px; font-size: 13px;
  margin-bottom: 6px; }
.longest-row .num { color: #888; font-variant-numeric: tabular-nums; }
.longest-row .date { color: #666; font-variant-numeric: tabular-nums; }
.longest-row .name a { color: #1a1a1a; font-weight: 500; text-decoration: none; }
.longest-row .name a:hover { text-decoration: underline; }
.longest-row .role { color: #777; font-size: 12px; display: block; margin-top: 2px; }
.longest-row .words { color: #555; font-variant-numeric: tabular-nums; font-size: 12px; text-align: right; }
.longest-row .pill { font-size: 11px; padding: 2px 8px; border-radius: 999px; text-align: center; font-weight: 500; white-space: nowrap; }
.longest-row .rat-cell { display: flex; flex-wrap: wrap; gap: 3px; align-items: center; }
.stance-block { background: #faf8f2; border: 0.5px solid rgba(0,0,0,0.08); border-radius: 10px; padding: 12px 18px; margin: 0 0 10px; font-size: 13px; }
.stance-block summary { cursor: pointer; list-style: none; font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 8px; padding: 4px 0; letter-spacing: 0.02em; }
.stance-block summary::-webkit-details-marker { display: none; }
.stance-block summary::after { content: "▾"; font-size: 14px; font-weight: 600; color: inherit; transition: transform 0.15s ease; margin-left: auto; }
.stance-block[open] summary::after { transform: rotate(180deg); }
.stance-block summary .bucket-meta { font-size: 12px; color: #888; font-weight: 400; letter-spacing: 0; }
.stance-block .stance-rows { margin-top: 10px; }
.methodology { background: #faf8f2; border: 0.5px solid rgba(0,0,0,0.08); border-radius: 10px; padding: 16px 20px; margin: 0 0 18px; font-size: 13px; line-height: 1.55; }
.methodology summary { cursor: pointer; list-style: none; font-size: 17px; font-weight: 600; color: #1a1a1a; display: flex; align-items: center; gap: 8px; padding: 4px 0; }
.methodology summary::-webkit-details-marker { display: none; }
.methodology summary::after { content: "▾"; font-size: 17px; font-weight: 600; color: #185fa5; transition: transform 0.15s ease; margin-left: auto; }
.methodology[open] summary::after { transform: rotate(180deg); }
.methodology summary .accordion-meta { font-size: 13px; color: #888; font-weight: 400; }
.methodology summary .kw-stance     { color: #185fa5; }
.methodology summary .kw-commenters { color: #6b3d8a; }
.methodology summary .kw-rationales { color: #2a7d6b; }
.methodology .body { margin-top: 12px; color: #444; font-size: 13px; }
.methodology dl { margin: 8px 0 0; display: grid; grid-template-columns: 110px 1fr; column-gap: 14px; row-gap: 10px; }
.methodology dt { font-weight: 500; color: #1a1a1a; }
.methodology dt .dot { display: inline-block; width: 8px; height: 8px; border-radius: 999px; margin-right: 6px; vertical-align: middle; }
.methodology dd { margin: 0; color: #444; }
.intro { background: #fbf9f3; border-left: 3px solid #185fa5; border-radius: 6px; padding: 14px 18px; margin: 8px 0 20px; font-size: 14px; line-height: 1.55; color: #2a2a2a; }
.intro p { margin: 0; }
.intro p + p { margin-top: 10px; }
.intro a { color: #185fa5; text-decoration: none; }
.intro a:hover { text-decoration: underline; }

/* Feedback modal */
.feedback-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.45); display: none; align-items: flex-start; justify-content: center; z-index: 998; padding: 36px; overflow-y: auto; }
.feedback-overlay.show { display: flex; }
.feedback-modal { background: #fff; max-width: 560px; width: 100%; border-radius: 12px; padding: 24px; box-shadow: 0 12px 48px rgba(0,0,0,0.2); }
.feedback-modal .field label { display: block; font-size: 11px; color: #888; margin-bottom: 4px; letter-spacing: 0.02em; text-transform: uppercase; }
.feedback-modal .field input, .feedback-modal .field textarea { width: 100%; padding: 8px 10px; border: 0.5px solid rgba(0,0,0,0.2); border-radius: 6px; font-family: inherit; font-size: 13px; color: #1a1a1a; background: #fff; }
.feedback-modal .field input:focus, .feedback-modal .field textarea:focus { outline: 0; border-color: #185fa5; box-shadow: 0 0 0 2px rgba(24,95,165,0.1); }
.feedback-modal .field textarea { resize: vertical; min-height: 120px; }
.feedback-modal .feedback-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
@media (max-width: 520px) { .feedback-modal .feedback-grid { grid-template-columns: 1fr; } }
.feedback-modal .feedback-actions { display: flex; gap: 10px; margin-top: 16px; justify-content: flex-end; }
.feedback-modal .feedback-actions button { padding: 8px 14px; border-radius: 8px; border: 0.5px solid rgba(0,0,0,0.2); background: #fff; cursor: pointer; font-size: 13px; }
.feedback-modal .feedback-actions button.primary { background: #1a1a1a; color: #fff; border-color: #1a1a1a; }
.feedback-modal .feedback-actions button.primary:disabled { background: #aaa; cursor: not-allowed; }

/*DEV_ONLY:BEGIN*/
.rat-badge { display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 8px; margin: 1px 2px; font-weight: 600; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 0.02em; cursor: help; }
.rat-zero-note { background: #faf8f2; border: 0.5px solid rgba(0,0,0,0.08); border-radius: 8px; padding: 10px 14px; margin: 12px 0 0; font-size: 12px; color: #444; line-height: 1.6; }
.rat-zero-note .rat-badge { margin: 0 2px; }
.rat-cell { line-height: 1.7; }
.pill-hover-zone { position: absolute; cursor: help; }
#rationale-tooltip {
  position: fixed; display: none; z-index: 9999; pointer-events: none;
  background: #1a1a1a; color: #fff; padding: 10px 14px; border-radius: 8px;
  font-size: 12px; line-height: 1.5; max-width: 360px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.25);
}
#rationale-tooltip .rt-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
#rationale-tooltip .rt-code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; letter-spacing: 0.03em; }
#rationale-tooltip .rt-name { font-weight: 500; font-size: 12px; color: #fff; }
#rationale-tooltip .rt-desc { color: #ccc; font-size: 12px; }
/*DEV_ONLY:END*/
table.full { width: 100%; border-collapse: collapse; font-size: 13px; }
table.full th, table.full td { padding: 8px 10px; border-bottom: 0.5px solid rgba(0,0,0,0.1); text-align: left; vertical-align: top; }
table.full th { font-weight: 500; color: #555; font-size: 12px; cursor: pointer; user-select: none; }
/* Keep stance label + agreement badge on the same line. The badge needs ~50px after the stance word, so give the column enough room and disable wrap. */
table.full th:nth-child(5), table.full td:nth-child(5) { white-space: nowrap; min-width: 130px; }
table.full th.sorted { color: #1a1a1a; }
table.full th.sorted::after { content: " ▾"; }
table.full th.sorted.asc::after { content: " ▴"; }
table.full td.num { font-variant-numeric: tabular-nums; }
table.full td.right { text-align: right; }
table.full a { color: #185fa5; text-decoration: none; }
table.full a:hover { text-decoration: underline; }
table.full tr.date-header td { background: #f0eee7; padding: 10px 14px; cursor: pointer; user-select: none; border-top: 1px solid rgba(0,0,0,0.15); border-bottom: 0.5px solid rgba(0,0,0,0.08); }
table.full tr.date-header .chevron { display: inline-block; width: 18px; color: #185fa5; font-size: 17px; font-weight: 600; transition: transform 0.15s ease; }
table.full tr.date-header.open .chevron { transform: rotate(0deg); }
table.full tr.date-header .group-date { font-weight: 600; color: #1a1a1a; font-size: 14px; margin-left: 4px; }
table.full tr.date-header .group-count { font-weight: 400; color: #777; font-size: 12px; margin-left: 10px; }
table.full tr.collapsed-row { display: none; }
.search-row { display: flex; align-items: center; gap: 10px; margin: 8px 0 12px; }
.search-row .search { flex: 1; margin: 0; }
.search { margin: 8px 0 12px; }
.search input { width: 100%; padding: 8px 12px; border: 0.5px solid rgba(0,0,0,0.2); border-radius: 8px; font-size: 14px; }
.expand-toggle { padding: 8px 14px; border: 0.5px solid rgba(0,0,0,0.2); border-radius: 8px; background: #fff; font-size: 12px; color: #444; cursor: pointer; white-space: nowrap; }
.expand-toggle:hover { background: #faf8f2; }
.footer { font-size: 12px; color: #888; margin-top: 32px; padding-top: 16px; border-top: 0.5px solid rgba(0,0,0,0.1); }
.footer a { color: #185fa5; text-decoration: none; }
.footer a:hover { text-decoration: underline; }
.regression-panel { background: #fafaf7; border: 0.5px solid rgba(0,0,0,0.1); border-radius: 10px; padding: 14px 18px; }
.reg-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.reg-table th, .reg-table td { padding: 8px 12px; text-align: left; vertical-align: top; }
.reg-table thead th { font-weight: 500; color: #555; font-size: 12px; border-bottom: 1px solid rgba(0,0,0,0.18); }
.reg-table thead th.spec { text-align: right; font-variant-numeric: tabular-nums; }
.reg-table tbody tr { border-bottom: 0.5px solid rgba(0,0,0,0.07); }
.reg-table td.var { font-size: 13px; }
.reg-table td.cell { text-align: right; font-variant-numeric: tabular-nums; }
.reg-table td.cell .coef { font-size: 13px; font-weight: 500; line-height: 1.25; }
.reg-table td.cell .se   { font-size: 11px; color: #777; line-height: 1.15; }
.reg-table td.cell .pv   { font-size: 11px; color: #777; line-height: 1.15; font-style: italic; }
.reg-table td.cell.sig .coef { color: #185fa5; }
.reg-table td.cell.sep { color: #999; font-style: italic; font-size: 12px; padding-top: 12px; }
.reg-table td.cell.dash { color: #bbb; font-size: 12px; }
.reg-table tfoot td { padding: 6px 12px; font-size: 12px; color: #555; }
.reg-table tfoot tr.fitline td { border-top: 1px solid rgba(0,0,0,0.18); font-weight: 500; color: #333; padding-top: 10px; }
.reg-table tfoot tr.fitline td.cell { font-variant-numeric: tabular-nums; text-align: right; }
.reg-star { color: #185fa5; font-weight: 600; }
.reg-footer { font-size: 12px; color: #555; margin-top: 14px; line-height: 1.55; }
.reg-footer code { background: #f3f1eb; padding: 1px 5px; border-radius: 3px; font-size: 11px; }
details.lr-test { margin-top: 12px; }
details.lr-test summary { cursor: pointer; font-size: 12px; color: #185fa5; padding: 4px 0; }
details.lr-test .lr-body { font-size: 12px; color: #555; padding: 8px 0 4px; line-height: 1.6; }

/*VOTING:BEGIN*/
/* ---- Vote widget ---- */
.vote-btn { display: inline-block; padding: 3px 10px; font-size: 11px; border: 0.5px solid rgba(0,0,0,0.2); background: #fff; border-radius: 999px; cursor: pointer; color: #1a1a1a; text-decoration: none; }
.vote-btn:hover { background: #faf8f2; }
.vote-btn.voted { background: #eef3e6; border-color: #c5d7a8; color: #3b6d11; cursor: default; }
.vote-modal-overlay { position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.45); display: none; align-items: flex-start; justify-content: center; z-index: 999; padding: 24px; overflow-y: auto; }
.vote-modal-overlay.show { display: flex; }
.vote-modal { background: #fff; max-width: 720px; width: 100%; border-radius: 12px; padding: 24px; box-shadow: 0 12px 48px rgba(0,0,0,0.2); max-height: calc(100vh - 48px); overflow-y: auto; }
.vote-modal h3 { margin: 0 0 4px; font-size: 18px; font-weight: 500; }
.vote-modal .vm-meta { color: #777; font-size: 12px; margin-bottom: 14px; }
.vote-modal .vm-body { background: #f7f5ef; border-radius: 8px; padding: 14px 16px; font-size: 13px; line-height: 1.6; white-space: pre-wrap; max-height: 280px; overflow-y: auto; margin-bottom: 16px; color: #2a2a2a; }
.vote-modal .vm-section { margin-top: 14px; }
.vote-modal .vm-section h4 { margin: 0 0 8px; font-size: 13px; font-weight: 500; color: #1a1a1a; }
.vote-modal .vm-section .lede { color: #666; font-size: 12px; margin-bottom: 10px; }
.vote-modal .likert { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.vote-modal .likert label { padding: 8px 4px; border: 0.5px solid rgba(0,0,0,0.15); border-radius: 6px; text-align: center; font-size: 11px; cursor: pointer; color: #444; background: #fff; }
.vote-modal .likert label.sel { background: #eaeef3; border-color: #185fa5; color: #185fa5; font-weight: 500; }
.vote-modal .likert input { display: none; }
.vote-modal .qs { display: grid; gap: 10px; }
.vote-modal .qs .q { display: grid; grid-template-columns: 1fr 200px; gap: 12px; align-items: center; font-size: 13px; color: #2a2a2a; }
.vote-modal .qs .triple { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; }
.vote-modal .qs .triple label { padding: 6px 4px; border: 0.5px solid rgba(0,0,0,0.15); border-radius: 6px; text-align: center; font-size: 11px; cursor: pointer; color: #555; background: #fff; }
.vote-modal .qs .triple label.sel { background: #eaeef3; border-color: #185fa5; color: #185fa5; font-weight: 500; }
.vote-modal .qs .triple input { display: none; }
.vote-modal .clarity { margin-top: 12px; display: flex; align-items: center; gap: 8px; font-size: 13px; color: #444; }
.vote-modal .vm-comment textarea { width: 100%; padding: 8px; border: 0.5px solid rgba(0,0,0,0.2); border-radius: 6px; font-family: inherit; font-size: 13px; resize: vertical; min-height: 60px; }
.vote-modal .vm-identity { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 6px; }
.vote-modal .vm-identity .field label { display: block; font-size: 11px; color: #888; margin-bottom: 4px; letter-spacing: 0.02em; text-transform: uppercase; }
.vote-modal .vm-identity .field input { width: 100%; padding: 8px 10px; border: 0.5px solid rgba(0,0,0,0.2); border-radius: 6px; font-family: inherit; font-size: 13px; color: #1a1a1a; background: #fff; }
.vote-modal .vm-identity .field input:focus { outline: 0; border-color: #185fa5; box-shadow: 0 0 0 2px rgba(24,95,165,0.1); }
.vote-modal .vm-identity .field input.invalid { border-color: #993c1d; }
.vote-modal .vm-identity .help { grid-column: 1 / -1; font-size: 11px; color: #888; margin-top: -4px; }
@media (max-width: 520px) { .vote-modal .vm-identity { grid-template-columns: 1fr; } }
.vote-modal .vm-actions { display: flex; gap: 10px; margin-top: 18px; justify-content: flex-end; }
.vote-modal .vm-actions button { padding: 8px 14px; border-radius: 8px; border: 0.5px solid rgba(0,0,0,0.2); background: #fff; cursor: pointer; font-size: 13px; }
.vote-modal .vm-actions button.primary { background: #1a1a1a; color: #fff; border-color: #1a1a1a; }
.vote-modal .vm-actions button.primary:disabled { background: #aaa; cursor: not-allowed; }
.vote-modal .vm-reveal { background: #fafaf7; border-radius: 8px; padding: 14px 16px; margin-top: 16px; font-size: 13px; }
.vote-modal .vm-reveal .row { display: grid; grid-template-columns: 140px 1fr; gap: 8px; padding: 4px 0; border: 0; }
.vote-modal .vm-reveal .row .lbl { color: #777; font-size: 12px; }
.vote-modal .vm-reveal .row .val { color: #1a1a1a; }
.vote-modal .vm-err { color: #993c1d; font-size: 12px; margin-top: 8px; }
.vote-modal .vm-banner { background: #fff7ec; color: #8a4f0a; padding: 8px 12px; border-radius: 6px; font-size: 12px; margin-bottom: 12px; }
.vote-cta { background: #f7f5ef; border-radius: 10px; padding: 16px 18px; margin: 0 0 24px; font-size: 13px; line-height: 1.5; color: #2a2a2a; }
.vote-cta strong { display: block; margin-bottom: 4px; font-size: 14px; color: #1a1a1a; }
.pill.hidden-stance { background: #efeae1; color: #999; letter-spacing: 2px; font-weight: 500; }
.blind-toggle { display: inline-block; margin-left: 12px; font-size: 12px; color: #185fa5; cursor: pointer; user-select: none; }
.blind-toggle:hover { text-decoration: underline; }
/*VOTING:END*/
.reg-footer { font-size: 12px; color: #666; margin: 12px 0 0; line-height: 1.55; }
.reg-footer code { background: #f0eee7; padding: 1px 5px; border-radius: 3px; font-size: 11px; }

</style>
</head>
<body>
<h1>SEC Semi-Annual Reporting Proposal Tracker <span style="color:#777; font-weight:400;">(S7-2026-15)</span></h1>

__TRAVEL_NOTICE__

<div class="intro">
  <p>In <strong>May 2026</strong> the SEC issued a proposal that would allow public companies to switch from quarterly (Form 10-Q) to semi-annual financial reporting (a new Form 10-S). From the date of publication, the public has <strong>60 days</strong> to comment on the proposal.</p>
  <p>This site was produced by <a href="https://fisher.osu.edu/people/zach.7" target="_blank" rel="noopener">Professor Tzachi Zach</a> at The Ohio State University Fisher College of Business as a public service to track the comment letters as they arrive, classify their positions, and surface patterns in the docket. A number of methodological decisions had to be made along the way — how to classify stance, how to bucket commenters by entity type, how to handle hedged or conditional letters — those decisions are explained below.</p>
  <p>Beyond the tracker itself, the project has two other goals. First, I hope it will encourage discussion among accounting academics about the proposal. The economic-analysis questions the proposal raises (short-termism, fraud risk, compliance burden, retail-investor protection) are central to what we study, and the comment period is a good moment to bring our expertise to bear. Second, it is quite interesting to test how well language-model classifiers handle regulatory text. With a few hundred letters and fast iteration, can we converge on classifier design choices that scale to future research? The site will be most relevant to accounting academics, auditors, preparers, financial analysts, IR professionals, and anyone who follows the SEC docket professionally.</p>
  <p>Comments, suggestions, or corrections welcome — <a href="#" id="feedback-open">send feedback here</a> or email <a href="mailto:zach.7@osu.edu?subject=S7-2026-15%20tracker%20feedback">zach.7@osu.edu</a>.</p>
</div>

<!-- Feedback modal -->
<div class="feedback-overlay" id="feedback-overlay" role="dialog" aria-modal="true">
  <div class="feedback-modal">
    <h3 style="margin:0 0 6px; font-size:18px; font-weight:500;">Send feedback</h3>
    <p style="margin:0 0 14px; color:#666; font-size:13px;">Thoughts on methodology, corrections to specific letters, suggestions for new charts — anything goes. Name and email are optional. We read every one.</p>

    <div class="feedback-grid">
      <div class="field">
        <label for="fb-name">Name</label>
        <input id="fb-name" type="text" maxlength="120" autocomplete="name" placeholder="Optional" />
      </div>
      <div class="field">
        <label for="fb-email">Email</label>
        <input id="fb-email" type="email" maxlength="200" autocomplete="email" placeholder="Optional — for a reply" />
      </div>
    </div>
    <div class="field" style="margin-top:10px;">
      <label for="fb-message">Message</label>
      <textarea id="fb-message" maxlength="3000" rows="6" placeholder="What's on your mind?"></textarea>
    </div>

    <div id="fb-err" style="color:#993c1d; font-size:12px; margin-top:8px; display:none;"></div>
    <div id="fb-ok" style="color:#3b6d11; font-size:12px; margin-top:8px; display:none;"></div>

    <div class="feedback-actions">
      <button id="fb-cancel">Cancel</button>
      <button id="fb-submit" class="primary">Send</button>
    </div>
  </div>
</div>

<p class="meta" id="meta">Loading…</p>

<div class="cards" id="cards"></div>

__FORM_LETTER_PANEL__

<details class="methodology">
  <summary>Thanks</summary>
  <div class="body">
    Thanks to <strong>Mert Erinc</strong> and <strong>Brian Monsen</strong> for helpful comments and suggestions on the classification methodology.
  </div>
</details>

<details class="methodology">
  <summary>How <span class="kw-stance">stances</span> are classified <span class="accordion-meta">(three-rater LLM ensemble)</span></summary>
  <div class="body">
    I had three Claude raters classify each letter independently. The headline stance shown here is the <strong>majority vote</strong> across the three. The LLM-annotation literature (Carlson &amp; Burbano, <em>SMJ</em> 2026; Liu, <em>CHB</em> 2026) recommends multi-prompt validation over a single classifier call, and that is what this design does.

    <dl>
      <dt>Rater 1 — Primary</dt>
      <dd>Balanced read of the whole letter. Assigns Support / Oppose / Conditional based on the dominant position.</dd>
      <dt>Rater 2 — Literalist</dt>
      <dd>Defaults to Oppose. Flips to Support only on explicit, unconditional endorsement language ("I support…", "I urge the Commission to adopt…"). Conditional only fires on explicit "if X then yes" structure.</dd>
      <dt>Rater 3 — Skeptic</dt>
      <dd>Defaults to Conditional unless the letter is unambiguous. Any qualification, concession, or alternative proposal flips the call to Conditional.</dd>
    </dl>

    <div style="margin-top:14px; padding-top:12px; border-top: 0.5px solid rgba(0,0,0,0.08);">
      <strong>Agreement across the three raters (N = METHOD_N):</strong>
      <ul style="margin: 6px 0 0; padding-left: 20px; color: #444;">
        <li>Unanimous: METHOD_UNANIMOUS_N (METHOD_UNANIMOUS_PCT%)</li>
        <li>2-of-3 majority: METHOD_MAJORITY_N (METHOD_MAJORITY_PCT%)</li>
        <li>Fleiss' κ: METHOD_FLEISS_K · pairwise Cohen's κ: Primary–Literalist METHOD_K_PL, Primary–Skeptic METHOD_K_PS, Literalist–Skeptic METHOD_K_LS</li>
      </ul>
      <p style="margin: 8px 0 0; color: #666; font-size: 12px;">Each letter card in the table below carries an agreement badge (Unanimous / 2-of-3) and shows all three rater calls on hover.</p>
    </div>

    <div style="margin-top:14px; padding-top:12px; border-top: 0.5px solid rgba(0,0,0,0.08);">
      <strong>Cross-model validation (ChatGPT-5.5, n = 137 overlap).</strong>
      <p style="margin: 6px 0 0;">I then ran the same 3 rubric prompts through ChatGPT-5.5 as an independent second ensemble. The question I wanted to answer: would the stance calls hold up under a different model family? Carlson &amp; Burbano (<em>SMJ</em> 2026) recommend this kind of cross-model check where feasible.</p>
      <p style="margin: 10px 0 0;"><strong>GPT-Majority vs Claude-Majority: 132 / 137 = 96.4% raw, Cohen's κ = 0.886.</strong> Substantial cross-model agreement on the aggregated label.</p>
      <p style="margin: 10px 0 4px;">Per-rubric agreement varies:</p>
      <ul style="margin: 0 0 0; padding-left: 20px; color: #444;">
        <li>GPT-Primary vs Claude-Primary: κ = 0.816 (substantial)</li>
        <li>GPT-Literalist vs Claude-Literalist: κ = 0.635 (moderate-substantial)</li>
        <li>GPT-Skeptic vs Claude-Skeptic: κ = 0.400 (moderate)</li>
      </ul>
      <p style="margin: 10px 0 0;">The Skeptic divergence reflects a rubric-conditioning effect. The same "default to Conditional unless unambiguous" instruction yielded 83 Conditional calls in GPT-5.5 versus 36 in Claude Opus 4.7. Same prompt, different operationalization across model families. Aggregate agreement on the majority vote holds; per-rubric agreement is more model-dependent.</p>
      <p style="margin: 10px 0 0;">5 letters fall outside the cross-model majority match: #2 Fardeen Irani, #13 Skyler Mathis, #43 Steven A. Collazo, #80 Bayo Olabisi, #122 Tal Madison. All 5 push from Claude's Support or Oppose call into GPT's Conditional call. 4 of the 5 already had at least one Claude rater calling Conditional, so the cross-model disagreement concentrates on the hedge-boundary letters Claude's own ensemble was already split on.</p>
      <p style="margin: 10px 0 0;">I read all 5 of these letters by hand. On every one, Claude-Majority is the call I would have made; GPT-Majority is not. The uniform GPT failure mode: it treats any structural alternative or rhetorical hedge in the letter body as evidence of conditionality, even when the author's stated position is unambiguous. Five letters is a small validation set, but the direction is one-sided.</p>
    </div>

    <div style="margin-top:14px;">
      <strong>Stance label conventions:</strong>
      <dl style="margin-top: 6px;">
        <dt><span class="dot" style="background:#993c1d"></span>Oppose</dt>
        <dd>Author argues against adoption.</dd>
        <dt><span class="dot" style="background:#3b6d11"></span>Support</dt>
        <dd>Author explicitly endorses the proposal.</dd>
        <dt><span class="dot" style="background:#a8830d"></span>Conditional <span style="color:#777; font-weight:400;">(in-between / mixed)</span></dt>
        <dd>Author wants modifications or alternatives (e.g. enhanced auditor assurance, monthly revenue disclosure, every-4-months cadence, qualifying-criteria framework). Would not vote yes on the rule as written.</dd>
      </dl>
    </div>
  </div>
</details>

<details class="methodology">
  <summary>How <span class="kw-commenters">commenters</span> <span class="accordion-meta">(entity)</span> are classified <span class="accordion-meta">(three-rater LLM ensemble)</span></summary>
  <div class="body">
    Letters fall into one of nine buckets by <strong>who is writing</strong>. As with stance, three rubrics classify each letter independently, and the headline bucket is the <strong>majority of three</strong>. A colleague with FASB comment-letter experience helped refine the taxonomy.

    <div style="margin-top: 10px;"><strong>The nine buckets:</strong></div>
    <ol style="margin: 6px 0 14px 18px; padding: 0; color: #444;">
      <li><strong>Individual</strong> — default dump bucket. We use "Individual" (not "Individual investor").</li>
      <li><strong>Accountant (CPA)</strong> — CPA or chartered accountant credential, speaking from that professional lens.</li>
      <li><strong>Issuer / Corporate — current</strong> — active corporate role (CFO, audit chair, financial reporting manager, etc.).</li>
      <li><strong>Issuer / Corporate — former</strong> — retired or former executives writing personally. Plausibly different incentives from current insiders.</li>
      <li><strong>Investment professional</strong> — active asset managers, hedge fund principals, RIAs, financial advisors.</li>
      <li><strong>Academic researcher</strong> — university faculty appointment.</li>
      <li><strong>Industry practitioner / technologist</strong> — non-academic professional roles outside corporate-issuer / investment-firm worlds (CISSP, software developer, IT auditor, compliance professional, etc.).</li>
      <li><strong>Legal practitioner</strong> — law firms, securities/corporate attorneys, and bar-association committees writing in a legal capacity (added 2026-06-04, carried over from the 2018 S7-26-18 rubric).</li>
      <li><strong>Student</strong> — currently enrolled student.</li>
    </ol>

    <dl>
      <dt>Rater 1 — Primary</dt>
      <dd>Balanced read. Uses the "follow the letterhead" principle as a tiebreaker: classify by the affiliation under which the writer is <em>speaking</em>. The institutional-vs-personal call comes from register, length, substance, and whether the institution is named for credibility or for attribution.</dd>
      <dt>Rater 2 — Self-described</dt>
      <dd>Takes the literal first identifier the writer offers. "CPA and retail investor" → Accountant; "Individual investor and former CFO" → Individual. No override based on context.</dd>
      <dt>Rater 3 — Letterhead / functional</dt>
      <dd>Overrides self-description with the strongest functional credential. Priority: current institutional role &gt; former institutional role &gt; formal professional credential &gt; sector descriptor &gt; self-id.</dd>
    </dl>

    <div style="margin-top:14px; padding-top:12px; border-top: 0.5px solid rgba(0,0,0,0.08);">
      <strong>Agreement across the three raters (N = METHOD_ENT_N):</strong>
      <ul style="margin: 6px 0 0; padding-left: 20px; color: #444;">
        <li>Unanimous: METHOD_ENT_UNANIMOUS_N (METHOD_ENT_UNANIMOUS_PCT%)</li>
        <li>2-of-3 majority: METHOD_ENT_MAJORITY_N (METHOD_ENT_MAJORITY_PCT%)</li>
        <li>Fleiss' κ: METHOD_ENT_FLEISS_K</li>
      </ul>
      <p style="margin: 8px 0 0; color: #666; font-size: 12px;">Substantially higher agreement than the stance ensemble (κ = METHOD_FLEISS_K). Majority headline distribution: METHOD_ENT_DIST.</p>
    </div>

    <div style="margin-top:14px; padding-top:12px; border-top: 0.5px solid rgba(0,0,0,0.08);">
      <strong>Cross-model validation (ChatGPT-5.5, n = 137 overlap).</strong>
      <p style="margin: 6px 0 0;">The same 3 rubric prompts ran through ChatGPT-5.5 as an independent second ensemble.</p>
      <p style="margin: 10px 0 0;"><strong>GPT-Majority vs Claude-Majority: 114 / 137 = 83.2%, Cohen's κ = 0.621.</strong> Moderate cross-model agreement on the aggregated label.</p>
      <p style="margin: 10px 0 4px;">Per-rubric agreement:</p>
      <ul style="margin: 0 0 0; padding-left: 20px; color: #444;">
        <li>GPT-Primary vs Claude-Primary: κ = 0.657 (substantial)</li>
        <li>GPT-Self-described vs Claude-Self-described: κ = 0.593 (moderate-substantial)</li>
        <li>GPT-Letterhead vs Claude-Letterhead: κ = 0.584 (moderate-substantial)</li>
      </ul>
      <p style="margin: 10px 0 0;">The pattern is systematic. GPT-5.5 has a stronger "Individual" prior than Claude Opus 4.7 across all three rubrics. The biggest split is on writers who sign as "CFO, ACME Corp" or similar institutional role but write in a personal register engaging investor-protection concerns rather than issuer-specific concerns: GPT-Primary classifies as Individual; Claude-Primary classifies as Issuer-current. Both readings are defensible under the rubric. The rubric requires a "speaking-as" judgment, and the two model families weight surface role vs register differently.</p>
      <p style="margin: 10px 0 0;">Intra-model Fleiss κ is 0.880 for Claude and 0.775 for GPT. Within-model agreement holds for both ensembles; the divergence is across model families.</p>
      <p style="margin: 10px 0 0;">23 letters fall outside the cross-model majority match. 18 of 23 flow into GPT-Individual from a more specific Claude bucket. 6 of these 23 are already on the contested-letters list internal to Claude's own three-rater ensemble.</p>
    </div>
  </div>
</details>

<details class="methodology">
  <summary>How <span class="kw-rationales">rationales</span> are classified <span class="accordion-meta">(argument taxonomy anchored on the SEC release; three-rater LLM ensemble)</span></summary>
  <div class="body">
    Each letter can invoke one or more argument families. The taxonomy starts from the SEC's framing in the proposing release (Release Nos. 33-11414; 34-105368; File No. S7-2026-15). Four commenter-distinctive codes cover arguments the SEC does not engage as standalone justifications. <strong>22 codes total:</strong> 16 SEC-engaged (9 anti-proposal, 5 pro-proposal, 1 conditional, 1 procedural), 4 commenter-distinctive (<em>IP</em> investor protection; <em>US</em> capital-market leadership; <em>RI</em> investor reliance interests; <em>PP</em> political pressure / regulatory capture), 1 "no substantive rationale" for letters that state a position without engaging an argument, and <em>GU</em> (guidance vs reporting) carried from the 2018 (S7-26-18) rubric for cross-tracker consistency (not yet invoked in the 2026 corpus). <em>PP</em> was promoted from a §6.6 watch item to a coded rationale on 2026-06-04; the cross-model κ figures below describe the original 20-code validation set and do not include it.

    <p style="margin: 12px 0 0;">Anti-proposal codes use a red shade and pro-proposal codes a green shade, so the directional balance reads at a glance. Every SEC-engaged code carries a verbatim quote from the proposing release. The quote shows how the SEC itself frames the argument.</p>

    <div style="margin-top: 16px; padding-top: 14px; border-top: 0.5px solid rgba(0,0,0,0.08);">
      <strong>Three-rater LLM ensemble.</strong> Rationale coding is multi-label: a letter can invoke 0+ codes. Three rubrics classify each letter independently, and the public-facing code list is the per-(letter, code) <strong>majority vote</strong> across the three.
      <dl style="margin-top: 10px;">
        <dt>Rater 1 — Primary</dt>
        <dd>Balanced read. Codes the rationale families the writer substantively argues, even when not framed in the SEC's exact language.</dd>
        <dt>Rater 2 — Literalist</dt>
        <dd>Strict. Codes a family <em>only</em> when the letter explicitly invokes that framing in surface text.</dd>
        <dt>Rater 3 — Inclusive</dt>
        <dd>Expansive. Codes a family whenever plausibly invoked, including allusive references and arguments the writer relies on without fully developing.</dd>
      </dl>
    </div>

    <div style="margin-top: 14px;">
      <strong>Agreement across the three raters (N = METHOD_RAT_N):</strong>
      <ul style="margin: 6px 0 0; padding-left: 20px; color: #444;">
        <li>Unanimous (all three raters produced identical code sets): METHOD_RAT_UNANIMOUS_N (METHOD_RAT_UNANIMOUS_PCT%)</li>
        <li>2-of-3 majority: METHOD_RAT_MAJORITY_N (METHOD_RAT_MAJORITY_PCT%)</li>
        <li>Split (three different code sets): METHOD_RAT_SPLIT_N (METHOD_RAT_SPLIT_PCT%)</li>
        <li>Mean per-code Cohen's κ across pairs: <strong>METHOD_RAT_MEAN_K</strong>. Substantial agreement, in line with multi-prompt LLM-annotation benchmarks.</li>
      </ul>
    </div>

    <div style="margin-top: 14px;">
      <strong>Per-code Cohen's κ</strong> (binary code-present vs absent, mean across the three pairwise comparisons). Surface-readable codes have high κ; inferential codes have lower κ. The methodology surfaces the structure of the taxonomy.
      <div style="margin: 8px 0 0; padding: 10px 12px; background: #f7f5ef; border-radius: 6px; font-size: 12px; line-height: 1.6; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: #2a2a2a;">
        METHOD_RAT_PERCODE
      </div>
      <p style="margin: 8px 0 0; color: #666; font-size: 12px;">METHOD_RAT_FREQNOTE</p>
    </div>

    <div style="margin-top:14px; padding-top:12px; border-top: 0.5px solid rgba(0,0,0,0.08);">
      <strong>Cross-model validation (ChatGPT-5.5, n = 137 overlap).</strong>
      <p style="margin: 6px 0 0;">The same 3 rubric prompts ran through ChatGPT-5.5 as an independent second ensemble.</p>
      <p style="margin: 10px 0 0;"><strong>GPT-Majority vs Claude-Majority: mean per-code Cohen's κ = 0.477.</strong> Moderate cross-model agreement, lower than the stance ensemble (κ = 0.886) and the entity ensemble (κ = 0.621). The ranking is consistent with rationale being the most inferential and multi-label of the three ensembles. Set-level exact match (GPT majority code set identical to Claude majority code set): 34 of 137 letters, 24.8%. Mean Jaccard similarity between the two majority sets: 0.52.</p>
      <p style="margin: 10px 0 4px;">Per-rubric mean κ across the 20 codes:</p>
      <ul style="margin: 0 0 0; padding-left: 20px; color: #444;">
        <li>GPT-Primary vs Claude-Primary: κ = 0.483</li>
        <li>GPT-Literalist vs Claude-Literalist: κ = 0.365</li>
        <li>GPT-Inclusive vs Claude-Inclusive: κ = 0.361</li>
      </ul>
      <p style="margin: 10px 0 0;">Surface-readable codes converge across model families: MF (κ = 0.79), CMP (κ = 0.76), FR (κ = 0.70), LE (κ = 0.70), NR (κ = 0.60). Inferential or umbrella codes diverge: EX (κ = 0.20), IP (κ = 0.32), OP (κ = 0.32), AU (κ = 0.39).</p>
      <p style="margin: 10px 0 0;">The rubric-conditioning pattern visible in the stance and entity ensembles shows up again. GPT-Inclusive fires 4.50 codes per letter; Claude-Inclusive fires 2.84. Same "code whenever plausibly invoked" instruction, very different operationalization. Claude's three rationale raters stay within a 25% spread of each other (2.25 to 2.84 codes per letter); GPT's three span nearly 2x (2.44 to 4.50). The 3-rater majority κ (0.477) is higher than two of the three matched-rubric κs, which shows that aggregation dampens cross-model variance just as it does within-model.</p>
    </div>

    <p style="margin: 14px 0 0;">
      <a href="rationale-taxonomy.html" style="display: inline-block; padding: 7px 14px; background: #1a1a1a; color: #fff; border-radius: 8px; text-decoration: none; font-size: 13px;">Full argument taxonomy with SEC quotes &rarr;</a>
    </p>
  </div>
</details>

<div class="section">
  <h2>Letters per day</h2>
  <div class="legend" id="legend"></div>
  <div class="chart-wrap"><canvas id="byDayChart" role="img" aria-label="Stacked bar chart of comment letters received per day, broken down by stance"></canvas></div>
</div>

<div class="section">
  <h2>Stance totals</h2>
  <div class="chart-wrap short"><canvas id="stanceChart" role="img" aria-label="Horizontal bar chart of letters by stance with percentages"></canvas></div>
  <ul class="stance-list" id="stance-list"></ul>
</div>

<div class="section">
  <h2>Stance by entity type</h2>
  <p class="lede" style="margin: 0 0 12px;">Letters grouped by who submitted them, color-coded by stance.</p>
  <div class="chart-wrap"><canvas id="entityChart" role="img" aria-label="Stacked bar chart of letters grouped by entity type, with each bar segmented by stance"></canvas></div>
</div>

<div class="section">
  <h2>Stance by letter length</h2>
  <p class="lede" style="margin: 0 0 12px;">Letters grouped by word count, color-coded by stance.</p>
  <div class="chart-wrap"><canvas id="bucketChart" role="img" aria-label="Stacked bar chart of letters grouped into word-count buckets, with each bar segmented by stance"></canvas></div>
</div>

<div class="section">
  <h2>Letter length by entity type</h2>
  <p class="lede" style="margin: 0 0 12px;">For each entity type, how its letters distribute across word-count buckets.</p>
  <div style="display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: #555; margin-bottom: 10px;"><span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;background:#B5D4F4;border-radius:2px;"></span>1–50w</span><span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;background:#85B7EB;border-radius:2px;"></span>51–150w</span><span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;background:#378ADD;border-radius:2px;"></span>151–300w</span><span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;background:#185FA5;border-radius:2px;"></span>301–600w</span><span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;background:#0C447C;border-radius:2px;"></span>600+w</span></div>
  <div class="chart-wrap" style="height: 280px;"><canvas id="entityLenChart" role="img" aria-label="Horizontal stacked bar chart showing distribution of letter word-counts within each entity type"></canvas></div>
</div>

<div class="section">
  <h2>Regression: predictors of stance — three specifications</h2>
  <p class="lede" style="margin: 0 0 12px;">Same predictors across all three models (7 entity dummies with Individual as reference, plus log(words+1)). The Logit and LPM share a binary outcome (Support=1 / Oppose=0, Conditional dropped). The ordinal logit uses the full 3-class outcome (Oppose &lt; Conditional &lt; Support). Each cell shows coefficient on top, SE in parentheses below, p-value in italics underneath.</p>
__REGRESSION_PANEL__
</div>

<!--DEV_ONLY:BEGIN-->
<div class="section">
  <h2>Rationales cited</h2>
  <p class="lede" style="margin: 0 0 12px;">Each letter can invoke zero or more argument families (multi-label). 22-code taxonomy anchored on the SEC's proposing release — see the <a href="rationale-taxonomy.html">argument taxonomy</a> for code definitions and verbatim SEC quotes.</p>
  <div class="chart-wrap" style="height: 420px;"><canvas id="rationaleChart"></canvas></div>
  <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 11px; color: #555; margin-top: 10px;">
    <span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;background:#993c1d;border-radius:2px;"></span>Anti-proposal (red scale)</span>
    <span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;background:#3b6d11;border-radius:2px;"></span>Pro-proposal (green scale)</span>
    <span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;background:#a8830d;border-radius:2px;"></span>Conditional</span>
    <span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;background:#185fa5;border-radius:2px;"></span>Procedural / legal</span>
    <span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;background:#888780;border-radius:2px;"></span>No rationale</span>
  </div>

  <div id="rationale-zero-note" class="rat-zero-note"></div>
</div>

<div class="section">
  <h2>Rationales by stance</h2>
  <p class="lede" style="margin: 0 0 12px;">Same rationales, stacked by the stance of the letter that cited them. Hover any code pill on the y-axis for a short explanation.</p>
  <div class="chart-wrap" style="height: 420px; position: relative;"><canvas id="rationaleStanceChart"></canvas></div>
</div>

<div id="rationale-tooltip"></div>
<!--DEV_ONLY:END-->

<div class="section">
  <h2>Longest letters by stance</h2>
  <p class="lede" style="margin: 0 0 14px; font-size: 13px; color: #555;">Top 5 longest letters within each stance bucket. The substantive intellectual center of each side reads at a glance.</p>
  <div id="longest"></div>
</div>

<div class="section">
  <h2>All letters</h2>
  <!--VOTING:BEGIN-->
  <div class="vote-cta" id="vote-cta">
    <strong>Help validate the classification.</strong>
    Classifying these letters as Support / Oppose / Conditional is inherently subjective. We've already done it three different ways (see methodology above). You can disagree. To keep your judgment independent, our stance for each letter is hidden until you vote on it. Click <em>Vote</em> on any row to read the letter, judge it on the underlying issues, then see how we coded it and how other readers have voted.
    <div style="margin-top: 10px;">
      <span id="blind-toggle" class="blind-toggle">Show all classifications (turn off blind mode)</span>
    </div>
  </div>
  <!--VOTING:END-->
  <p class="lede" style="margin: 0 0 10px; font-size: 13px; color: #555;">
    Each letter is classified three times for stance, entity, and rationales, each time by a different Claude rubric. The small pill next to each value shows whether the three raters agreed: <strong>Unanimous</strong> (all three matched), <strong>2 of 3</strong> (majority match), or <strong>Split</strong> (all three differed, rationales only). See the methodology sections above for the rubric details.
  </p>
  <div class="search-row">
    <div class="search" style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
      <select id="entsel" style="padding:7px 10px;border:0.5px solid rgba(0,0,0,0.2);border-radius:6px;font-size:13px;background:#fff;color:#1a1a1a;"></select>
      <input id="q" type="search" placeholder="Search by name, role, stance, or rationale code (e.g. PP, MF)…" style="flex:1;min-width:200px;" />
    </div>
    <button id="expand-toggle" class="expand-toggle" type="button">Expand all</button>
  </div>
  <table class="full" id="full">
    <thead><tr>
      <th data-k="n">#</th>
      <th data-k="date">Date</th>
      <th data-k="name">Commenter</th>
      <th data-k="role">Role</th>
      <th data-k="stance">Stance</th>
      <th data-k="words" class="right">Words</th>
      <!--DEV_ONLY:BEGIN--><th>Rationales</th><!--DEV_ONLY:END-->
      <!--VOTING:BEGIN--><th>Judge</th><!--VOTING:END-->
    </tr></thead>
    <tbody id="full-body"></tbody>
  </table>
</div>

<!--VOTING:BEGIN-->
<!-- Vote modal -->
<div class="vote-modal-overlay" id="vote-overlay" role="dialog" aria-modal="true">
  <div class="vote-modal" id="vote-modal">
    <div id="vote-banner" class="vm-banner" style="display:none;"></div>
    <h3 id="vm-title"></h3>
    <div class="vm-meta" id="vm-meta"></div>
    <div class="vm-body" id="vm-body">Loading letter body…</div>

    <div class="vm-section">
      <h4>Overall stance — where does this letter fall?</h4>
      <p class="lede">Pick one. Don't see our coding yet — we want your independent read first.</p>
      <div class="likert" id="vm-likert">
        <label data-v="-2"><input type="radio" name="likert" value="-2">Strongly oppose</label>
        <label data-v="-1"><input type="radio" name="likert" value="-1">Lean oppose</label>
        <label data-v="0"><input type="radio" name="likert" value="0">Conditional</label>
        <label data-v="1"><input type="radio" name="likert" value="1">Lean support</label>
        <label data-v="2"><input type="radio" name="likert" value="2">Strongly support</label>
      </div>
      <div class="clarity">
        <input type="checkbox" id="vm-clear" checked>
        <label for="vm-clear">The author's position was clear to me</label>
      </div>
    </div>

    <div class="vm-section">
      <h4>What does the letter say about each issue?</h4>
      <p class="lede">For each, mark Yes / No / Not mentioned. Skip what you're unsure about — those default to Not mentioned.</p>
      <div class="qs" id="vm-qs"></div>
    </div>

    <div class="vm-section">
      <h4>Who's voting? (optional)</h4>
      <p class="lede">If you'd like your name attached to your votes — useful for academics or commenters who want to be cited. Email is never displayed publicly.</p>
      <div class="vm-identity">
        <div class="field">
          <label for="vm-name">Name</label>
          <input id="vm-name" type="text" maxlength="120" autocomplete="name" placeholder="Optional" />
        </div>
        <div class="field">
          <label for="vm-email">Email</label>
          <input id="vm-email" type="email" maxlength="200" autocomplete="email" placeholder="Optional" />
        </div>
        <div class="help">We remember these in your browser so you don't have to retype each time. Leave both blank to stay anonymous.</div>
      </div>
    </div>

    <div class="vm-section vm-comment">
      <h4>Anything else? (optional, &lt;500 chars)</h4>
      <textarea id="vm-comment" maxlength="500" placeholder="One-line note on what made this letter interesting (or hard to classify)."></textarea>
    </div>

    <div class="vm-err" id="vm-err" style="display:none;"></div>

    <div class="vm-actions">
      <button id="vm-cancel">Cancel</button>
      <button id="vm-submit" class="primary" disabled>Submit &amp; reveal</button>
    </div>

    <div class="vm-reveal" id="vm-reveal" style="display:none;"></div>
  </div>
</div>
<!--VOTING:END-->

<p class="footer">
  Source: <a href="https://www.sec.gov/rules-regulations/public-comments/s7-2026-15" target="_blank" rel="noopener">SEC.gov — Comments on S7-2026-15</a> · Snapshot as of <span id="asof">__ASOF__</span> · Built by <a href="https://fisher.osu.edu/people/zach.7" target="_blank" rel="noopener">Tzachi Zach</a> (<a href="https://www.linkedin.com/in/tzachi-zach-85aa482/" target="_blank" rel="noopener">LinkedIn</a>) with <a href="https://claude.com/" target="_blank" rel="noopener">Claude</a>.
</p>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
<script>
const RECORDS = __RECORDS__;

/*VOTING:BEGIN*/
// These constants must be declared BEFORE renderTable() runs, since voteButton() reads them.
// (const declarations don't hoist; placing them later causes a temporal-dead-zone error.)
const SUPABASE_URL = "__SUPABASE_URL__";
const SUPABASE_KEY = "__SUPABASE_ANON_KEY__";
const BODIES_INLINE = __BODIES_INLINE__;
const BODIES_URL = "bodies.json";
const SUPABASE_LIVE = SUPABASE_URL && SUPABASE_URL.startsWith("https://") && SUPABASE_KEY && SUPABASE_KEY.length > 20;
const VOTE_ENABLED = true;

// Blind mode: hide our coding in the table until the visitor has voted on each letter.
// Visitor can flip with the "Show all" link above the table; choice persists in localStorage.
let BLIND_MODE = true;
try {
  const saved = localStorage.getItem('sec_blind_mode');
  if (saved === '0') BLIND_MODE = false;
} catch(e) {}

// Voted-set helpers — must be defined early since stanceCell() reads them via getVotedSet().
function getVotedSet() {
  try { return new Set(JSON.parse(localStorage.getItem('sec_voted_on') || '[]')); }
  catch(e) { return new Set(); }
}
function markVoted(n) {
  const s = getVotedSet(); s.add(n);
  try { localStorage.setItem('sec_voted_on', JSON.stringify([...s])); } catch(e) {}
}
/*VOTING:END*/
const STANCE_COLORS = { 'Oppose':'#993c1d', 'Support':'#3b6d11', 'Conditional':'#a8830d', 'PDF — not parsed':'#888780' };
const STANCE_ORDER = ['Oppose','Conditional','Support','PDF — not parsed'];

function pct(n,t) { return t===0?'0%':Math.round(n/t*100)+'%'; }
function pillClass(s) { return s==='PDF — not parsed' ? 'PDF' : s; }
function fmtMonthDay(d) {
  const m = d.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return d;
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return months[parseInt(m[2],10)-1] + ' ' + parseInt(m[3],10);
}
function escape(s) { return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function stanceCellRevealed(r) {
  const pill = '<span class="pill '+pillClass(r.stance)+'">'+escape(r.stance)+'</span>';
  if (!r.literalist || !r.skeptic) return pill;
  const agree = r.agreement === 'unanimous' ? 'Unanimous' : '2 of 3';
  const badgeBg = r.agreement === 'unanimous' ? '#e8eee0' : '#f4eedb';
  const badgeColor = r.agreement === 'unanimous' ? '#3b6d11' : '#854f0b';
  const tooltip = 'Primary: '+r.primary+' | Literalist: '+r.literalist+' | Skeptic: '+r.skeptic;
  const badge = '<span class="agreement-badge" title="'+escape(tooltip)+'" style="display:inline-block; font-size:10px; padding:1px 6px; margin-left:6px; border-radius:8px; background:'+badgeBg+'; color:'+badgeColor+'; vertical-align:middle;">'+agree+'</span>';
  return pill + badge;
}
function stanceCell(r) {
  // In blind mode (the default), our coding is hidden on rows the visitor hasn't voted on yet.
  // Voted rows reveal. Visitor can override with the "Show all" link at the top of the table.
  /*VOTING:BEGIN*/
  const blindMode = (typeof BLIND_MODE !== 'undefined') ? BLIND_MODE : true;
  const voted = (typeof getVotedSet === 'function') ? getVotedSet().has(r.n) : false;
  if (blindMode && !voted) {
    return '<span class="pill hidden-stance" title="Click Vote to reveal our coding">·&nbsp;·&nbsp;·</span>';
  }
  /*VOTING:END*/
  return stanceCellRevealed(r);
}

// Entity agreement badge (parallel to the stance one). Shows Unanimous / 2 of 3
// next to the entity bucket; tooltip on hover lists the three rater calls.
function entityBadge(r) {
  if (!r.entity_agreement) return '';
  const agree = r.entity_agreement === 'unanimous' ? 'Unanimous' : '2 of 3';
  const badgeBg    = r.entity_agreement === 'unanimous' ? '#e8eee0' : '#f4eedb';
  const badgeColor = r.entity_agreement === 'unanimous' ? '#3b6d11' : '#854f0b';
  const tooltip = 'Entity (majority): ' + (r.entity || '—')
    + ' | Primary: ' + (r.entity_primary || '—')
    + ' | Self-described: ' + (r.entity_selfdescribed || '—')
    + ' | Letterhead: ' + (r.entity_letterhead || '—');
  return '<span class="agreement-badge" title="' + escape(tooltip)
    + '" style="display:inline-block; font-size:10px; padding:1px 6px; margin-left:6px; border-radius:8px; background:'
    + badgeBg + '; color:' + badgeColor + '; vertical-align:middle;">' + agree + '</span>';
}

// Role cell — shows the writer's self-described role on top, the entity bucket
// (with agreement badge) underneath in small gray. If role and entity are the
// same string, we render just one line + the badge to avoid duplication.
function roleCell(r) {
  const role   = escape(r.role || '');
  const entity = escape(r.entity || '');
  const badge  = entityBadge(r);
  if (!entity || role === entity) {
    return role + badge;
  }
  return role
    + '<div style="font-size:11px; color:#777; margin-top:3px;">'
    + entity + badge
    + '</div>';
}

function aggregate(records) {
  const byDate = {}, byStance = {};
  for (const r of records) {
    const d = r.date, s = r.stance;
    if (!byDate[d]) byDate[d] = {};
    byDate[d][s] = (byDate[d][s]||0)+1;
    byStance[s] = (byStance[s]||0)+1;
  }
  return { byDate, byStance, total: records.length };
}

const agg = aggregate(RECORDS);

document.getElementById('meta').textContent = 'Tracking ' + agg.total + ' letters · ' + Object.keys(agg.byDate).length + ' days of submissions';

document.getElementById('cards').innerHTML = [
  { label: 'Total letters', value: agg.total, sub: '', cls: '' },
  { label: 'Oppose', value: agg.byStance['Oppose']||0, sub: pct(agg.byStance['Oppose']||0, agg.total)+' of total', cls:'oppose' },
  { label: 'Support', value: agg.byStance['Support']||0, sub: pct(agg.byStance['Support']||0, agg.total)+' of total', cls:'support' },
  { label: 'Conditional', value: agg.byStance['Conditional']||0, sub: pct(agg.byStance['Conditional']||0, agg.total)+' of total', cls:'conditional' }
].map(c => '<div class="card '+c.cls+'"><p class="label">'+c.label+'</p><p class="value">'+c.value+'</p>'+(c.sub?'<p class="pct">'+c.sub+'</p>':'')+'</div>').join('');

document.getElementById('legend').innerHTML = STANCE_ORDER.filter(s=>agg.byStance[s]).map(s =>
  '<span><span class="swatch" style="background:'+STANCE_COLORS[s]+'"></span>'+s+'</span>'
).join('');

// Bail out of chart rendering gracefully if Chart.js failed to load (e.g. from file://
// with no internet). The rest of the page — methodology, table, vote widget — should
// still work. The hardening relies on a typeof check before each Chart() call below.
const HAS_CHART = (typeof Chart !== 'undefined');
if (!HAS_CHART) {
  console.warn('Chart.js failed to load — charts will be skipped. Table and vote widget still work.');
  document.querySelectorAll('canvas[id$="Chart"]').forEach(c => {
    const p = c.parentElement;
    if (p) p.innerHTML = '<div style="padding:12px; color:#888; font-size:12px;">Chart unavailable (Chart.js did not load).</div>';
  });
}

const dates = Object.keys(agg.byDate).sort();
if (HAS_CHART) new Chart(document.getElementById('byDayChart'), {
  type:'bar',
  data: { labels: dates.map(fmtMonthDay), datasets: STANCE_ORDER.map(s => ({
    label:s, data: dates.map(d=>agg.byDate[d][s]||0), backgroundColor: STANCE_COLORS[s]
  })) },
  options: { responsive:true, maintainAspectRatio:false, animation:{duration:200},
    scales:{ x:{stacked:true,ticks:{autoSkip:false}}, y:{stacked:true,beginAtZero:true,ticks:{precision:0}} },
    plugins:{legend:{display:false}, tooltip:{callbacks:{footer:items=>'Total: '+items.reduce((a,b)=>a+b.parsed.y,0)}}}
  }
});

const sLabels = STANCE_ORDER.filter(s=>agg.byStance[s]);
const sData = sLabels.map(s=>agg.byStance[s]);
const sColors = sLabels.map(s=>STANCE_COLORS[s]);
const labelPlugin = { id:'lbl', afterDatasetsDraw(c) {
  const ctx = c.ctx; const total = agg.total;
  c.data.datasets[0].data.forEach((v,i)=> {
    const m = c.getDatasetMeta(0).data[i]; if (!m) return;
    ctx.save();
    ctx.fillStyle='#1a1a1a';
    ctx.font='500 12px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign='left'; ctx.textBaseline='middle';
    ctx.fillText(v + '  (' + Math.round(v/total*100) + '%)', m.x+6, m.y);
    ctx.restore();
  });
}};
if (HAS_CHART) new Chart(document.getElementById('stanceChart'), {
  type:'bar',
  data: { labels: sLabels, datasets: [{ data: sData, backgroundColor: sColors }] },
  options: { indexAxis:'y', responsive:true, maintainAspectRatio:false, animation:{duration:200},
    layout:{padding:{right:60}},
    scales:{x:{beginAtZero:true,ticks:{precision:0},suggestedMax: Math.ceil(Math.max(...sData)*1.18)}},
    plugins:{legend:{display:false}}
  },
  plugins: [labelPlugin]
});

document.getElementById('stance-list').innerHTML = sLabels.map((s,i)=>
  '<li><span class="lbl"><span class="swatch" style="background:'+sColors[i]+'"></span>'+s+'</span>'+
  '<span class="num"><strong>'+sData[i]+'</strong> · '+pct(sData[i], agg.total)+'</span></li>'
).join('');

const ENTITY_ORDER = ['Individual','Accountant (CPA)','Issuer / Corporate — current','Issuer / Corporate — former','Investment professional','Academic researcher','Industry practitioner / technologist','Legal practitioner','Student','Other / Anonymous'];
const entityCounts = STANCE_ORDER.map(s => ENTITY_ORDER.map(_ => 0));
for (const r of RECORDS) {
  const i = ENTITY_ORDER.indexOf(r.entity || '');
  const j = STANCE_ORDER.indexOf(r.stance);
  if (i >= 0 && j >= 0) entityCounts[j][i]++;
}
const entityTotals = ENTITY_ORDER.map((_, i) => STANCE_ORDER.reduce((sum, s, j) => sum + entityCounts[j][i], 0));
const entityShown = ENTITY_ORDER.map((e, i) => ({e, total: entityTotals[i], idx: i})).filter(x => x.total > 0);
if (HAS_CHART) new Chart(document.getElementById('entityChart'), {
  type: 'bar',
  data: {
    labels: entityShown.map(x => x.e + ' (' + x.total + ')'),
    datasets: STANCE_ORDER.filter(s => agg.byStance[s]).map(s => ({
      label: s,
      data: entityShown.map(x => entityCounts[STANCE_ORDER.indexOf(s)][x.idx]),
      backgroundColor: STANCE_COLORS[s]
    }))
  },
  options: {
    responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
    indexAxis: 'y',
    scales: {
      x: { stacked: true, beginAtZero: true, ticks: { precision: 0 } },
      y: { stacked: true, ticks: { autoSkip: false } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => {
            const t = entityShown[ctx.dataIndex].total || 0;
            const v = ctx.parsed.x;
            const pct = t === 0 ? '0%' : Math.round(v / t * 100) + '%';
            return ctx.dataset.label + ': ' + v + ' (' + pct + ' of bucket)';
          },
          footer: items => 'Bucket total: ' + (entityShown[items[0].dataIndex].total || 0)
        }
      }
    }
  }
});

const BUCKETS = [
  {lo:1, hi:50, name:'1–50'},
  {lo:51, hi:150, name:'51–150'},
  {lo:151, hi:300, name:'151–300'},
  {lo:301, hi:600, name:'301–600'},
  {lo:601, hi:99999, name:'600+'}
];
function bucketIndex(w) { for (let i=0; i<BUCKETS.length; i++) { if (w >= BUCKETS[i].lo && w <= BUCKETS[i].hi) return i; } return -1; }
const bucketCounts = STANCE_ORDER.map(s => BUCKETS.map(_ => 0));
for (const r of RECORDS) {
  const i = bucketIndex(r.words || 0);
  const j = STANCE_ORDER.indexOf(r.stance);
  if (i >= 0 && j >= 0) bucketCounts[j][i]++;
}
const bucketTotals = BUCKETS.map((_, i) => STANCE_ORDER.reduce((sum, s, j) => sum + bucketCounts[j][i], 0));
if (HAS_CHART) new Chart(document.getElementById('bucketChart'), {
  type: 'bar',
  data: {
    labels: BUCKETS.map((b, i) => b.name + ' words (' + bucketTotals[i] + ')'),
    datasets: STANCE_ORDER.filter(s => agg.byStance[s]).map((s, i) => ({
      label: s,
      data: bucketCounts[STANCE_ORDER.indexOf(s)],
      backgroundColor: STANCE_COLORS[s]
    }))
  },
  options: {
    responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
    scales: {
      x: { stacked: true, ticks: { autoSkip: false } },
      y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => {
            const t = bucketTotals[ctx.dataIndex] || 0;
            const v = ctx.parsed.y;
            const pct = t === 0 ? '0%' : Math.round(v / t * 100) + '%';
            return ctx.dataset.label + ': ' + v + ' (' + pct + ' of bucket)';
          },
          footer: items => 'Bucket total: ' + (bucketTotals[items[0].dataIndex] || 0)
        }
      }
    }
  }
});

const LEN_COLORS = ['#B5D4F4','#85B7EB','#378ADD','#185FA5','#0C447C'];
const LEN_LABELS = BUCKETS.map(b => b.name + 'w');
const ENTITY_ORDER_CT = ['Individual','Accountant (CPA)','Issuer / Corporate — current','Issuer / Corporate — former','Investment professional','Academic researcher','Industry practitioner / technologist','Legal practitioner','Student','Other / Anonymous'];
const ctCounts = LEN_LABELS.map(_ => ENTITY_ORDER_CT.map(__ => 0));
const ctWords = ENTITY_ORDER_CT.map(_ => []);
for (const r of RECORDS) {
  const ei = ENTITY_ORDER_CT.indexOf(r.entity || '');
  const li = bucketIndex(r.words || 0);
  if (ei >= 0 && li >= 0) {
    ctCounts[li][ei]++;
    ctWords[ei].push(r.words || 0);
  }
}
const ctTotals = ENTITY_ORDER_CT.map((_, i) => LEN_LABELS.reduce((sum, l, li) => sum + ctCounts[li][i], 0));
const ctMedian = ctWords.map(arr => {
  if (!arr.length) return 0;
  const s = arr.slice().sort((a,b)=>a-b);
  return s[Math.floor(s.length/2)];
});
const ctShown = ENTITY_ORDER_CT.map((e, i) => ({e, total: ctTotals[i], idx: i, median: ctMedian[i]})).filter(x => x.total > 0);
if (HAS_CHART) new Chart(document.getElementById('entityLenChart'), {
  type: 'bar',
  data: {
    labels: ctShown.map(x => x.e + ' (' + x.total + ', median ' + x.median + 'w)'),
    datasets: LEN_LABELS.map((lab, li) => ({
      label: lab,
      data: ctShown.map(x => ctCounts[li][x.idx]),
      backgroundColor: LEN_COLORS[li]
    }))
  },
  options: {
    indexAxis: 'y',
    responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
    scales: {
      x: { stacked: true, beginAtZero: true, ticks: { precision: 0 } },
      y: { stacked: true, ticks: { autoSkip: false } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => {
            const t = ctShown[ctx.dataIndex].total || 0;
            const v = ctx.parsed.x;
            const pct = t === 0 ? '0%' : Math.round(v / t * 100) + '%';
            return ctx.dataset.label + ': ' + v + ' (' + pct + ' of entity)';
          },
          footer: items => 'Entity total: ' + (ctShown[items[0].dataIndex].total) + ' · median ' + ctShown[items[0].dataIndex].median + ' words'
        }
      }
    }
  }
});

/*DEV_ONLY:BEGIN*/
// Rationale taxonomy — 22 codes (PP promoted 2026-06-04; GU carried from the 2018 S7-26-18 rubric).
// Anti-proposal in the red scale, pro-proposal in the green scale.
// US, RI, and PP (commenter-distinctive) are anti-proposal arguments and get muted-red shades.
const RATIONALE_META = {
  // code: [long name, family group, color, short description]
  IP:  ['Investor protection / transparency',         'cd',   '#993c1d', 'Commenter-distinctive. Commenters argue the SEC’s investor-protection mandate weighs against reducing disclosure frequency. The release asserts IP won’t be undermined but does not engage the affirmative argument that it might be sacrificed.'],
  IA:  ['Info asymmetry / retail vs institutional',   'anti', '#ad4624', 'Institutional investors have expert networks, alternative data, and channel checks. The 10-Q is the leveling mechanism for retail investors.'],
  FR:  ['Fraud / insider-trading risk',               'anti', '#c1502b', 'Longer reporting gaps allow malfeasance to compound and widen the window for trading on undisclosed material information.'],
  MF:  ['Market function / price discovery',          'anti', '#d55a32', 'Less frequent information leads to wider bid-ask spreads, jump volatility, and prices deviating longer from fundamentals.'],
  AU:  ['Audit / verification',                       'anti', '#b06037', 'Limited-assurance auditor review is misaligned with a 6-month cadence; auditors may identify misstatements and ICFR deficiencies later.'],
  ICc: ['Intl evidence — cautionary',                 'anti', '#7a2a14', 'UK / Singapore semiannual experience cited as cautionary: Singapore reverting toward more frequent; lower trading volumes; hidden corporate problems.'],
  EX:  ['Externality / spillover',                    'anti', '#8a3320', 'An issuer’s frequency choice imposes costs on peer firms, on private firms that learn from public-firm data, and on the broader market.'],
  CMP: ['Comparability / granularity',                'anti', '#c97058', 'Loss of intra-period granularity (Q1 vs Q2); reduced ability to detect seasonality; reduced comparability across issuers with different fiscal years.'],
  CC:  ['Contractual constraints',                    'anti', '#663020', 'Debt covenants, lenders, listing standards, and bank regulators force continued quarterly preparation — the cost savings would not fully materialize.'],
  SG:  ['Signaling transparency',                     'anti', '#94483a', 'Continuing quarterly reporters may signal a transparency commitment that investors value — switching loses that signaling benefit.'],
  US:  ['US capital market leadership (commenter)',   'cd',   '#b85542', 'Quarterly reporting underpins global confidence in US markets; loosening it harms US competitiveness. Not engaged as a standalone argument in the SEC release.'],
  RI:  ['Reliance interests (commenter)',             'cd',   '#a8625a', 'Analysts, mutual-fund pricing, ETFs, credit committees, and rating agencies have built workflows around quarterly cadence. The SEC discusses switching costs for issuers but not reliance for investors.'],
  PP:  ['Political pressure / regulatory capture',     'cd',   '#7a1f3d', 'Commenter-distinctive. The letter argues the rule itself is politically motivated or serves the powerful / captured regulators — attribution to political pressure, lobbying, donor influence, partisan/regime alignment, or regulatory capture. Promoted from a §6.6 watch item to a coded rationale on 2026-06-04. Narrow definition: generic concealment-suspicion, ordinary insiders-vs-retail framing, and generic motive-questioning do NOT qualify. Not part of the original 20-code cross-model κ validation.'],
  CB:  ['Compliance burden',                          'pro',  '#3b6d11', 'Quarterly reporting is expensive: SEC estimates ~$198,000/issuer/year savings if a company switches to semiannual.'],
  ST:  ['Short-termism / managerial focus',           'pro',  '#487a1a', 'Quarterly cadence pressures managers toward short-term targets; semiannual frees them to focus on long-term strategy.'],
  OP:  ['Optionality / flexibility',                  'pro',  '#559524', 'Companies should be able to choose the cadence appropriate to their size, industry, and investor base. The proposal is voluntary, not mandatory.'],
  OV:  ['Option value for non-switchers',             'pro',  '#6ba83c', 'Even firms that don’t switch benefit from having the option available — SEC argues the flexibility itself has value.'],
  ICs: ['Intl evidence — supportive',                 'pro',  '#2c5d22', 'UK / Singapore studies find little evidence that changes in reporting frequency materially affect real investment decisions.'],
  AL:  ['Alternative cadence / hybrid',               'cond', '#854f0b', 'Proposes a middle path: 4-month cadence, mandatory monthly revenue, scaled SRC-only relief, or mandatory quarterly earnings releases.'],
  GU:  ['Guidance vs reporting',                      'cond', '#2a7d6f', 'The argument that quarterly earnings GUIDANCE (voluntary EPS forecasts), not quarterly REPORTING itself, drives short-termism — so the SEC should address guidance rather than reporting frequency (Buffett/Dimon, Larry Fink framing). A close cousin of ST. Central to the 2018 RFC (S7-26-18) and shared with that tracker; carried in the 2026 taxonomy for cross-rubric consistency, not yet invoked in the 2026 corpus.'],
  LE:  ['Legal / administrative-law',                 'proc', '#185fa5', 'APA, Loper-Bright (2024) deference framework, major-questions doctrine, §13(a) statutory text, State Farm, D.C. Circuit cost-benefit (Business Roundtable).'],
  NR:  ['No substantive rationale',                   'none', '#888780', 'Letter states a position without engaging any substantive argument — e.g. “This is a bad idea.”, “Keep it quarterly.”'],
};
const RATIONALE_ORDER = ['IP','IA','FR','MF','AU','ICc','EX','CMP','CC','SG','US','RI','PP','CB','ST','OP','OV','ICs','AL','GU','LE','NR'];

const rationaleCounts = {};
RATIONALE_ORDER.forEach(c => rationaleCounts[c] = 0);
RECORDS.forEach(r => (r.rationales || []).forEach(c => {
  if (c in rationaleCounts) rationaleCounts[c]++;
}));

// Drop zero-count codes from the main chart (note rendered separately below).
const ratActive = RATIONALE_ORDER.filter(c => rationaleCounts[c] > 0).sort((a, b) => rationaleCounts[b] - rationaleCounts[a]);
const ratInactive = RATIONALE_ORDER.filter(c => rationaleCounts[c] === 0);

const ratLabels = ratActive.map(c => c + '  ·  ' + RATIONALE_META[c][0]);
const ratData = ratActive.map(c => rationaleCounts[c]);
const ratColors = ratActive.map(c => RATIONALE_META[c][2]);

if (HAS_CHART) new Chart(document.getElementById('rationaleChart'), {
  type: 'bar',
  data: {
    labels: ratLabels,
    datasets: [{
      label: 'Letters citing this rationale',
      data: ratData,
      backgroundColor: ratColors,
      borderWidth: 0,
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
    indexAxis: 'y',
    scales: {
      x: { beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: 'Letters citing this rationale (of ' + RECORDS.length + ')' } },
      y: { ticks: { autoSkip: false, font: { size: 11 } } }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => {
            const pct = Math.round(ctx.parsed.x / RECORDS.length * 100);
            return ctx.parsed.x + ' letters (' + pct + '% of corpus)';
          }
        }
      }
    }
  }
});

// Note about zero-count SEC-anticipated codes
if (ratInactive.length) {
  const noteEl = document.getElementById('rationale-zero-note');
  if (noteEl) {
    noteEl.innerHTML = '<strong>SEC-anticipated rationales with 0 commenter mentions:</strong> ' +
      ratInactive.map(c => '<span class="rat-badge" data-rat-code="'+c+'" style="background:'+RATIONALE_META[c][2]+'; color:#fff;">'+c+'</span> ' + RATIONALE_META[c][0]).join(' &nbsp;·&nbsp; ') +
      '. These arguments appear in the SEC\'s own proposing release but no commenter has invoked them yet.';
  }
}

// Stacked-by-stance chart: which rationales are cited by Oppose vs Conditional vs Support letters
const STANCES_FOR_RAT = ['Oppose','Conditional','Support'];
const STANCE_COLORS_RAT = { 'Oppose':'#993c1d', 'Conditional':'#a8830d', 'Support':'#3b6d11' };
const ratByStance = {};
ratActive.forEach(c => { ratByStance[c] = {Oppose:0, Conditional:0, Support:0}; });
RECORDS.forEach(r => {
  if (!STANCES_FOR_RAT.includes(r.stance)) return;
  (r.rationales || []).forEach(c => {
    if (c in ratByStance) ratByStance[c][r.stance]++;
  });
});

// Shared tooltip helpers — used by chart y-axis pills, table-row badges, and zero-note badges.
function showRationaleTooltip(evt, code) {
  const meta = RATIONALE_META[code];
  if (!meta) return;
  const tip = document.getElementById('rationale-tooltip');
  if (!tip) return;
  tip.innerHTML =
    '<div class="rt-head">' +
      '<span class="rt-code" style="background:' + meta[2] + '; color:#fff;">' + escape(code) + '</span>' +
      '<span class="rt-name">' + escape(meta[0]) + '</span>' +
    '</div>' +
    '<div class="rt-desc">' + escape(meta[3] || '') + '</div>';
  tip.style.display = 'block';
  // Position above the cursor, clamped to viewport
  const x = evt.clientX, y = evt.clientY;
  const rect = tip.getBoundingClientRect();
  let left = x + 12;
  let top = y - rect.height - 14;
  if (left + rect.width > window.innerWidth - 12) left = window.innerWidth - rect.width - 12;
  if (top < 8) top = y + 16;
  tip.style.left = left + 'px';
  tip.style.top = top + 'px';
}
function hideRationaleTooltip() {
  const tip = document.getElementById('rationale-tooltip');
  if (tip) tip.style.display = 'none';
}

// Chart.js plugin that paints colored "pill" backgrounds behind y-axis tick labels
// and registers HTML hover zones over them for the shared rationale tooltip.
const pillLabelsPlugin = {
  id: 'pillLabels',
  afterDraw(chart) {
    if (!chart.options._pillLabels) return;
    const { ctx, scales: { y }, canvas } = chart;
    if (!y) return;
    const labels = chart.data.labels;
    ctx.save();
    ctx.font = '700 11px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.textBaseline = 'middle';
    const pills = [];
    labels.forEach((code, i) => {
      const meta = RATIONALE_META[code];
      if (!meta) return;
      const yPos = y.getPixelForTick(i);
      const textW = ctx.measureText(code).width;
      const padX = 7, pillH = 18;
      const pillW = textW + padX * 2;
      const pillX = y.right - pillW - 4;
      const pillY = yPos - pillH / 2;
      // Pill background
      ctx.fillStyle = meta[2];
      if (ctx.roundRect) {
        ctx.beginPath();
        ctx.roundRect(pillX, pillY, pillW, pillH, 9);
        ctx.fill();
      } else {
        ctx.fillRect(pillX, pillY, pillW, pillH);
      }
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'left';
      ctx.fillText(code, pillX + padX, yPos);
      pills.push({ code, x: pillX, y: pillY, w: pillW, h: pillH });
    });
    ctx.restore();

    // Rebuild HTML hover zones over each canvas pill (one per draw cycle).
    const parent = canvas.parentElement;
    if (!parent) return;
    parent.style.position = parent.style.position || 'relative';
    let overlay = parent.querySelector('.pill-hover-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'pill-hover-overlay';
      overlay.style.cssText = 'position:absolute; top:0; left:0; right:0; bottom:0; pointer-events:none;';
      parent.appendChild(overlay);
    }
    // Canvas may be offset within parent due to padding; align with canvas top-left.
    const canvasOffsetTop = canvas.offsetTop;
    const canvasOffsetLeft = canvas.offsetLeft;
    overlay.innerHTML = pills.map(p =>
      '<div class="pill-hover-zone" data-rat-code="' + p.code + '" style="left:' +
      (p.x + canvasOffsetLeft) + 'px;top:' + (p.y + canvasOffsetTop) + 'px;width:' +
      p.w + 'px;height:' + p.h + 'px;pointer-events:auto;"></div>'
    ).join('');
    // Wire events (delegated on overlay)
    if (!overlay._wired) {
      overlay.addEventListener('mouseover', (e) => {
        const z = e.target.closest('.pill-hover-zone');
        if (z) showRationaleTooltip(e, z.dataset.ratCode);
      });
      overlay.addEventListener('mousemove', (e) => {
        const z = e.target.closest('.pill-hover-zone');
        if (z) showRationaleTooltip(e, z.dataset.ratCode);
      });
      overlay.addEventListener('mouseout', (e) => {
        const z = e.target.closest('.pill-hover-zone');
        if (z) hideRationaleTooltip();
      });
      overlay._wired = true;
    }
  }
};

// Wire the shared tooltip to table-row badges and zero-note badges via event delegation on body.
document.addEventListener('mouseover', (e) => {
  const b = e.target.closest('.rat-badge[data-rat-code]');
  if (b) showRationaleTooltip(e, b.dataset.ratCode);
});
document.addEventListener('mousemove', (e) => {
  const b = e.target.closest('.rat-badge[data-rat-code]');
  if (b) showRationaleTooltip(e, b.dataset.ratCode);
});
document.addEventListener('mouseout', (e) => {
  const b = e.target.closest('.rat-badge[data-rat-code]');
  if (b) hideRationaleTooltip();
});

if (HAS_CHART && document.getElementById('rationaleStanceChart')) new Chart(document.getElementById('rationaleStanceChart'), {
  type: 'bar',
  plugins: [pillLabelsPlugin],
  data: {
    labels: ratActive.map(c => c),
    datasets: STANCES_FOR_RAT.map(s => ({
      label: s,
      data: ratActive.map(c => ratByStance[c][s]),
      backgroundColor: STANCE_COLORS_RAT[s],
    }))
  },
  options: {
    responsive: true, maintainAspectRatio: false, animation: { duration: 200 },
    indexAxis: 'y',
    _pillLabels: true,
    layout: { padding: { left: 12 } },
    scales: {
      x: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: 'Letters citing this rationale, stacked by stance' } },
      y: { stacked: true, ticks: { display: false, autoSkip: false }, afterFit(scale) { scale.width = 60; } }
    },
    plugins: {
      legend: { display: true, position: 'top', labels: { boxWidth: 12, font: { size: 11 } } },
      tooltip: {
        callbacks: {
          afterLabel: ctx => {
            const code = ratActive[ctx.dataIndex];
            return RATIONALE_META[code][0];
          }
        }
      }
    }
  }
});

// Per-letter rationale badge column — small color-coded pills with hover tooltip
function rationaleBadges(r) {
  if (!r.rationales || !r.rationales.length) return '';
  return r.rationales.map(c => {
    const m = RATIONALE_META[c];
    if (!m) return '';
    return '<span class="rat-badge" data-rat-code="'+c+'" style="background:'+m[2]+'; color:#fff;">'+c+'</span>';
  }).join(' ');
}

// Rationale agreement badge — parallel to stance/entity, but rationale is
// multi-label so it has THREE possible states (unanimous / majority / split)
// rather than two. Split gets a muted red to signal "no clear consensus."
function rationaleAgreementBadge(r) {
  if (!r.rationale_agreement) return '';
  const a = r.rationale_agreement;
  let label, badgeBg, badgeColor;
  if (a === 'unanimous')      { label = 'Unanimous'; badgeBg = '#e8eee0'; badgeColor = '#3b6d11'; }
  else if (a === 'majority')  { label = '2 of 3';    badgeBg = '#f4eedb'; badgeColor = '#854f0b'; }
  else                         { label = 'Split';     badgeBg = '#f4dbdb'; badgeColor = '#8b2c2c'; }
  const fmt = arr => (arr && arr.length) ? arr.join(', ') : '—';
  const tooltip = 'Primary: ' + fmt(r.rationales_primary)
    + ' | Literalist: ' + fmt(r.rationales_literalist)
    + ' | Inclusive: ' + fmt(r.rationales_inclusive);
  return '<span class="agreement-badge" title="' + escape(tooltip)
    + '" style="display:inline-block; font-size:10px; padding:1px 6px; margin-left:6px; border-radius:8px; background:'
    + badgeBg + '; color:' + badgeColor + '; vertical-align:middle;">' + label + '</span>';
}

// Rationale cell — pills first, then the agreement badge at the end.
function rationaleCell(r) {
  const pills = rationaleBadges(r);
  const badge = rationaleAgreementBadge(r);
  if (!pills && !badge) return '';
  return pills + badge;
}
/*DEV_ONLY:END*/

// Longest letters by stance — top 5 per stance in collapsible accordions.
// Lives here (after RATIONALE_META and rationaleCell) because the rows render
// rationale pills via rationaleCell, and RATIONALE_META is declared as const
// (TDZ) further up. Running this block before line 1108 throws ReferenceError
// and kills every script that follows.
const LONGEST_STANCES = ['Oppose','Conditional','Support'];
const LONGEST_HEADER_COLOR = { 'Oppose':'#993c1d', 'Conditional':'#a8830d', 'Support':'#3b6d11' };
const longestRow = r => (
  '<div class="longest-row">' +
    '<span class="num">#'+r.n+'</span>' +
    '<span class="date">'+fmtMonthDay(r.date)+'</span>' +
    '<span><span class="name">'+(r.url ? '<a href="'+escape(r.url)+'" target="_blank" rel="noopener">'+escape(r.name)+'</a>' : escape(r.name))+'</span><span class="role">'+escape(r.role||'')+'</span></span>' +
    '<span class="pill '+pillClass(r.stance)+'">'+r.stance+'</span>' +
    '<span class="words">'+(r.words||0).toLocaleString()+'w</span>' +
    '<span class="rat-cell">'+rationaleCell(r)+'</span>' +
  '</div>'
);
document.getElementById('longest').innerHTML = LONGEST_STANCES.map(s => {
  const sub = RECORDS.filter(r => r.stance===s && (r.words||0)>0)
                     .sort((a,b)=>(b.words||0)-(a.words||0))
                     .slice(0,5);
  const bucketCount = RECORDS.filter(r => r.stance===s).length;
  return (
    '<details class="stance-block">' +
      '<summary style="color: '+LONGEST_HEADER_COLOR[s]+';">' +
        s + ' <span class="bucket-meta">(top 5 of ' + bucketCount + ')</span>' +
      '</summary>' +
      '<div class="stance-rows">' +
        sub.map(longestRow).join('') +
      '</div>' +
    '</details>'
  );
}).join('');

// Default: newest letters first, grouped by date. First group open, rest collapsed.
let sortKey = 'date', sortAsc = false;
let expandAll = false;             // user-toggled via "Expand all" button
const collapsedGroups = new Set(); // explicitly-collapsed dates when not in expandAll
const openedGroups = new Set();    // explicitly-opened dates when not in expandAll

function rowHtml(r, groupKey) {
  return (
    '<tr data-group="'+(groupKey||'')+'">' +
      '<td class="num">'+r.n+'</td>' +
      '<td class="num">'+fmtMonthDay(r.date)+'</td>' +
      '<td>'+(r.url ? '<a href="'+escape(r.url)+'" target="_blank" rel="noopener">'+escape(r.name)+'</a>' : escape(r.name))+'</td>' +
      '<td>'+roleCell(r)+'</td>' +
      '<td>'+stanceCell(r)+'</td>' +
      '<td class="num right">'+(r.words||0).toLocaleString()+'</td>' +
      /*DEV_ONLY:BEGIN*/'<td class="rat-cell">'+rationaleCell(r)+'</td>' +/*DEV_ONLY:END*/
      /*VOTING:BEGIN*/'<td>'+voteButton(r)+'</td>' +/*VOTING:END*/
    '</tr>'
  );
}

function fmtFullDate(iso) {
  // 2026-05-15 -> "May 15, 2026"
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso||'');
  if (!m) return iso || '';
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  return months[parseInt(m[2],10)-1] + ' ' + parseInt(m[3],10) + ', ' + m[1];
}

function renderTable() {
  const q = (document.getElementById('q').value||'').toLowerCase().trim();
  const entSel = (document.getElementById('entsel')||{}).value || '';
  const searching = q.length > 0;
  let rows = RECORDS.slice();
  if (entSel) rows = rows.filter(r => (r.entity || '') === entSel);
  if (q) {
    // If the query is exactly a rationale code (e.g. "PP", "MF", "ICc"), match on that code
    // ONLY — exact membership in the letter's rationale set, not a substring of names/roles.
    // Otherwise fall back to a name / role / entity / stance substring search.
    const codeMap = {};
    RECORDS.forEach(r => (r.rationales || []).forEach(c => { codeMap[c.toUpperCase()] = c; }));
    const codeHit = codeMap[q.toUpperCase()];
    rows = rows.filter(r => codeHit
      ? (r.rationales || []).includes(codeHit)
      : (r.name + ' ' + r.role + ' ' + r.entity + ' ' + r.stance).toLowerCase().includes(q));
  }
  rows.sort((a,b)=>{
    const av=a[sortKey], bv=b[sortKey];
    let cmp = 0;
    if (av==null && bv==null) cmp = 0;
    else if (av==null) cmp = 1;
    else if (bv==null) cmp = -1;
    else if (typeof av === 'number' && typeof bv === 'number') cmp = sortAsc ? av-bv : bv-av;
    else cmp = sortAsc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
    if (cmp !== 0) return cmp;
    // Tiebreaker: when sorting by date, fall back to descending letter number
    // so the newest n within each date group sits at the top.
    if (sortKey === 'date') return (b.n||0) - (a.n||0);
    return 0;
  });

  const groupBy = (sortKey === 'date' || sortKey === 'n');
  const colCount = document.querySelectorAll('table.full thead th').length;
  const body = document.getElementById('full-body');

  if (!groupBy) {
    // Flat render for non-date sorts
    body.innerHTML = rows.map(r => rowHtml(r)).join('');
  } else {
    // Group rows by date, preserving sort order within and across groups
    const groups = [];
    const groupIndex = new Map();
    rows.forEach(r => {
      const key = r.date || '(no date)';
      if (!groupIndex.has(key)) { groupIndex.set(key, groups.length); groups.push({ key, rows: [] }); }
      groups[groupIndex.get(key)].rows.push(r);
    });
    let html = '';
    groups.forEach((g, idx) => {
      // Decide open/collapsed for this group
      let isOpen;
      if (searching || expandAll) {
        isOpen = true;
      } else if (openedGroups.has(g.key)) {
        isOpen = true;
      } else if (collapsedGroups.has(g.key)) {
        isOpen = false;
      } else {
        // Default: only the first (top) group is open
        isOpen = (idx === 0);
      }
      const headerClass = 'date-header' + (isOpen ? ' open' : '');
      const rowClass    = isOpen ? '' : ' class="collapsed-row"';
      html += '<tr class="'+headerClass+'" data-group="'+escape(g.key)+'">' +
              '<td colspan="'+colCount+'">' +
                '<span class="chevron">'+(isOpen ? '▾' : '▸')+'</span>' +
                '<span class="group-date">'+escape(fmtFullDate(g.key))+'</span>' +
                '<span class="group-count">'+g.rows.length+' letter'+(g.rows.length===1?'':'s')+'</span>' +
              '</td></tr>';
      html += g.rows.map(r => rowHtml(r, g.key).replace('<tr ', '<tr'+(isOpen?'':' class="collapsed-row"')+' ')).join('');
    });
    body.innerHTML = html;
  }

  // Update sort-arrow display on column headers
  document.querySelectorAll('table.full th').forEach(th => {
    th.classList.remove('sorted','asc');
    if (th.dataset.k === sortKey) { th.classList.add('sorted'); if (sortAsc) th.classList.add('asc'); }
  });

  // Update Expand all / Collapse all button label
  const btn = document.getElementById('expand-toggle');
  if (btn) btn.textContent = expandAll ? 'Collapse all' : 'Expand all';
}

document.querySelectorAll('table.full th').forEach(th => {
  th.addEventListener('click', () => {
    const k = th.dataset.k;
    if (sortKey === k) sortAsc = !sortAsc; else { sortKey = k; sortAsc = (k!=='words' && k!=='n'); }
    renderTable();
  });
});
// Populate the commenter-type (entity) filter dropdown from the data, ordered by count.
(function(){
  const sel = document.getElementById('entsel');
  if (!sel) return;
  const c = {};
  RECORDS.forEach(r => { const e = r.entity || 'Other'; c[e] = (c[e]||0) + 1; });
  const order = Object.keys(c).sort((a,b) => c[b] - c[a]);
  const escAttr = s => String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
  sel.innerHTML = '<option value="">All commenter types (' + RECORDS.length + ')</option>' +
    order.map(e => '<option value="' + escAttr(e) + '">' + escAttr(e) + ' (' + c[e] + ')</option>').join('');
  sel.addEventListener('change', renderTable);
})();
document.getElementById('q').addEventListener('input', renderTable);

// Click a date-header row → toggle that group
document.getElementById('full-body').addEventListener('click', (e) => {
  const header = e.target.closest('tr.date-header');
  if (!header) return;
  const key = header.dataset.group;
  // Determine current state: explicit override > default-by-position
  let currentlyOpen = header.classList.contains('open');
  if (currentlyOpen) {
    collapsedGroups.add(key);
    openedGroups.delete(key);
  } else {
    openedGroups.add(key);
    collapsedGroups.delete(key);
  }
  renderTable();
});

// Expand all / Collapse all toggle
document.getElementById('expand-toggle').addEventListener('click', () => {
  expandAll = !expandAll;
  // Wipe per-group overrides so the toggle is authoritative
  collapsedGroups.clear();
  openedGroups.clear();
  renderTable();
});

renderTable();

/* ======================================================================
 * Feedback modal — site-wide comments box.
 * If Supabase is wired up, posts to the `feedback` table. Otherwise falls
 * back to a mailto: link so visitors can still send something.
 * ====================================================================== */
function openFeedback() {
  // Pre-fill name/email from localStorage if previously entered (shared with vote widget)
  try {
    document.getElementById('fb-name').value  = localStorage.getItem('sec_voter_name')  || '';
    document.getElementById('fb-email').value = localStorage.getItem('sec_voter_email') || '';
  } catch(e) {}
  document.getElementById('fb-message').value = '';
  document.getElementById('fb-err').style.display = 'none';
  document.getElementById('fb-ok').style.display = 'none';
  document.getElementById('fb-submit').disabled = false;
  document.getElementById('fb-submit').textContent = 'Send';
  document.getElementById('feedback-overlay').classList.add('show');
}
function closeFeedback() { document.getElementById('feedback-overlay').classList.remove('show'); }
async function submitFeedback() {
  const name  = (document.getElementById('fb-name').value  || '').trim().slice(0, 120) || null;
  const email = (document.getElementById('fb-email').value || '').trim().slice(0, 200) || null;
  const msg   = (document.getElementById('fb-message').value || '').trim().slice(0, 3000);
  const errEl = document.getElementById('fb-err');
  const okEl  = document.getElementById('fb-ok');
  errEl.style.display = okEl.style.display = 'none';
  if (!msg) {
    errEl.textContent = 'Please type a message.'; errEl.style.display = 'block'; return;
  }
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errEl.textContent = "That email address doesn't look right."; errEl.style.display = 'block'; return;
  }
  try {
    if (name)  localStorage.setItem('sec_voter_name',  name);
    if (email) localStorage.setItem('sec_voter_email', email);
  } catch(e) {}

  const btn = document.getElementById('fb-submit');
  btn.disabled = true; btn.textContent = 'Sending…';

  // Try Supabase first; fall back to opening a mailto: with the message pre-filled.
  const supabaseLive = (typeof SUPABASE_LIVE !== 'undefined') && SUPABASE_LIVE;
  if (supabaseLive) {
    try {
      const res = await fetch(SUPABASE_URL + '/rest/v1/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_KEY,
          'Authorization': 'Bearer ' + SUPABASE_KEY,
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify({
          sender_name: name,
          sender_email: email,
          message: msg,
          user_agent: navigator.userAgent.slice(0, 200),
        })
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      okEl.textContent = 'Thanks — your feedback has been sent.'; okEl.style.display = 'block';
      btn.textContent = 'Sent ✓';
      setTimeout(closeFeedback, 1400);
      return;
    } catch (err) {
      // fall through to mailto
    }
  }
  // Fallback: open default mail client pre-filled
  const subject = encodeURIComponent('S7-2026-15 tracker feedback');
  const bodyLines = [];
  if (name)  bodyLines.push('From: ' + name);
  if (email) bodyLines.push('Email: ' + email);
  if (bodyLines.length) bodyLines.push('');
  bodyLines.push(msg);
  const body = encodeURIComponent(bodyLines.join('\n'));
  window.location.href = 'mailto:zach.7@osu.edu?subject=' + subject + '&body=' + body;
  okEl.textContent = 'Opening your mail client…'; okEl.style.display = 'block';
  btn.textContent = 'Sent ✓';
  setTimeout(closeFeedback, 1400);
}
document.getElementById('feedback-open').addEventListener('click', (e) => { e.preventDefault(); openFeedback(); });
document.getElementById('fb-cancel').addEventListener('click', closeFeedback);
document.getElementById('fb-submit').addEventListener('click', submitFeedback);
document.getElementById('feedback-overlay').addEventListener('click', (e) => {
  if (e.target.id === 'feedback-overlay') closeFeedback();
});

/*VOTING:BEGIN*/
/* ======================================================================
 * VOTE WIDGET — blind judgment with reveal
 * (SUPABASE_URL, SUPABASE_KEY, BODIES_INLINE, BODIES_URL, SUPABASE_LIVE, VOTE_ENABLED
 *  are declared near the top of the script, before renderTable runs.)
 * ====================================================================== */

// Per-issue questions visitors answer about each letter
const ISSUES = [
  { id: 'q_cadence_ok',   label: 'Does the writer find 6-month cadence acceptable?' },
  { id: 'q_assurance',    label: 'Does the writer ask for enhanced auditor review / assurance?' },
  { id: 'q_retail_focus', label: 'Is retail-investor protection a central argument?' },
  { id: 'q_alt_cadence',  label: 'Does the writer propose an alternative cadence (4-month, monthly, scaled, etc.)?' },
  { id: 'q_cost_burden',  label: 'Does the writer engage with the cost-burden / small-issuer argument?' },
  { id: 'q_sec_mandate',  label: 'Does the writer invoke the SEC’s investor-protection mandate?' },
];

// Persistent voter UUID (anonymous, browser-scoped)
function voterUuid() {
  let id = null;
  try {
    id = localStorage.getItem('sec_voter_uuid');
    if (!id) {
      id = (crypto.randomUUID ? crypto.randomUUID() : ('xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random()*16|0; const v = c === 'x' ? r : (r&0x3|0x8); return v.toString(16);
      })));
      localStorage.setItem('sec_voter_uuid', id);
    }
  } catch(e) {}
  return id;
}
// (getVotedSet / markVoted are defined earlier so stanceCell can use them.)

function voteButton(r) {
  const voted = getVotedSet().has(r.n);
  if (voted) return '<span class="vote-btn voted" title="You already voted">Voted ✓</span>';
  const label = SUPABASE_LIVE ? 'Vote' : 'Vote (preview)';
  const title = SUPABASE_LIVE ? '' : ' title="Preview only — Supabase not configured yet, votes won&#39;t persist"';
  return '<button class="vote-btn" data-vote-n="'+r.n+'"'+title+'>'+label+'</button>';
}

// Lazy-load letter bodies once. Prefer inlined bodies (avoids file:// fetch errors);
// fall back to fetch(BODIES_URL) if bodies weren't inlined.
let _bodiesPromise = null;
function loadBodies() {
  if (_bodiesPromise) return _bodiesPromise;
  if (BODIES_INLINE && Object.keys(BODIES_INLINE).length) {
    _bodiesPromise = Promise.resolve(BODIES_INLINE);
  } else {
    _bodiesPromise = fetch(BODIES_URL).then(r => r.json()).catch(()=> ({}));
  }
  return _bodiesPromise;
}

// Modal state
let currentVoteRecord = null;
let voteStartTime = 0;

function openVoteModal(record) {
  currentVoteRecord = record;
  voteStartTime = Date.now();

  document.getElementById('vm-title').textContent = record.name + ' — letter #' + record.n;
  document.getElementById('vm-meta').textContent = (record.date || '') + ' · ' + (record.role || '') + ' · ' + (record.words || 0).toLocaleString() + ' words';

  // Body
  document.getElementById('vm-body').textContent = 'Loading letter body…';
  loadBodies().then(bodies => {
    const body = (bodies && bodies[record.n]) || ('(Body not available locally. Read on SEC.gov: ' + record.url + ')');
    document.getElementById('vm-body').textContent = body;
  });

  // Reset form
  document.querySelectorAll('#vm-likert label').forEach(l => l.classList.remove('sel'));
  document.querySelectorAll('#vm-likert input').forEach(i => i.checked = false);
  document.getElementById('vm-clear').checked = true;
  document.getElementById('vm-comment').value = '';
  // Pre-fill name + email from localStorage (set on first vote so returning voters don't retype)
  try {
    document.getElementById('vm-name').value = localStorage.getItem('sec_voter_name') || '';
    document.getElementById('vm-email').value = localStorage.getItem('sec_voter_email') || '';
  } catch(e) {}
  document.getElementById('vm-name').classList.remove('invalid');
  document.getElementById('vm-email').classList.remove('invalid');
  document.getElementById('vm-err').style.display = 'none';
  document.getElementById('vm-reveal').style.display = 'none';
  document.getElementById('vm-submit').disabled = true;
  document.getElementById('vm-submit').textContent = 'Submit & reveal';

  // Build per-issue questions
  const qs = document.getElementById('vm-qs');
  qs.innerHTML = ISSUES.map(iss => (
    '<div class="q"><div>'+escape(iss.label)+'</div>' +
      '<div class="triple" data-issue="'+iss.id+'">' +
        '<label data-v="yes"><input type="radio" name="'+iss.id+'" value="yes">Yes</label>' +
        '<label data-v="no"><input type="radio" name="'+iss.id+'" value="no">No</label>' +
        '<label data-v="na"><input type="radio" name="'+iss.id+'" value="na">Not mentioned</label>' +
      '</div>' +
    '</div>'
  )).join('');

  // Click handlers for selection styling
  document.querySelectorAll('#vm-likert label').forEach(l => {
    l.onclick = () => {
      document.querySelectorAll('#vm-likert label').forEach(x => x.classList.remove('sel'));
      l.classList.add('sel');
      l.querySelector('input').checked = true;
      document.getElementById('vm-submit').disabled = false;
    };
  });
  document.querySelectorAll('#vm-qs .triple label').forEach(l => {
    l.onclick = () => {
      l.parentElement.querySelectorAll('label').forEach(x => x.classList.remove('sel'));
      l.classList.add('sel');
      l.querySelector('input').checked = true;
    };
  });

  document.getElementById('vote-overlay').classList.add('show');
}

function closeVoteModal() {
  document.getElementById('vote-overlay').classList.remove('show');
  currentVoteRecord = null;
}

async function submitVote() {
  if (!currentVoteRecord) return;
  const r = currentVoteRecord;
  const sel = document.querySelector('#vm-likert input:checked');
  if (!sel) {
    document.getElementById('vm-err').textContent = 'Please pick an overall stance.';
    document.getElementById('vm-err').style.display = 'block';
    return;
  }
  const likert = parseInt(sel.value, 10);
  const positionClear = document.getElementById('vm-clear').checked;
  const comment = document.getElementById('vm-comment').value.trim().slice(0, 500) || null;
  const readMs = Date.now() - voteStartTime;

  // Optional voter identity. Validate email format if provided.
  const nameEl = document.getElementById('vm-name');
  const emailEl = document.getElementById('vm-email');
  const voterName = (nameEl.value || '').trim().slice(0, 120) || null;
  const voterEmail = (emailEl.value || '').trim().slice(0, 200) || null;
  nameEl.classList.remove('invalid');
  emailEl.classList.remove('invalid');
  if (voterEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(voterEmail)) {
    emailEl.classList.add('invalid');
    document.getElementById('vm-err').textContent = 'That email address doesn\'t look right. Fix it or clear the field to stay anonymous.';
    document.getElementById('vm-err').style.display = 'block';
    return;
  }
  // Persist for next time
  try {
    if (voterName)  localStorage.setItem('sec_voter_name', voterName);  else localStorage.removeItem('sec_voter_name');
    if (voterEmail) localStorage.setItem('sec_voter_email', voterEmail); else localStorage.removeItem('sec_voter_email');
  } catch(e) {}

  const payload = {
    letter_id: r.n,
    voter_uuid: voterUuid(),
    stance_likert: likert,
    position_clear: positionClear,
    comment_text: comment,
    voter_name: voterName,
    voter_email: voterEmail,
    read_time_ms: readMs,
    user_agent: navigator.userAgent.slice(0, 200),
  };
  ISSUES.forEach(iss => {
    const v = document.querySelector('#vm-qs input[name="'+iss.id+'"]:checked');
    payload[iss.id] = v ? v.value : 'na';
  });

  const btn = document.getElementById('vm-submit');
  btn.disabled = true; btn.textContent = 'Submitting…';
  document.getElementById('vm-err').style.display = 'none';

  // Preview mode: Supabase not configured. Reveal anyway so the user can see the UX.
  if (!SUPABASE_LIVE) {
    markVoted(r.n);
    revealAfterVote(r, likert, { preview: true });
    btn.textContent = 'Preview only';
    renderTable();
    return;
  }

  try {
    const res = await fetch(SUPABASE_URL + '/rest/v1/votes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const txt = await res.text();
      // Duplicate vote handling
      if (res.status === 409 || /duplicate|unique/i.test(txt)) {
        document.getElementById('vm-err').textContent = 'Looks like you already voted on this letter from this browser.';
      } else {
        document.getElementById('vm-err').textContent = 'Could not save vote (HTTP ' + res.status + '). You can try again.';
      }
      document.getElementById('vm-err').style.display = 'block';
      btn.disabled = false; btn.textContent = 'Submit & reveal';
      return;
    }
    markVoted(r.n);
    revealAfterVote(r, likert);
    btn.textContent = 'Done — thanks!';
    renderTable();
  } catch (err) {
    document.getElementById('vm-err').textContent = 'Network error: ' + (err.message || err);
    document.getElementById('vm-err').style.display = 'block';
    btn.disabled = false; btn.textContent = 'Submit & reveal';
  }
}

async function revealAfterVote(r, yourLikert, opts) {
  opts = opts || {};
  const div = document.getElementById('vm-reveal');
  const yourLabel = ['Strongly oppose','Lean oppose','Conditional','Lean support','Strongly support'][yourLikert + 2];
  let html = '<strong>Reveal</strong>';
  if (opts.preview) {
    html += '<div class="vm-banner" style="margin:8px 0; display:block;">Preview mode — your vote was not saved. Configure Supabase (see <code>_meta/SUPABASE_SETUP.md</code>) to persist votes and aggregate crowd data.</div>';
  }
  html +=
    '<div class="row"><span class="lbl">Your vote</span><span class="val">'+escape(yourLabel)+'</span></div>' +
    '<div class="row"><span class="lbl">Rater 1 (Primary)</span><span class="val">'+escape(r.primary||'—')+'</span></div>' +
    '<div class="row"><span class="lbl">Rater 2 (Literalist)</span><span class="val">'+escape(r.literalist||'—')+'</span></div>' +
    '<div class="row"><span class="lbl">Rater 3 (Skeptic)</span><span class="val">'+escape(r.skeptic||'—')+'</span></div>' +
    '<div class="row"><span class="lbl">Majority of three</span><span class="val">'+escape(r.stance||'—')+'</span></div>';
  if (SUPABASE_LIVE) {
    try {
      const agg = await fetch(SUPABASE_URL + '/rest/v1/vote_aggregates?letter_id=eq.' + r.n, {
        headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY }
      }).then(r=>r.json());
      if (Array.isArray(agg) && agg.length) {
        const a = agg[0];
        const dist = 'Oppose ' + a.n_oppose + ' · Conditional ' + a.n_conditional + ' · Support ' + a.n_support;
        html += '<div class="row"><span class="lbl">Crowd (n=' + a.n_votes + ')</span><span class="val">' + escape(dist) + ' · mean Likert ' + (a.mean_likert==null?'—':a.mean_likert) + '</span></div>';
      }
    } catch(e) {}
  }
  div.innerHTML = html;
  div.style.display = 'block';
}

// Wire up modal events
document.getElementById('vote-overlay').addEventListener('click', (e) => {
  if (e.target.id === 'vote-overlay') closeVoteModal();
});
document.getElementById('vm-cancel').addEventListener('click', closeVoteModal);
document.getElementById('vm-submit').addEventListener('click', submitVote);

// Delegate Vote button clicks
document.getElementById('full-body').addEventListener('click', (e) => {
  const btn = e.target.closest('[data-vote-n]');
  if (!btn) return;
  const n = parseInt(btn.dataset.voteN, 10);
  const rec = RECORDS.find(r => r.n === n);
  if (rec) openVoteModal(rec);
});

if (!SUPABASE_LIVE) {
  const cta = document.getElementById('vote-cta');
  if (cta) {
    const banner = document.createElement('div');
    banner.style.cssText = 'background:#fff7ec; color:#8a4f0a; padding:8px 12px; border-radius:6px; font-size:12px; margin-top:10px;';
    banner.innerHTML = 'Preview mode — Supabase not configured. Click Vote (preview) on any letter to see the modal; submissions will not be saved. To go live, follow <code>_meta/SUPABASE_SETUP.md</code>.';
    cta.appendChild(banner);
  }
}

// Blind-mode toggle
function updateBlindToggleLabel() {
  const el = document.getElementById('blind-toggle');
  if (!el) return;
  el.textContent = BLIND_MODE
    ? 'Show all classifications (turn off blind mode)'
    : 'Hide our classifications (blind mode on)';
}
updateBlindToggleLabel();
document.getElementById('blind-toggle').addEventListener('click', () => {
  BLIND_MODE = !BLIND_MODE;
  try { localStorage.setItem('sec_blind_mode', BLIND_MODE ? '1' : '0'); } catch(e) {}
  updateBlindToggleLabel();
  renderTable();
});
/*VOTING:END*/
</script>
__GOATCOUNTER__
</body>
</html>
"""

# ---- Build step ------------------------------------------------------------

def build_snapshot(records):
    """Compress to just what the dashboard needs.

    Headline stance is majority-of-3 if present. Two sentinels are filtered out:
      - "Unclassified" — letters the daily GitHub Actions fetch picked up but Claude
        has not yet classified. They stay in renumbered_records.json (for the Cowork
        session to pick up) but stay invisible on the public site until classified.
      - "Off-topic" — letters filed under the S7-2026-15 docket by submission error
        but addressing a different rulemaking entirely. Kept in renumbered_records.json
        so the daily fetch does not re-pull them, but excluded from the site, the
        rater statistics, and the regression.
    """
    out = []
    skipped_unclassified = 0
    skipped_offtopic = 0
    skipped_noposition = 0
    for r in records:
        headline = r.get("majority_stance") or r.get("stance", "")
        if headline == "Unclassified":
            skipped_unclassified += 1
            continue
        if headline == "Off-topic":
            skipped_offtopic += 1
            continue
        if headline == "No position":
            # On-topic but states no Support/Oppose/Conditional position on reporting
            # frequency (research / procedural / endorse-by-reference). Kept in
            # renumbered_records.json but excluded from the public split, rater stats,
            # and regression — same treatment as Off-topic. (Category added 2026-05-21,
            # carried over from the 2018 S7-26-18 mirror methodology.)
            skipped_noposition += 1
            continue
        if headline == "Duplicate":
            # Verbatim re-submission of another commenter's own letter (the SEC docket
            # sometimes lists both a base and a "_0" variant of the same upload). Kept
            # in renumbered_records.json so the fetch does not re-pull it, but excluded
            # from the public split, rater stats, and regression so a single commenter
            # is not double-counted. (Category added 2026-05-31.)
            skipped_noposition += 1
            continue
        out.append({
            "n": r["n"],
            "page": r.get("page", 0),
            "date": r.get("date", ""),
            "name": r.get("name", ""),
            "role": (r.get("role", "") or "")[:120],
            "entity": r.get("entity", ""),
            "entity_agreement": r.get("entity_agreement", ""),
            "entity_primary": r.get("entity_primary", ""),
            "entity_selfdescribed": r.get("entity_selfdescribed", ""),
            "entity_letterhead": r.get("entity_letterhead", ""),
            "stance": headline,
            "primary": r.get("primary_stance", r.get("stance", "")),
            "literalist": r.get("literalist_stance", ""),
            "skeptic": r.get("skeptic_stance", ""),
            "agreement": r.get("agreement", ""),
            "url": r.get("url", ""),
            "words": r.get("words", 0),
            "rationales": r.get("rationales", []),
            "rationale_agreement": r.get("rationale_agreement", ""),
            "rationales_primary": r.get("rationales_primary", []),
            "rationales_literalist": r.get("rationales_literalist", []),
            "rationales_inclusive": r.get("rationales_inclusive", []),
        })
    if skipped_unclassified:
        print(f"[build] {skipped_unclassified} unclassified letter(s) held out of the public snapshot.")
    if skipped_offtopic:
        print(f"[build] {skipped_offtopic} off-topic letter(s) held out of the public snapshot.")
    if skipped_noposition:
        print(f"[build] {skipped_noposition} no-position letter(s) held out of the public snapshot.")
    return out


def count_unclassified(records):
    return sum(1 for r in records if (r.get("majority_stance") or r.get("stance", "")) == "Unclassified")


def compute_method_stats(records):
    """Compute 3-rater agreement statistics for the methodology panel."""
    from collections import Counter
    # Only letters that have valid stance values across all three raters — exclude PDF placeholders.
    VALID = {"Support", "Oppose", "Conditional"}
    have_three = [r for r in records
                  if r.get("primary_stance") in VALID
                  and r.get("literalist_stance") in VALID
                  and r.get("skeptic_stance") in VALID]
    if not have_three:
        return None
    n = len(have_three)
    unanimous = 0
    majority = 0
    for r in have_three:
        votes = {r.get("primary_stance"), r.get("literalist_stance"), r.get("skeptic_stance")}
        if len(votes) == 1:
            unanimous += 1
        else:
            majority += 1

    def kappa(key_a, key_b):
        labels = ["Support", "Oppose", "Conditional"]
        a = [r.get(key_a) for r in have_three]
        b = [r.get(key_b) for r in have_three]
        po = sum(1 for x, y in zip(a, b) if x == y) / n
        ca, cb = Counter(a), Counter(b)
        pe = sum((ca.get(l, 0) / n) * (cb.get(l, 0) / n) for l in labels)
        return 1.0 if pe == 1 else (po - pe) / (1 - pe)

    def fleiss(records_):
        labels = ["Support", "Oppose", "Conditional"]
        rows = []
        for r in records_:
            row = [0, 0, 0]
            for v in (r.get("primary_stance"), r.get("literalist_stance"), r.get("skeptic_stance")):
                if v in labels:
                    row[labels.index(v)] += 1
            rows.append(row)
        n_items = len(rows)
        n_raters = sum(rows[0])
        p_j = [sum(row[j] for row in rows) / (n_items * n_raters) for j in range(len(labels))]
        P_i = [(sum(c * c for c in row) - n_raters) / (n_raters * (n_raters - 1)) for row in rows]
        P_bar = sum(P_i) / n_items
        P_e = sum(p * p for p in p_j)
        return 1.0 if P_e == 1 else (P_bar - P_e) / (1 - P_e)

    out = {
        "n": n,
        "unanimous_n": unanimous,
        "unanimous_pct": f"{100 * unanimous / n:.1f}",
        "majority_n": majority,
        "majority_pct": f"{100 * majority / n:.1f}",
        "fleiss_k": f"{fleiss(have_three):.3f}",
        "k_pl": f"{kappa('primary_stance', 'literalist_stance'):.2f}",
        "k_ps": f"{kappa('primary_stance', 'skeptic_stance'):.2f}",
        "k_ls": f"{kappa('literalist_stance', 'skeptic_stance'):.2f}",
    }

    # --- Entity and rationale agreement, computed live over the in-corpus letters ---
    # (Previously hardcoded at N=287; now tracks the corpus like the stance block above.)
    HELD_SENTINELS = {"Duplicate", "Off-topic", "No position", "Unclassified"}

    def held(r):
        return (r.get("majority_stance") or r.get("stance", "")) in HELD_SENTINELS

    # Canonicalize a few shorthand entity-label spellings to their full bucket name so
    # punctuation variants do not register as rater disagreement or split the distribution.
    ENTITY_CANON = {
        "Industry practitioner-technologist": "Industry practitioner / technologist",
        "Issuer-current": "Issuer / Corporate — current",
        "Issuer-former": "Issuer / Corporate — former",
    }
    def ecanon(x):
        return ENTITY_CANON.get(x, x)

    # ----- Entity (commenter) agreement -----
    ent = [r for r in records if not held(r)
           and r.get("entity_primary") and r.get("entity_selfdescribed") and r.get("entity_letterhead")]
    if ent:
        en = len(ent)
        e_uni = e_maj = 0
        for r in ent:
            vs = {ecanon(r["entity_primary"]), ecanon(r["entity_selfdescribed"]), ecanon(r["entity_letterhead"])}
            if len(vs) == 1:
                e_uni += 1
            elif len(vs) == 2:
                e_maj += 1
        elabels = sorted({ecanon(r[k]) for r in ent
                          for k in ("entity_primary", "entity_selfdescribed", "entity_letterhead")})

        def efleiss():
            rows = []
            for r in ent:
                row = [0] * len(elabels)
                for v in (r["entity_primary"], r["entity_selfdescribed"], r["entity_letterhead"]):
                    row[elabels.index(ecanon(v))] += 1
                rows.append(row)
            ni, nr = len(rows), 3
            pj = [sum(row[j] for row in rows) / (ni * nr) for j in range(len(elabels))]
            Pi = [(sum(c * c for c in row) - nr) / (nr * (nr - 1)) for row in rows]
            Pbar = sum(Pi) / ni
            Pe = sum(p * p for p in pj)
            return 1.0 if Pe == 1 else (Pbar - Pe) / (1 - Pe)

        ESHORT = {"Industry practitioner / technologist": "Industry practitioner",
                  "Issuer / Corporate — current": "Issuer-current",
                  "Issuer / Corporate — former": "Issuer-former"}
        edist = Counter(ecanon(r["entity"]) for r in ent)
        out.update({
            "ent_n": en,
            "ent_unanimous_n": e_uni,
            "ent_unanimous_pct": f"{100 * e_uni / en:.1f}",
            "ent_majority_n": e_maj,
            "ent_majority_pct": f"{100 * e_maj / en:.1f}",
            "ent_fleiss_k": f"{efleiss():.3f}",
            "ent_dist": " / ".join(f"{ESHORT.get(k, k)} {v}" for k, v in edist.most_common()),
        })

    # ----- Rationale agreement (multi-label) -----
    RAT = ("rationales_primary", "rationales_literalist", "rationales_inclusive")
    rat = [r for r in records if not held(r) and all(isinstance(r.get(k), list) for k in RAT)]
    if rat:
        rn = len(rat)
        r_uni = r_maj = r_split = 0
        for r in rat:
            sets = {frozenset(r["rationales_primary"]), frozenset(r["rationales_literalist"]),
                    frozenset(r["rationales_inclusive"])}
            if len(sets) == 1:
                r_uni += 1
            elif len(sets) == 2:
                r_maj += 1
            else:
                r_split += 1
        codes = sorted({c for r in rat for k in RAT for c in r[k]})

        def kbin(a, b):
            m = len(a)
            po = sum(1 for x, y in zip(a, b) if x == y) / m
            p1a, p1b = sum(a) / m, sum(b) / m
            pe = p1a * p1b + (1 - p1a) * (1 - p1b)
            return 1.0 if pe == 1 else (po - pe) / (1 - pe)

        percode = {}
        for c in codes:
            pres = {k: [1 if c in r[k] else 0 for r in rat] for k in RAT}
            ks = [kbin(pres[RAT[0]], pres[RAT[1]]), kbin(pres[RAT[0]], pres[RAT[2]]), kbin(pres[RAT[1]], pres[RAT[2]])]
            percode[c] = sum(ks) / 3
        ordered = sorted(percode, key=lambda c: -percode[c])
        inv = Counter()
        for r in rat:
            for c in set(r.get("rationales") or []):
                inv[c] += 1
        CODE_NAMES = {"OV": "option value", "SG": "signaling", "RI": "reliance interests",
                      "CMP": "comparability", "CC": "contractual constraints", "ICs": "intl evidence — supportive",
                      "CB": "compliance burden", "US": "US market leadership", "PP": "political pressure"}
        # Illustrate "reliability scales with frequency" using the rarest codes (lowest invocation
        # count), not the lowest κ — some low-κ codes (e.g. RI) are not rare.
        rarest = sorted(codes, key=lambda c: (inv.get(c, 0), c))[:3]
        note = "; ".join(
            f"{c} ({CODE_NAMES.get(c, c)}) on {inv.get(c, 0)} letter{'s' if inv.get(c, 0) != 1 else ''} (κ {percode[c]:.2f})"
            for c in rarest)
        out.update({
            "rat_n": rn,
            "rat_unanimous_n": r_uni,
            "rat_unanimous_pct": f"{100 * r_uni / rn:.1f}",
            "rat_majority_n": r_maj,
            "rat_majority_pct": f"{100 * r_maj / rn:.1f}",
            "rat_split_n": r_split,
            "rat_split_pct": f"{100 * r_split / rn:.1f}",
            "rat_mean_k": f"{sum(percode.values()) / len(percode):.3f}",
            "rat_percode": " · ".join(f"{c}&nbsp;{percode[c]:.2f}" for c in ordered),
            "rat_freqnote": f"Low-frequency codes have volatile κ (swinging to either extreme on a handful of calls): {note}. κ stabilizes as code frequency rises.",
        })

    return out


REG_JSON_PATH = META_DIR / "regression_compare.json"

# Travel notice banner. Set SHOW_TRAVEL_NOTICE = True to render it on the
# PRODUCTION site as well as the dev mirror. Set it back to False (or remove
# the block) when the trip is over — 2026-05-22 to 2026-05-31; off June 1.
SHOW_TRAVEL_NOTICE = False
TRAVEL_NOTICE_HTML = """<div style="background:#fff7e0; border-left: 4px solid #d4a017; border-radius: 6px; padding: 14px 18px; margin: 16px 0 24px; font-size: 14px; line-height: 1.55; color: #3a3a3a;">
  <strong>📅 Site on pause: classification resumes June 1, 2026.</strong>
  <p style="margin: 8px 0 0;">I am traveling from <strong>May 22</strong> to <strong>May 31, 2026</strong>. New letters keep arriving in the docket, but they will not appear on the site until I return and classify them. The current letter count and stance distribution reflect everything I had processed before I left.</p>
</div>"""


def load_regression_compare():
    """Load regression_compare.json. Returns None if missing — caller falls back to a placeholder."""
    if not REG_JSON_PATH.exists():
        return None
    try:
        return json.loads(REG_JSON_PATH.read_text())
    except Exception:
        return None


def _fmt_cell(coef, se, p, separated, dash=False, label=""):
    """Render one (coef, SE, p) cell as stacked HTML lines."""
    if dash:
        return f'<td class="cell dash">{label or "—"}</td>'
    if separated:
        return '<td class="cell sep">separated</td>'
    # significance star
    star = ""
    if p < 0.01: star = '<span class="reg-star">***</span>'
    elif p < 0.05: star = '<span class="reg-star">**</span>'
    elif p < 0.10: star = '<span class="reg-star">*</span>'
    sig_cls = " sig" if p < 0.10 else ""
    sign = "+" if coef >= 0 else "−"
    abs_coef = abs(coef)
    # use 3 decimals for LPM (small magnitudes), 2 decimals otherwise — caller controls via formatting
    return (
        f'<td class="cell{sig_cls}">'
        f'<div class="coef">{sign}{abs_coef:.2f} {star}</div>'
        f'<div class="se">({se:.2f})</div>'
        f'<div class="pv">p = {p:.3f}</div>'
        f'</td>'
    )


def _fmt_cell_lpm(coef, se, p, separated):
    """LPM coefficients are small probabilities; show 3 decimals."""
    if separated:
        return '<td class="cell sep">separated</td>'
    star = ""
    if p < 0.01: star = '<span class="reg-star">***</span>'
    elif p < 0.05: star = '<span class="reg-star">**</span>'
    elif p < 0.10: star = '<span class="reg-star">*</span>'
    sig_cls = " sig" if p < 0.10 else ""
    sign = "+" if coef >= 0 else "−"
    return (
        f'<td class="cell{sig_cls}">'
        f'<div class="coef">{sign}{abs(coef):.3f} {star}</div>'
        f'<div class="se">({se:.3f})</div>'
        f'<div class="pv">p = {p:.3f}</div>'
        f'</td>'
    )


def build_regression_panel(reg):
    """Render the three-spec regression panel HTML from regression_compare.json."""
    if reg is None:
        return (
            '<div class="regression-panel"><p class="reg-footer">'
            'Regression results not available — run <code>python3 _scripts/run_regression_compare.py</code> '
            'to regenerate <code>_meta/regression_compare.json</code>.'
            '</p></div>'
        )
    var_order = reg["var_order"]
    labels = reg["labels"]
    logit = reg["logit"]; lpm = reg["lpm"]; ordinal = reg["ordinal"]

    # Build rows
    rows = []
    for var in var_order:
        label = labels.get(var, var)
        # Logit cell
        if var == "const":
            d = logit["by_var"].get(var)
            logit_cell = _fmt_cell(d["coef"], d["se"], d["p"], d["separated"]) if d else '<td class="cell dash">—</td>'
        else:
            d = logit["by_var"].get(var)
            logit_cell = _fmt_cell(d["coef"], d["se"], d["p"], d["separated"]) if d else '<td class="cell dash">—</td>'

        # Ordinal cell — no constant in ordinal model
        if var == "const":
            ord_cell = '<td class="cell dash">— (cutpoints below)</td>'
        else:
            d = ordinal["by_var"].get(var)
            ord_cell = _fmt_cell(d["coef"], d["se"], d["p"], d["separated"]) if d else '<td class="cell dash">—</td>'

        # LPM cell
        d = lpm["by_var"].get(var)
        lpm_cell = _fmt_cell_lpm(d["coef"], d["se"], d["p"], d["separated"]) if d else '<td class="cell dash">—</td>'

        rows.append(f'<tr><td class="var">{label}</td>{logit_cell}{ord_cell}{lpm_cell}</tr>')

    # Cutpoint line for ordinal
    cuts = ordinal.get("cutpoints", [])
    cutline = ""
    if len(cuts) == 2:
        cutline = (
            f'<p class="reg-footer" style="margin-top: 4px;">'
            f'<strong>Ordinal cutpoints (logit scale).</strong> '
            f'Oppose | Conditional = {cuts[0]:.2f}, '
            f'Conditional | Support = {cuts[1]:.2f}. '
            f'A letter\'s latent stance crosses these thresholds to land in each observed category.'
            f'</p>'
        )

    po = reg["po_lr_test"]
    po_verdict = "reject proportional-odds" if po["p"] < 0.05 else "do not reject proportional-odds"

    fit_logit = f'McFadden R² = {logit["mcfadden"]:.3f}'
    fit_lpm = f'R² = {lpm["r2"]:.3f} (adj. {lpm["adj_r2"]:.3f})'
    fit_ord = f'McFadden R² = {ordinal["mcfadden"]:.3f}'

    html = f'''<div class="regression-panel">
  <table class="reg-table">
    <thead>
      <tr>
        <th style="width: 32%;">Variable</th>
        <th class="spec" style="width: 22%;">Logit<br><span style="font-weight:400;font-size:11px;color:#777;">Support vs Oppose</span></th>
        <th class="spec" style="width: 23%;">Ordinal logit<br><span style="font-weight:400;font-size:11px;color:#777;">Oppose &lt; Cond. &lt; Support</span></th>
        <th class="spec" style="width: 23%;">LPM (OLS)<br><span style="font-weight:400;font-size:11px;color:#777;">Support vs Oppose, HC1</span></th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
    <tfoot>
      <tr class="fitline">
        <td>N</td>
        <td class="cell">{logit["n"]}</td>
        <td class="cell">{ordinal["n"]}</td>
        <td class="cell">{lpm["n"]}</td>
      </tr>
      <tr>
        <td>Fit</td>
        <td class="cell">{fit_logit}</td>
        <td class="cell">{fit_ord}</td>
        <td class="cell">{fit_lpm}</td>
      </tr>
      <tr>
        <td>Log-likelihood</td>
        <td class="cell">{logit["ll"]:.2f}</td>
        <td class="cell">{ordinal["ll"]:.2f}</td>
        <td class="cell">(OLS)</td>
      </tr>
    </tfoot>
  </table>

  <p class="reg-footer"><strong>Reading the table.</strong> Each cell stacks coefficient, SE in parentheses, p-value in italics. Significance markers: <span class="reg-star">*</span> p&lt;0.10, <span class="reg-star">**</span> p&lt;0.05, <span class="reg-star">***</span> p&lt;0.01. Positive coefficients push letters up the stance ladder (toward Support). Reference category for entity is Individual.</p>
  {cutline}
  <p class="reg-footer" style="margin-top: 4px;"><strong>Separation.</strong> "Separated" buckets carry no within-bucket variation in the outcome (no Support letters in the binary specs; all letters in a single ordinal class in the ordinal spec). Treat as "perfectly Oppose" rather than as an estimated effect.</p>

  <details class="lr-test">
    <summary>Proportional-odds assumption (LR test of ordinal vs. multinomial logit)</summary>
    <div class="lr-body">
      Compared the ordinal logit (restricted, single slope vector across both cuts) against an unrestricted multinomial logit on the same predictors. LR = 2 × ({po["multinomial_ll"]:.2f} − {po["ordinal_ll"]:.2f}) = {po["lr"]:.2f}, df = {po["df"]}, p = {po["p"]:.3f}. {po_verdict.capitalize()}. Caveat: low power — only {ordinal["n_support"]} Support letters in the sample.
    </div>
  </details>

  <p class="reg-footer" style="margin-top: 12px;">Last run: {reg["as_of"]} on n = {reg["n_records"]} letters.</p>
</div>'''
    return html


def _strip_voting_blocks(html):
    """Remove all content between VOTING:BEGIN and VOTING:END markers (HTML and JS variants).

    Note: DEV_ONLY markers used to be stripped here too, but everything formerly under that
    marker (the rationale panels, taxonomy badges, tooltips) has been promoted to production.
    The DEV_ONLY markers now stay as annotation comments but are not stripped."""
    html = re.sub(r'<!--VOTING:BEGIN-->.*?<!--VOTING:END-->', '', html, flags=re.DOTALL)
    html = re.sub(r'/\*VOTING:BEGIN\*/.*?/\*VOTING:END\*/', '', html, flags=re.DOTALL)
    return html


def build_form_letter_panel(fl, corpus_counts=None):
    """Render the SEC aggregate form-letter tally as a static panel.

    Reported SIDE BY SIDE with the per-letter corpus, never summed into the headline:
    the submitter counts are anonymous aggregates that may overlap with named letters.
    The panel does show a clearly-labeled hypothetical combined line (docketed + form
    letters) at Tzachi's request, computed dynamically from `corpus_counts` so it stays
    correct as the corpus grows. Returns "" when there is no form-letter data.

    corpus_counts: optional dict {"total": int, "Oppose": int, "Conditional": int,
    "Support": int} for the in-corpus snapshot. When absent, the combined line is omitted.
    """
    import html as _html
    if not fl or not fl.get("types"):
        return ""
    total = fl.get("total_submitters", sum(t.get("submitter_count", 0) for t in fl["types"]))
    n_types = fl.get("n_types", len(fl["types"]))
    asof = fl.get("asof", "")
    summ = fl.get("stance_summary", {}) or {}
    # Stance one-liner: list only non-zero buckets so future Support/Conditional types show.
    order = [("Oppose", "#993c1d"), ("Conditional", "#a8830d"), ("Support", "#3b6d11")]
    parts = [f'<span style="color:{c};font-weight:600;">{summ.get(s,0)} {s}</span>'
             for s, c in order if summ.get(s, 0)]
    stance_line = ", ".join(parts) if parts else "—"

    # Hypothetical combined line: docketed corpus + form-letter submitters, percentages
    # recomputed against the combined total. Labeled as a hypothetical; the headline cards
    # above stay at the docketed count.
    combined_html = ""
    if corpus_counts and corpus_counts.get("total"):
        c_total = corpus_counts["total"]
        comb_total = c_total + total
        seg = []
        for s, color in order:
            c_n = corpus_counts.get(s, 0)
            f_n = summ.get(s, 0)
            comb = c_n + f_n
            if comb == 0:
                continue
            pct = (comb / comb_total * 100) if comb_total else 0
            add = f" ({c_n} + {f_n})" if f_n else ""
            seg.append(
                f'<span style="color:{color};font-weight:600;">{comb} {s}</span>'
                f'<span style="color:#777;">{add} = {pct:.1f}%</span>'
            )
        combined_html = (
            '<p style="margin:10px 0 0;font-size:13px;color:#444;line-height:1.5;'
            'border-top:1px dashed #e0dacf;padding-top:10px;">'
            '<strong>If the form-letter submitters are added to the docketed letters</strong> '
            f'(hypothetical, not the headline count): <strong>{comb_total}</strong> total '
            f'({c_total} + {total}) — ' + ", ".join(seg) + '. '
            '<span style="color:#777;">Shown for scale only; the two tallies are reported separately '
            'above because the form-letter submitters are anonymous and may overlap with named letters.</span>'
            '</p>'
        )

    rows = []
    for t in fl["types"]:
        text_html = _html.escape(t.get("text", "")).replace("\n", "<br>")
        stance = t.get("stance", "")
        scolor = dict(order).get(stance, "#555")
        rows.append(
            '<tr>'
            f'<td style="padding:6px 10px;font-weight:600;white-space:nowrap;">Type {_html.escape(t.get("type",""))}</td>'
            f'<td style="padding:6px 10px;text-align:right;font-variant-numeric:tabular-nums;">{t.get("submitter_count",0)}</td>'
            f'<td style="padding:6px 10px;"><span style="color:{scolor};font-weight:600;">{_html.escape(stance)}</span></td>'
            f'<td style="padding:6px 10px;color:#444;font-style:italic;">&ldquo;{text_html}&rdquo;</td>'
            '</tr>'
        )
    rows_html = "\n".join(rows)

    return f'''<section id="form-letters" style="margin:14px 0 4px;border:1px solid #e6e1d8;border-radius:10px;background:#faf8f4;padding:16px 18px;">
  <div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 14px;">
    <h2 style="margin:0;font-size:16px;">SEC form letters <span style="color:#777;font-weight:400;font-size:14px;">(aggregated)</span></h2>
    <span style="font-size:13px;color:#555;">{total} submitters across {n_types} template types · {stance_line}</span>
  </div>
  <p style="margin:8px 0 0;font-size:13px;color:#555;line-height:1.5;">
    The SEC posts campaign / form letters as a template text plus a submitter count, without docketing the individual
    submissions. These are tracked separately from the <strong>{{CORPUS_N}}</strong> individually-classified letters above
    and are <strong>not summed</strong> with them: the submitter counts are anonymous and may overlap with named letters.
    Held out of the classification statistics and the regression. As reported by the SEC as of {asof}.
  </p>
  <table style="margin:12px 0 0;border-collapse:collapse;font-size:13px;width:100%;">
    <thead>
      <tr style="text-align:left;color:#777;border-bottom:1px solid #e0dacf;">
        <th style="padding:4px 10px;font-weight:600;">Type</th>
        <th style="padding:4px 10px;font-weight:600;text-align:right;">Submitters</th>
        <th style="padding:4px 10px;font-weight:600;">Stance</th>
        <th style="padding:4px 10px;font-weight:600;">Template text</th>
      </tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  {combined_html}
</section>'''


def regenerate_html(snapshot, asof_iso, records=None, with_voting=False):
    snapshot_js = json.dumps(snapshot, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__RECORDS__", snapshot_js).replace("__ASOF__", asof_iso)
    # SEC aggregate form-letter panel (side by side with the per-letter corpus, never summed
    # in the headline; the panel shows a labeled hypothetical combined line).
    fl = load_form_letters()
    corpus_n = len(snapshot)
    corpus_counts = {"total": corpus_n}
    for s in ("Oppose", "Conditional", "Support"):
        corpus_counts[s] = sum(1 for r in snapshot if r.get("stance") == s)
    html = html.replace("__FORM_LETTER_PANEL__",
                        build_form_letter_panel(fl, corpus_counts).replace("{CORPUS_N}", str(corpus_n)))
    # Regression panel — three-spec stacked layout, numbers from _meta/regression_compare.json
    reg = load_regression_compare()
    html = html.replace("__REGRESSION_PANEL__", build_regression_panel(reg))
    # Travel-notice banner. Shows in the dev mirror, and in production when
    # SHOW_TRAVEL_NOTICE is True. Set that flag back to False when the trip ends.
    travel_html = TRAVEL_NOTICE_HTML if (with_voting or SHOW_TRAVEL_NOTICE) else ""
    html = html.replace("__TRAVEL_NOTICE__", travel_html)
    stats = compute_method_stats(records or [])
    if stats:
        for k, v in stats.items():
            html = html.replace(f"METHOD_{k.upper()}", str(v))
    else:
        for tok in ["METHOD_N", "METHOD_UNANIMOUS_N", "METHOD_UNANIMOUS_PCT",
                    "METHOD_MAJORITY_N", "METHOD_MAJORITY_PCT",
                    "METHOD_FLEISS_K", "METHOD_K_PL", "METHOD_K_PS", "METHOD_K_LS",
                    "METHOD_ENT_N", "METHOD_ENT_UNANIMOUS_N", "METHOD_ENT_UNANIMOUS_PCT",
                    "METHOD_ENT_MAJORITY_N", "METHOD_ENT_MAJORITY_PCT", "METHOD_ENT_FLEISS_K",
                    "METHOD_ENT_DIST",
                    "METHOD_RAT_N", "METHOD_RAT_UNANIMOUS_N", "METHOD_RAT_UNANIMOUS_PCT",
                    "METHOD_RAT_MAJORITY_N", "METHOD_RAT_MAJORITY_PCT",
                    "METHOD_RAT_SPLIT_N", "METHOD_RAT_SPLIT_PCT",
                    "METHOD_RAT_MEAN_K", "METHOD_RAT_PERCODE", "METHOD_RAT_FREQNOTE"]:
            html = html.replace(tok, "—")
    if with_voting:
        sb_url, sb_key = load_supabase_creds()
        html = html.replace("__SUPABASE_URL__", sb_url or "")
        html = html.replace("__SUPABASE_ANON_KEY__", sb_key or "")
        # Embed letter bodies inline so the modal works even from file:// (no fetch needed).
        bodies = load_letter_bodies()
        html = html.replace("__BODIES_INLINE__", json.dumps(bodies, ensure_ascii=False))
    else:
        # Production: even without voting, the feedback widget still wants Supabase if set up.
        sb_url, sb_key = load_supabase_creds()
        # No voting block — but feedback JS will check SUPABASE_LIVE which doesn't exist in prod.
        # Production strips the voting block which contains SUPABASE_LIVE; the feedback JS guards
        # with `typeof SUPABASE_LIVE !== 'undefined'` so it just falls through to mailto. That's fine.
        html = _strip_voting_blocks(html)
    # GoatCounter analytics snippet — same on prod and dev. Picked up from _meta/.goatcounter_code.
    html = html.replace("__GOATCOUNTER__", load_goatcounter_snippet())
    return html


def write_public_files():
    if not RECORDS_PATH.exists():
        sys.stderr.write(f"ERROR: missing {RECORDS_PATH}\n")
        sys.exit(2)

    records = json.loads(RECORDS_PATH.read_text())
    snapshot = build_snapshot(records)
    asof = datetime.date.today().isoformat()

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    # Production build: NO voting widget. This is what gets pushed to GitHub.
    PUBLIC_HTML.write_text(regenerate_html(snapshot, asof, records=records, with_voting=False))
    PUBLIC_JSON.write_text(json.dumps(snapshot, indent=2))
    # Refresh bodies.json on the production side too so the pushed file is not stale.
    # The production HTML does not load bodies.json directly (voting is dev-only) but
    # the file lives in FILES_TO_PUSH and there is no reason to leave it stale.
    bodies_prod = load_letter_bodies()
    if bodies_prod:
        PUBLIC_BODIES.write_text(json.dumps(bodies_prod, ensure_ascii=False))

    # Dev mirror with voting widget enabled — local preview only, never pushed.
    if BUILD_DEV_MIRROR:
        PUBLIC_DEV_DIR.mkdir(parents=True, exist_ok=True)
        PUBLIC_DEV_HTML.write_text(regenerate_html(snapshot, asof, records=records, with_voting=True))
        PUBLIC_DEV_JSON.write_text(json.dumps(snapshot, indent=2))
        bodies = load_letter_bodies()
        if bodies:
            PUBLIC_DEV_BODIES.write_text(json.dumps(bodies, ensure_ascii=False))
        # Mirror the taxonomy HTML. The dev-only file at _meta/rationale-taxonomy-dev.html
        # carries the extended "A note on IP specifically" callout (two-point commentary)
        # that Tzachi has kept in dev for further reflection. If absent, fall back to prod.
        taxonomy_dev_src = META_DIR / "rationale-taxonomy-dev.html"
        taxonomy_prod_src = PUBLIC_DIR / "rationale-taxonomy.html"
        if taxonomy_dev_src.exists():
            (PUBLIC_DEV_DIR / "rationale-taxonomy.html").write_text(taxonomy_dev_src.read_text())
        elif taxonomy_prod_src.exists():
            (PUBLIC_DEV_DIR / "rationale-taxonomy.html").write_text(taxonomy_prod_src.read_text())
        print(f"[build:dev] Wrote {PUBLIC_DEV_HTML.relative_to(PROJECT_DIR)} (with voting widget — preview only, NOT pushed)")

    print(f"[build] Wrote {PUBLIC_HTML.relative_to(PROJECT_DIR)}  ({len(snapshot)} letters, asof {asof})")
    print(f"[build] Wrote {PUBLIC_JSON.relative_to(PROJECT_DIR)}")
    return records, snapshot, asof


# ---- GitHub push step ------------------------------------------------------

def gh_request(method, path, token, body=None):
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "sec-tracker-build/1.0",
            "Content-Type": "application/json" if data else "application/octet-stream",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body}
    except urllib.error.URLError as e:
        return -1, {"error": str(e.reason)}


def push_file_to_github(remote_path, local_path, token, commit_msg):
    """Create-or-update a file in the repo via the Contents API."""
    api_path = f"/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{remote_path}"

    # Get current sha (if file exists). 404 means create-new.
    status, data = gh_request("GET", f"{api_path}?ref={GITHUB_BRANCH}", token)
    sha = data.get("sha") if status == 200 else None

    content_b64 = base64.b64encode(local_path.read_bytes()).decode("ascii")
    body = {
        "message": commit_msg,
        "content": content_b64,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        body["sha"] = sha

    put_status, put_data = gh_request("PUT", api_path, token, body)
    if put_status not in (200, 201):
        raise RuntimeError(f"PUT {remote_path} failed (status {put_status}): {put_data}")
    commit_sha = put_data.get("commit", {}).get("sha", "")[:7]
    print(f"[push] {remote_path}  commit {commit_sha}")
    return commit_sha


# ---- Main ------------------------------------------------------------------

def _dropbox_running():
    """Best-effort detection of a live macOS Dropbox process. Returns False on
    Linux / CI runners (no Dropbox there), so the Action is unaffected."""
    import subprocess
    try:
        r = subprocess.run(["pgrep", "-x", "Dropbox"],
                           capture_output=True, text=True, timeout=2)
        return r.returncode == 0
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-push", action="store_true",
                    help="Build the public HTML/JSON locally but do not push to GitHub.")
    ap.add_argument("--dev", action="store_true",
                    help="Also build public_site_dev/ with the voting widget enabled. "
                         "public_site_dev/ is NEVER pushed — local preview only.")
    ap.add_argument("--message", default=None,
                    help="Commit message override.")
    args = ap.parse_args()

    global BUILD_DEV_MIRROR
    BUILD_DEV_MIRROR = args.dev

    # Dropbox-race warning. Issue a nudge to use push_safely.sh whenever Dropbox
    # is alive on this host. Soft warning only — not a block — because the user
    # may have just paused sync manually via the menu bar.
    if _dropbox_running() and not args.no_push:
        sys.stderr.write(
            "\n[warn] Dropbox is running on this host. Bidirectional sync can "
            "revert _meta/renumbered_records.json mid-build and result in a "
            "stale push to GitHub.\n"
            "       Recommended: bash _scripts/push_safely.sh  (auto-pauses "
            "Dropbox for the build window).\n"
            "       Or pause Dropbox manually via the menu bar before "
            "continuing.\n\n"
        )

    records, snapshot, asof = write_public_files()

    if args.no_push:
        print("[done] Built locally only (--no-push).")
        return

    if not TOKEN_PATH.exists():
        sys.stderr.write(
            f"\nERROR: missing GitHub token file at {TOKEN_PATH}\n"
            f"Create it with:\n"
            f"  echo 'YOUR_PAT_HERE' > '{TOKEN_PATH}'\n"
            f"  chmod 600 '{TOKEN_PATH}'\n"
            f"\nSkipping push.\n"
        )
        sys.exit(3)

    token = TOKEN_PATH.read_text().strip()
    if not token:
        sys.stderr.write("ERROR: token file is empty\n")
        sys.exit(3)

    msg = args.message or f"Auto-update tracker: {len(snapshot)} letters as of {asof}"
    for remote_path, local_path in FILES_TO_PUSH.items():
        push_file_to_github(remote_path, local_path, token, msg)

    print(f"[done] Pushed {len(FILES_TO_PUSH)} files to {GITHUB_USER}/{GITHUB_REPO}")


if __name__ == "__main__":
    main()
