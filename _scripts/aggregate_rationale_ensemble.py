"""Aggregate three LLM-rater rationale outputs and compute per-code Cohen's κ.

Inputs (all under _meta/):
  rationale_primary.json     — canonical primary classifications (n, name, rationales)
  rationale_rater_literalist.json — LLM Literalist pass (n, name, rationales, evidence)
  rationale_rater_inclusive.json  — LLM Inclusive pass (n, name, rationales, evidence)

Outputs:
  rationale_three_rater.json — per-letter trio + majority + per-letter agreement flag;
                                per-code κ table; overall mean κ.
  renumbered_records.json    — adds rationales_primary, rationales_literalist,
                                rationales_inclusive, rationales_majority,
                                rationale_agreement.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "_meta"

ALL_CODES = [
    "IA", "FR", "MF", "AU", "ICc", "EX", "CMP", "CC", "SG",   # anti
    "CB", "ST", "OP", "OV", "ICs",                              # pro
    "AL",                                                        # conditional
    "LE",                                                        # procedural
    "IP", "US", "RI",                                            # commenter-distinctive
    "NR",                                                        # other
]


def cohen_kappa_binary(a: list[bool], b: list[bool]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for ai, bi in zip(a, b) if ai == bi) / n
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def main():
    primary = json.loads((META / "rationale_primary.json").read_text())
    literalist = json.loads((META / "rationale_rater_literalist.json").read_text())
    inclusive = json.loads((META / "rationale_rater_inclusive.json").read_text())

    P = {r["n"]: r.get("rationales", []) for r in primary}
    L = {r["n"]: r.get("rationales", []) for r in literalist}
    I = {r["n"]: r.get("rationales", []) for r in inclusive}

    ns = sorted(P.keys())
    rows = []
    for n in ns:
        p = P.get(n, [])
        l = L.get(n, [])
        i = I.get(n, [])
        majority = []
        for code in ALL_CODES:
            votes = (code in p) + (code in l) + (code in i)
            if votes >= 2:
                majority.append(code)

        if set(p) == set(l) == set(i):
            agreement = "unanimous"
        elif set(p) == set(l) or set(p) == set(i) or set(l) == set(i):
            agreement = "majority"
        else:
            agreement = "split"

        rows.append({
            "n": n,
            "name": next((r["name"] for r in primary if r["n"] == n), ""),
            "primary": p,
            "literalist": l,
            "inclusive": i,
            "majority": majority,
            "agreement": agreement,
        })

    # Per-code Cohen's κ — three pairwise
    per_code = {}
    for code in ALL_CODES:
        pv = [code in P[n] for n in ns]
        lv = [code in L[n] for n in ns]
        iv = [code in I[n] for n in ns]
        pl = cohen_kappa_binary(pv, lv)
        pi = cohen_kappa_binary(pv, iv)
        li = cohen_kappa_binary(lv, iv)
        # Mean pairwise — when a κ is undefined (e.g., all same), treat as 1.0 if frequencies agree, 0 if not
        valid = [k for k in (pl, pi, li) if k == k]  # filter nan
        mean_k = sum(valid) / len(valid) if valid else float("nan")
        per_code[code] = {
            "primary_vs_literalist": round(pl, 3),
            "primary_vs_inclusive": round(pi, 3),
            "literalist_vs_inclusive": round(li, 3),
            "mean_pairwise": round(mean_k, 3) if mean_k == mean_k else None,
            "frequencies": {"primary": sum(pv), "literalist": sum(lv), "inclusive": sum(iv)},
        }

    valid_codes = [c for c in ALL_CODES if per_code[c]["mean_pairwise"] is not None]
    mean_k_overall = sum(per_code[c]["mean_pairwise"] for c in valid_codes) / len(valid_codes)

    agreement_dist = Counter(row["agreement"] for row in rows)

    # Write three-rater summary
    (META / "rationale_three_rater.json").write_text(json.dumps({
        "n_letters": len(rows),
        "raters": {
            "primary": "LLM (Claude Opus 4.7) — balanced rubric. Canonical classification.",
            "literalist": "LLM (Claude Opus 4.7) — strict rubric. Only codes families with explicit surface invocation.",
            "inclusive": "LLM (Claude Opus 4.7) — expansive rubric. Codes any plausibly-invoked family.",
        },
        "agreement_distribution": dict(agreement_dist),
        "mean_kappa_across_codes": round(mean_k_overall, 3),
        "per_code_kappa": per_code,
        "letters": rows,
    }, indent=2, ensure_ascii=False))

    # Merge into renumbered_records.json
    records = json.loads((META / "renumbered_records.json").read_text())
    rows_by_n = {row["n"]: row for row in rows}
    for r in records:
        row = rows_by_n.get(r["n"])
        if not row:
            continue
        r["rationales_primary"] = row["primary"]
        r["rationales_literalist"] = row["literalist"]
        r["rationales_inclusive"] = row["inclusive"]
        r["rationales_majority"] = row["majority"]
        r["rationale_agreement"] = row["agreement"]
        # Public-facing `rationales` switches to majority (mirrors stance/entity convention)
        r["rationales"] = row["majority"]
    (META / "renumbered_records.json").write_text(json.dumps(records, indent=2, ensure_ascii=False))

    # Print summary
    print(f"3-rater ensemble on N={len(rows)} letters")
    print(f"Agreement: {dict(agreement_dist)}  "
          f"({100*agreement_dist['unanimous']/len(rows):.1f}% unanimous, "
          f"{100*agreement_dist['majority']/len(rows):.1f}% majority, "
          f"{100*agreement_dist['split']/len(rows):.1f}% split)")
    print(f"Mean per-code κ across pairs: {mean_k_overall:.3f}")
    print()
    print("Per-code κ:")
    print(f"  {'Code':<5} {'mean κ':>7} {'P×L':>6} {'P×I':>6} {'L×I':>6}   {'fP':>3} {'fL':>3} {'fI':>3}")
    for code in sorted(ALL_CODES, key=lambda c: -(per_code[c]["mean_pairwise"] or -1)):
        v = per_code[code]
        mk = v["mean_pairwise"]
        f = v["frequencies"]
        mk_s = f"{mk:.2f}" if mk is not None else "  - "
        print(f"  {code:<5} {mk_s:>7}  {v['primary_vs_literalist']:>+5.2f}  {v['primary_vs_inclusive']:>+5.2f}  {v['literalist_vs_inclusive']:>+5.2f}    {f['primary']:>3} {f['literalist']:>3} {f['inclusive']:>3}")
    print()
    # Final public-facing code freq (majority)
    c = Counter()
    for row in rows:
        for code in row["majority"]:
            c[code] += 1
    print("Public-facing (majority) code freq:")
    for k, v in c.most_common():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
