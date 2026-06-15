#!/usr/bin/env python3
"""Plot the docket-posting lag, poll by poll, from the internal lag log.

Reads the per-poll summaries in `_meta/docket_lag_log.json` (written by
`update_lag_log.py` every poll) and renders a single chart:

  * mean lag       — line + markers, value labels
  * median lag     — dashed line
  * min..max band  — shaded range for each poll
  * n (new letters)— annotated under each poll's x-tick

The lag log is gitignored / internal, so the PNG is too. Re-run this after
`update_lag_log.py` on any poll to refresh the chart.

Usage:
    python3 _scripts/plot_lag_by_day.py
    python3 _scripts/plot_lag_by_day.py [log=_meta/docket_lag_log.json] [out=_meta/docket_lag_by_day.png]

Lag = (pull_date) - (docket "Date Received"), in days. One point per poll.
"""
import json
import sys
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def main() -> int:
    log_path = sys.argv[1] if len(sys.argv) > 1 else "_meta/docket_lag_log.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "_meta/docket_lag_by_day.png"

    try:
        log = json.load(open(log_path))
    except FileNotFoundError:
        print(f"[error] lag log not found at {log_path} — run update_lag_log.py first.", file=sys.stderr)
        return 1

    entries = sorted(log.get("entries", []), key=lambda e: e["pull_date"])
    if not entries:
        print("[error] no poll entries in the lag log yet.", file=sys.stderr)
        return 1

    x      = [date.fromisoformat(e["pull_date"]) for e in entries]
    mean   = [e["mean_lag_days"]   for e in entries]
    median = [e["median_lag_days"] for e in entries]
    lo     = [e["min_lag_days"]    for e in entries]
    hi     = [e["max_lag_days"]    for e in entries]
    n_new  = [e.get("n_new", 0)    for e in entries]

    fig, ax = plt.subplots(figsize=(11, 6))

    # min..max band
    ax.fill_between(x, lo, hi, color="#4C72B0", alpha=0.15, label="min–max range")
    # median (dashed)
    ax.plot(x, median, color="#55A868", linestyle="--", linewidth=1.6, marker="o",
            markersize=4, label="median lag")
    # mean (solid, emphasized)
    ax.plot(x, mean, color="#C44E52", linewidth=2.2, marker="o", markersize=6, label="mean lag")

    # value labels on the mean points
    for xi, mi in zip(x, mean):
        ax.annotate(f"{mi:.1f}", (xi, mi), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color="#C44E52")

    # n annotations under the axis
    ymin = min(lo) - (max(hi) - min(lo)) * 0.12
    for xi, ni in zip(x, n_new):
        ax.annotate(f"n={ni}", (xi, ymin), ha="center", va="top", fontsize=7, color="#555555")

    ax.set_title("SEC S7-2026-15 — docket-posting lag by poll", fontsize=13, fontweight="bold")
    ax.set_ylabel("Lag (days): pull date − docket 'Date Received'")
    ax.set_xlabel("Poll (pull) date")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %-d"))
    ax.set_ylim(bottom=ymin)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(loc="upper left", framealpha=0.9)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    print(f"[done] wrote {out_path}  ({len(entries)} polls, "
          f"{x[0]:%Y-%m-%d} → {x[-1]:%Y-%m-%d}; latest mean {mean[-1]:.1f}d)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
