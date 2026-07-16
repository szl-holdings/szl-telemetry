#!/usr/bin/env python3
"""Daily telemetry snapshot for the SZLHOLDINGS Hugging Face estate.

Honest scope (do not overclaim):
- Samples Hugging Face PUBLIC API cumulative counters once per run: downloads
  (models, datasets; HF's own counting semantics) and likes (models, datasets,
  spaces). Point-in-time, UTC-stamped.
- Day-over-day deltas are DERIVED from consecutive snapshots, not measured.
- No uniqueness, user-count, or quality claims. v1 does NOT track discussions,
  clones, or Spaces runtime usage.
Stdlib only. Deterministic file layout: data/daily/YYYY-MM-DD.json (overwritten
if re-run same day), data/downloads.csv (regenerated from all dailies).
"""
import csv, datetime, json, pathlib, urllib.request

ORG = "SZLHOLDINGS"
ROOT = pathlib.Path(__file__).resolve().parent.parent
FLAGSHIPS = [
    "SZLHOLDINGS/SZL-Khipu-1.5B-BrainNavigator",
    "SZLHOLDINGS/SZL-Forge-1.5B-ReceiptAgent",
    "SZLHOLDINGS/SZL-Khipu-1.5B-GGUF",
]

def fetch(kind: str, expands: list[str]) -> list[dict]:
    q = "&".join(f"expand[]={e}" for e in expands)
    url = f"https://huggingface.co/api/{kind}?author={ORG}&limit=500&{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "szl-telemetry/1"})
    with urllib.request.urlopen(req, timeout=60) as f:
        return json.loads(f.read())

def main() -> None:
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    rows = []
    for kind, expands in (("models", ["downloads", "likes"]),
                          ("datasets", ["downloads", "likes"]),
                          ("spaces", ["likes"])):
        for it in fetch(kind, expands):
            rows.append({
                "date": today, "type": kind[:-1], "repo": it["id"],
                "downloads": it.get("downloads"), "likes": it.get("likes", 0),
            })
    rows.sort(key=lambda r: (r["type"], r["repo"]))
    daily = ROOT / "data" / "daily" / f"{today}.json"
    daily.write_text(json.dumps({"sampledAtUtcDate": today, "rows": rows}, indent=1) + "\n")

    all_rows = []
    for p in sorted((ROOT / "data" / "daily").glob("*.json")):
        all_rows.extend(json.loads(p.read_text())["rows"])
    with (ROOT / "data" / "downloads.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "type", "repo", "downloads", "likes"])
        w.writeheader(); w.writerows(all_rows)

    # README trend block: baseline + deltas vs 1/7/14 days ago where history exists.
    by_repo_date = {(r["repo"], r["date"]): r for r in all_rows}
    dates = sorted({r["date"] for r in all_rows})
    def cell(repo, back):
        if len(dates) <= back: return "—"
        cur, ref = by_repo_date.get((repo, dates[-1])), by_repo_date.get((repo, dates[-1 - back]))
        if not cur or not ref or cur["downloads"] is None or ref["downloads"] is None: return "—"
        d = cur["downloads"] - ref["downloads"]
        return f"{d:+d}"
    lines = ["| repo | downloads (cum.) | Δ1d | Δ7d | Δ14d |", "|---|---|---|---|---|"]
    for repo in FLAGSHIPS:
        cur = by_repo_date.get((repo, dates[-1]), {})
        lines.append(f"| [{repo.split('/')[1]}](https://huggingface.co/{repo}) | "
                     f"{cur.get('downloads', '—')} | {cell(repo,1)} | {cell(repo,7)} | {cell(repo,14)} |")
    lines.append("")
    lines.append(f"_Last snapshot: {dates[-1]} UTC · counters are HF-reported cumulative"
                 " downloads; deltas DERIVED from consecutive daily snapshots._")
    readme = ROOT / "README.md"
    txt = readme.read_text()
    start, end = "<!-- TREND:START -->", "<!-- TREND:END -->"
    pre, _, rest = txt.partition(start); _, _, post = rest.partition(end)
    readme.write_text(pre + start + "\n" + "\n".join(lines) + "\n" + end + post)
    print(f"snapshot {today}: {len(rows)} repos")

if __name__ == "__main__":
    main()
