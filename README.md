# SEC S7-2026-15 — Public comment letter tracker

Live tracker for public comment letters submitted on the SEC's proposed rule **S7-2026-15** (Optional Semiannual Reporting by Public Companies).

Data is read once and baked into `index.html`. The page renders entirely client-side using Chart.js.

## What's in this folder

- `index.html` — the dashboard. Self-contained, no build step. Open it locally in a browser to test.
- `data.json` — same data as a separate JSON file (currently informational only; future automation can read this).
- `README.md` — this file.

## Publishing on GitHub Pages — step by step

1. **Create a GitHub account** if you don't have one: <https://github.com/signup>. Free.
2. **Create a new repository.** Click the "+" in the top right, choose "New repository". Name it something like `sec-s7-2026-15-tracker`. Set it to **Public** (required for free GitHub Pages). Skip the README option since this folder already has one. Click "Create repository".
3. **Upload these files.** On the new empty repo page, click "uploading an existing file". Drag `index.html`, `data.json`, and `README.md` into the upload area. Scroll down, click "Commit changes".
4. **Enable Pages.** Click the **Settings** tab in your repo → in the left sidebar, **Pages**. Under "Build and deployment", set the Source to **Deploy from a branch**, Branch = **main**, Folder = **/ (root)**. Click Save.
5. **Wait ~30 seconds.** Refresh the Pages settings page. You'll see a banner: "Your site is live at `https://<your-username>.github.io/sec-s7-2026-15-tracker/`". Click it.

That's it — the dashboard is now publicly accessible.

## Updating the data later

The cleanest way to refresh the published version: regenerate `index.html` (by re-running the Cowork pipeline), then on GitHub:

1. Open the repo, click `index.html`
2. Click the pencil icon (Edit)
3. Paste the new file contents
4. Scroll down, "Commit changes"

Or via the GitHub Desktop app, or `git push` from a local clone — whatever's most comfortable.

## What the dashboard shows

- **Total / Oppose / Support / Conditional** stat cards with percentages
- **Letters per day** — stacked bar by stance
- **Stance totals** — horizontal bar with percentages
- **Longest letters** — top 5 by word count, useful for identifying substantive submissions
- **All letters** — sortable, searchable table

Last updated: 2026-05-09
Source: <https://www.sec.gov/rules-regulations/public-comments/s7-2026-15>
