# szl-telemetry

Daily public-API telemetry snapshots for the [SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS)
Hugging Face estate. Exists to answer one question honestly: **does momentum
survive the launch spike?**

## What this measures (and what it does not)

- **Measured:** Hugging Face public-API cumulative counters, sampled once per
  UTC day — `downloads` (models, datasets; HF's counting semantics apply) and
  `likes` (models, datasets, spaces). Point-in-time samples.
- **DERIVED:** day-over-day deltas computed from consecutive snapshots. A delta
  is only as good as the two samples around it.
- **Not claimed:** unique users, install base, quality, or adoption. Not
  tracked in v1: discussions, clones, Spaces runtime usage (no stable public
  counter).

## Flagship momentum

<!-- TREND:START -->
| repo | downloads (cum.) | Δ1d | Δ7d | Δ14d |
|---|---|---|---|---|
| [SZL-Khipu-1.5B-BrainNavigator](https://huggingface.co/SZLHOLDINGS/SZL-Khipu-1.5B-BrainNavigator) | 1033 | — | — | — |
| [SZL-Forge-1.5B-ReceiptAgent](https://huggingface.co/SZLHOLDINGS/SZL-Forge-1.5B-ReceiptAgent) | 780 | — | — | — |
| [SZL-Khipu-1.5B-GGUF](https://huggingface.co/SZLHOLDINGS/SZL-Khipu-1.5B-GGUF) | 189 | — | — | — |

_Last snapshot: 2026-07-16 UTC · counters are HF-reported cumulative downloads; deltas DERIVED from consecutive daily snapshots._
<!-- TREND:END -->

## Layout

- `data/daily/YYYY-MM-DD.json` — one snapshot per UTC day (idempotent per day)
- `data/downloads.csv` — long-format regeneration of all dailies
- `scripts/snapshot.py` — stdlib-only sampler; also rewrites the trend block above
- `.github/workflows/snapshot.yml` — daily cron + manual dispatch

Run locally: `python3 scripts/snapshot.py`
