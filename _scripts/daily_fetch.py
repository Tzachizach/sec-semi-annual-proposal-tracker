#!/usr/bin/env python3
"""
Daily fetch of new SEC S7-2026-15 comment letters.

Runs from GitHub Actions on a daily cron (09:00 UTC = 5 AM ET). The script:

  1. Pulls the SEC comment-letter index for the docket (pages 1-3).
  2. Diffs the URLs against `_meta/renumbered_records.json`.
  3. For each new URL, fetches the letter HTML, extracts commenter name +
     body, and appends a placeholder record with stance / entity / rationales
     all set to "Unclassified".
  4. Writes a Letters/NN_*.md file with the unclassified header so the
     leakage-free for-models mirror picks it up on the next rebuild.

Classification (the 3-rater Claude ensemble for stance, entity, rationale)
stays a manual Cowork-session task. The Action only handles fetch + placeholder
write + build + commit. The public site's `build_snapshot` filter (see
build_and_push.py) excludes Unclassified rows from the visible table so
the docket displays only fully-classified letters.

Run locally for testing (will hit SEC.gov):
    python3 _scripts/daily_fetch.py

Dependencies: requests, beautifulsoup4. Installed in the Actions workflow.
"""
import json
import re
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e}\n"
        "Install with: pip install requests beautifulsoup4\n"
    )
    sys.exit(2)

PROJECT_DIR = Path(__file__).resolve().parent.parent
RECORDS = PROJECT_DIR / "_meta" / "renumbered_records.json"
LETTERS_DIR = PROJECT_DIR / "Letters"
PDF_DIR = PROJECT_DIR / "_meta" / "pdf_letters"

# SEC docket index — Drupal-based comments page on sec.gov.
# Pagination uses ?page=N (zero-indexed). Letter URLs in the table point at
# the older /comments/S7-2026-15/... path (mixed case S7).
DOCKET_INDEX_URL = "https://www.sec.gov/rules-regulations/public-comments/s7-2026-15"

# SEC requires a real User-Agent. Use the project contact email.
USER_AGENT = "OSU-Fisher SEC tracker zach.7@osu.edu"
# Cache-Control hints push past SEC's CloudFront layer, which has been observed
# serving stale snapshots of page 0 (see STATUS §3 — the original Cowork task
# missed new letters for the same reason).
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# Crawl more pages than seem necessary. The docket grows ~30 letters/day at peak,
# so 8 pages × ~30 rows ≈ a week of headroom even if we miss a day.
PAGES_TO_CHECK = 8


def fetch(url, timeout=30):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text


def fetch_response(url, timeout=30):
    """Return the full Response so we can inspect Content-Type and body bytes."""
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r


def is_pdf_url(url):
    return url.lower().split("?")[0].endswith(".pdf")


def is_pdf_response(resp):
    return "pdf" in (resp.headers.get("Content-Type") or "").lower()


def is_html_stub_for_pdf(html):
    """Heuristic: the HTML 'wrapper' pages SEC sometimes serves for PDF letters
    have no commenter body — usually just a 'View as PDF' link or an embedded
    PDF viewer. If we cannot find a 'From:' line, treat it as a stub.
    """
    if "From:" in html:
        return False
    # Trigger words on typical PDF-wrapper pages
    return any(
        marker in html.lower()
        for marker in ("application/pdf", "<embed ", "<iframe", "view as pdf", ".pdf\"")
    )


def index_page_url(page_n):
    """SEC paginates the Drupal comments page via `?page=N`, 0-indexed.

    Appends a unix-timestamp `_t` parameter to bust CloudFront's URL-level cache.
    The SEC backend ignores unknown query params; the CDN treats the URL as new.
    """
    bust = int(time.time())
    sep = "&" if "?" in DOCKET_INDEX_URL else "?"
    if page_n == 0:
        return f"{DOCKET_INDEX_URL}{sep}_t={bust}"
    return f"{DOCKET_INDEX_URL}{sep}page={page_n}&_t={bust}"


def parse_index(html, base_url):
    """Return [{date, name, url}] for each Public Comment row.

    The Drupal page renders a `<table>` with three columns (Date, Letter Type,
    Commenter Name) and an `<a>` inside the Commenter Name cell pointing at the
    letter at /comments/S7-2026-15/...
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("tr"):
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue
        date = tds[0].get_text(strip=True)
        ctype = tds[1].get_text(strip=True)
        name_cell = tds[2]
        a = name_cell.find("a", href=True)
        name = name_cell.get_text(strip=True)
        if "Public Comment" not in ctype:
            continue
        if not a:
            continue
        url = urllib.parse.urljoin(base_url, a["href"])
        # Only accept letter URLs in /comments/ — skip any extra links on the row.
        if "/comments/" not in url.lower():
            continue
        rows.append({"date": date, "name": name, "url": url})
    return rows


def normalize_date(date_str):
    """Convert 'May 16, 2026' to '2026-05-16'. Fall through unchanged on parse error."""
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str


def parse_letter(html, source_url):
    """Extract commenter name + body from an SEC comment-letter page."""
    soup = BeautifulSoup(html, "html.parser")
    # Drop scripts and styles so they don't pollute the text dump
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text("\n", strip=False)
    # Body and From line live after "Subject: File No. ..."
    m_from = re.search(r"From:\s*(.+)", text)
    name = m_from.group(1).strip() if m_from else "Unknown"
    if m_from:
        body = text[m_from.end():].strip()
    else:
        body = text.strip()
    # Collapse repeated blank lines
    body = re.sub(r"\n{3,}", "\n\n", body)
    return name, body


def lid(url):
    """letter_id = last numeric segments of the URL filename.

    URLs come in two shapes:
      .../s7202615-{prefix}-{tail}.html   (most common)
      .../s7202615-{tail}.htm             (some older ones, e.g. Chris Ridder)
    Capture whichever form is present.
    """
    m = re.search(r"s7202615-((?:\d+-)?\d+(?:_\d+)?)\.html?$", url, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    return url.rsplit("/", 1)[-1].replace(".html", "").replace(".htm", "")


def fname_safe(name, max_len=30):
    s = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return s[:max_len].rstrip("_") or "Unknown"


def split_name_role(raw):
    """'Tim Mulligan, attorney' -> ('Tim Mulligan', 'attorney').
       'Sherri' -> ('Sherri', 'Individual')."""
    if "," in raw:
        commenter, role = raw.split(",", 1)
        commenter = commenter.strip()
        role = role.strip()
        return commenter, role or "Individual"
    return raw.strip(), "Individual"


def normalize_url(u):
    """Lowercase + collapse the s7 case variants for diffing."""
    return u.strip().lower()


def main():
    if not RECORDS.exists():
        print(f"[error] {RECORDS} not found.", file=sys.stderr)
        return 1
    records = json.loads(RECORDS.read_text())
    print(f"[info] Loaded {len(records)} existing records.")

    existing = set()
    for r in records:
        u = normalize_url(r["url"])
        existing.add(u)
        # also accept the case-flipped version of /s7-2026-15/ vs /S7-2026-15/
        existing.add(u.replace("/s7-2026-15/", "/S7-2026-15/").lower())
        existing.add(u.replace("/S7-2026-15/", "/s7-2026-15/").lower())

    new_rows = []
    seen_urls = set()
    for page in range(0, PAGES_TO_CHECK):
        page_url = index_page_url(page)
        print(f"[fetch] index page {page}: {page_url}")
        try:
            html = fetch(page_url)
        except Exception as e:
            print(f"[warn] index page {page} fetch failed: {e}")
            continue
        rows = parse_index(html, page_url)
        print(f"[fetch] page {page}: {len(rows)} Public Comment rows")
        for r in rows:
            nu = normalize_url(r["url"])
            if nu in seen_urls or nu in existing:
                continue
            seen_urls.add(nu)
            new_rows.append(r)
        time.sleep(0.5)

    if not new_rows:
        print("[done] No new letters.")
        return 0

    print(f"[info] {len(new_rows)} new letter(s) to fetch.")
    next_n = max(r["n"] for r in records) + 1
    appended = 0
    pdfs_saved = 0
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    for r in new_rows:
        # Decide upfront whether this is a PDF (by URL suffix). PDF letters
        # need a different handling path: download bytes, save to _meta/pdf_letters/,
        # write a placeholder Letters/NN_*.md so the next Cowork session knows
        # to read the PDF and fill in body + classification.
        is_pdf = is_pdf_url(r["url"])
        body = ""
        commenter = r["name"]
        role = "Individual"
        words = 0
        pdf_filename = ""

        try:
            resp = fetch_response(r["url"])
        except Exception as e:
            print(f"[warn] letter fetch failed ({r['url']}): {e}")
            continue

        # Promote to PDF path if URL did not signal but response Content-Type did.
        if not is_pdf and is_pdf_response(resp):
            is_pdf = True

        if is_pdf:
            # Save PDF bytes to _meta/pdf_letters/<basename>.pdf
            pdf_filename = r["url"].rsplit("/", 1)[-1].split("?")[0]
            if not pdf_filename.lower().endswith(".pdf"):
                pdf_filename += ".pdf"
            pdf_path = PDF_DIR / pdf_filename
            pdf_path.write_bytes(resp.content)
            pdfs_saved += 1

            raw_name = r["name"]
            commenter, role = split_name_role(raw_name)
            body = (
                f"(PDF letter — text extraction pending. "
                f"PDF saved at _meta/pdf_letters/{pdf_filename}. "
                f"Open the PDF and replace this body with the extracted text "
                f"before the next classification pass.)"
            )
            words = 0
            print(f"[pdf]    #{next_n} {commenter[:35]:35s} (PDF) -> _meta/pdf_letters/{pdf_filename}")
        else:
            html = resp.text
            # If the HTML is actually a stub pointing at a PDF, handle the same way
            if is_html_stub_for_pdf(html):
                raw_name = r["name"]
                commenter, role = split_name_role(raw_name)
                body = (
                    f"(Letter served as an HTML stub wrapping a PDF. "
                    f"Open {r['url']} in a browser, save the linked PDF to "
                    f"_meta/pdf_letters/, then replace this body with the "
                    f"extracted text before the next classification pass.)"
                )
                words = 0
                is_pdf = True  # flag for the print/summary line
                print(f"[stub]   #{next_n} {commenter[:35]:35s} (HTML-stub-for-PDF)")
            else:
                name_from_letter, body = parse_letter(html, r["url"])
                raw_name = r["name"] or name_from_letter
                commenter, role = split_name_role(raw_name)
                words = len(body.split())

        rec = {
            "n": next_n,
            "page": 1,
            "date": normalize_date(r["date"]),
            "name": commenter,
            "role": role,
            "entity": "Unclassified",
            "stance": "Unclassified",
            "primary_stance": "Unclassified",
            "literalist_stance": "Unclassified",
            "skeptic_stance": "Unclassified",
            "majority_stance": "Unclassified",
            "agreement": "",
            "entity_primary": "Unclassified",
            "entity_selfdescribed": "Unclassified",
            "entity_letterhead": "Unclassified",
            "entity_majority": "Unclassified",
            "entity_agreement": "",
            "rationales": [],
            "rationale_evidence": "",
            "rationales_primary": [],
            "rationales_literalist": [],
            "rationales_inclusive": [],
            "rationales_majority": [],
            "rationale_agreement": "",
            "summary": "(PDF — awaiting manual processing.)" if is_pdf else "(Awaiting Claude classification.)",
            "url": r["url"],
            "words": words,
            "letter_id": lid(r["url"]),
        }
        records.append(rec)

        # Letters/NN_*.md placeholder file. Includes a "_pdf" tag in the
        # filename when applicable so PDF-pending records are easy to grep.
        slug = fname_safe(commenter)
        pdf_tag = "_pdf" if is_pdf else ""
        fpath = LETTERS_DIR / f"{rec['n']}_{slug}{pdf_tag}_{rec['letter_id']}.md"
        header = (
            f"# Letter {rec['n']} — {commenter}\n\n"
            f"- **Date:** {rec['date']}\n"
            f"- **Role/Affiliation:** {role}\n"
            f"- **Stance:** Unclassified\n"
            f"- **Entity:** Unclassified\n"
            f"- **Rationales:** \n"
            f"- **Source:** {r['url']}\n"
        )
        if is_pdf and pdf_filename:
            header += f"- **PDF:** _meta/pdf_letters/{pdf_filename}\n"
        header += (
            f"\n---\n\n"
            f"Subject: File No. S7-2026-15\n"
            f"From: {commenter}\n\n"
            f"{body}\n"
        )
        fpath.write_text(header)
        if not is_pdf:
            print(f"[append] #{rec['n']} {commenter[:35]:35s} ({words}w) -> {fpath.name}")
        next_n += 1
        appended += 1
        time.sleep(0.5)  # gentle on SEC

    RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"[done] Appended {appended} letter(s). {len(records)} total records.")
    if pdfs_saved:
        print(f"[done] Saved {pdfs_saved} PDF(s) to _meta/pdf_letters/.")
        print(f"[notice] PDF-pending letters need manual body extraction "
              f"in the next Cowork session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
