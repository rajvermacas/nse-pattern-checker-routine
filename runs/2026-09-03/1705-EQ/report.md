# NSE hourly pattern screen — rally + rounded base near highs

| | |
|---|---|
| **Executed at** | **2026-09-03 17:05:59 IST** (`run_ts_ist`) — wall-clock start of this run |
| **Latest data bar** | **2026-09-03 15:15:00 IST** (`last_closed_bar`) — session `2026-09-03`, `session_age_days` = 0 |

The latest available session is the same date as the run, and the run fired after the
15:30 IST close, so this is a complete, post-close scan of **the 3 September 2026
session**. Nothing here is stale.

**Chart (all 15 panels, full resolution):** https://claude.ai/code/artifact/e96fd82a-2494-4dd2-a090-db7c857def7f

> **These are candidates matching a geometry, not recommendations.** The structural
> RRR column ranks the *shape* of the trade — what it pays if it works. It says nothing
> about how often it works, and the top-ranked name is not a buy.

---

## Coverage

| Metric | Value |
|---|---|
| Universe | **EQ series — 2,289 symbols** (the skill's default and widest slice; not a narrowed index) |
| Symbols with usable hourly data | **2,245 / 2,289 = 98%** |
| Symbols carrying the reported last bar | 2,162 / 2,245 = **96.3%** |
| Universe consensus last bar | 2026-09-03 15:15:00 (2,162 symbols) — same as the reported last bar |
| Interval / period | 1h / 60d |

44 symbols returned no usable hourly history from the feed after two gap-fill rounds
(round 1 recovered 21, round 2 recovered 0 — the remainder are genuinely absent from
Yahoo rather than throttled) and are **not** in this scan. Examples: ALFREDHE, ANSALBU,
APOORVA, ARYAMAN, ASSAMENT, ASTAR, AUGMONT, CRAVATEX, GAJA, GKB.

`pct_at_last_bar` is 96.3, and **all 15 surviving hits have `bars_behind_universe` = 0** —
every price quoted below is the 15:15 bar. No per-hit staleness adjustment was needed.

### One environmental fix was applied before this run

The first invocation exited **40** at the universe stage: `nsearchives.nseindia.com`
returned **HTTP 403 Access Denied** for `EQUITY_L.csv`. The egress proxy reported no
relay failures, so the block was NSE's edge, not the network path. Testing showed the
edge now refuses the entire Chrome/Chromium user-agent family regardless of version
(Chrome/139, /146, /152 and Edge/146 all 403) while Gecko passes (Firefox/145 → 200) —
a change from the version-floor behaviour the script's own comment documented on
2026-08-20. **The fix was the user-agent string in `fetch_universe.py`, nothing else.**
No detector threshold, filter parameter or ranking rule was touched. The re-run
(one re-run only) completed with exit 0.

---

## Funnel

| Stage | Count | What the filter cut |
|---|---:|---|
| Symbols scanned | 2,245 | 0 crashed |
| Raw detector hits | **42** | Rally + parabola-fit rounded base near highs |
| After context filters | **15** | 27 rejected — see below |

**The 27 rejections, by reason** (a name can fail more than one):

- **Illiquid** (< ₹5cr/day turnover) — 17 names: RSL (3.73cr), NITINSPIN (4.08cr),
  VENKEYS (4.19cr), ATLANTAA (0.09cr), GRAUWEIL (1.03cr), SPORTKING (4.55cr),
  KAPSTON (1.93cr), GENUSPAPER (0.04cr), ALMONDZ (0.09cr), IKIO (1.88cr),
  JAIBALAJI (2.76cr), DMCC (0.84cr), PLATIND (0.79cr), MACPOWER (4.61cr),
  TTL (0.08cr), SIMPLEXINF (0.79cr), SHREEPUSHK (1.89cr), LANCORHOL (0.47cr),
  LANCER (0.28cr), INDIANHUME (0.59cr), TFL (0.00cr).
- **Not at highs** (< 97% of the 60-day high) — 13 names, worst first: ATLANTAA (82.0%),
  GRAUWEIL (83.0%), SHIPROCKET (89.2%), TEJASNET (90.0%), TFL (91.4%), IKIO (92.5%),
  DMCC (93.4%), INDIANHUME (93.8%), PLATIND (93.9%), EXICOM (94.0%), NORTHARC (94.1%),
  SIMPLEXINF (94.1%), TTL (94.3%), GENUSPAPER (94.9%), ATLANTAELE (95.7%).
- **Gap-driven** (one bar carrying too much of the rally) — 14 names: TTL (1.43),
  TEJASNET (1.01), INDIANHUME (0.98), NORTHARC (0.95), DMCC (0.87), EXICOM (0.86),
  SHIPROCKET (0.80), IKIO (0.79), VENKEYS (0.70), MACPOWER (0.66), MANINDS (0.65),
  SIMPLEXINF (0.61), LANCER (0.57), KAPSTON (0.54), GENUSPAPER (0.55), ATLANTAA (0.53),
  TFL (0.51).

---

## Ranked table — the 15 survivors

Ranked by structural RRR (target ÷ risk-to-base-low), best first.

| # | Symbol | Close | Entry (lip) | Base low | Base depth | Rally | Base bars | R² | Dist. from lip | Vol ratio | Turnover ₹cr | T2 | **Structural RRR** |
|--:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | ENTERO | 1,848.00 | 1,863.00 | 1,790.50 | 3.89% | 29.62% | 19 | 0.792 | 0.81% | 0.13 | 15.9 | 2,142.45 | **3.86** |
| 2 | ENGINERSIN | 280.80 | 284.90 | 273.80 | 3.90% | 18.11% | 18 | 0.550 | 1.44% | 0.67 | 36.2 | 327.63 | **3.85** |
| 3 | MANINFRA | 124.59 | 125.55 | 119.61 | 4.73% | 12.19% | 15 | 0.497 | 0.76% | 0.82 | 11.9 | 144.38 | **3.17** |
| 4 | SAIL | 197.00 | 200.65 | 190.27 | 5.17% | 15.76% | 28 | 0.565 | 1.82% | 0.42 | 239.3 | 230.75 | **2.90** |
| 5 | BALAMINES | 2,424.00 | 2,505.80 | 2,372.50 | 5.32% | 12.43% | 13 | 0.644 | 3.26% | 0.79 | 18.1 | 2,881.67 | **2.82** |
| 6 | LICHSGFIN | 554.00 | 555.15 | 525.25 | 5.39% | 11.61% | 28 | 0.791 | 0.21% | 0.66 | 83.0 | 638.42 | **2.78** |
| 7 | INOXINDIA | 2,176.20 | 2,200.00 | 2,079.10 | 5.50% | 19.18% | 20 | 0.606 | 1.08% | 0.20 | 17.6 | 2,530.00 | **2.73** |
| 8 | SETL | 387.65 | 393.65 | 370.00 | 6.01% | 30.29% | 19 | 0.684 | 1.52% | 0.46 | 16.3 | 452.70 | **2.50** |
| 9 | LALITHAA | 281.90 | 282.90 | 262.60 | 7.18% | 16.47% | 19 | 0.768 | 0.35% | 0.65 | 229.6 | 325.33 | **2.09** |
| 10 | GIPCL | 208.04 | 211.54 | 196.01 | 7.34% | 23.38% | 30 | 0.689 | 1.65% | 0.39 | 10.5 | 243.27 | **2.04** |
| 11 | MOL | 67.52 | 68.75 | 63.30 | 7.93% | 14.03% | 19 | 0.624 | 1.79% | 0.37 | 6.0 | 79.06 | **1.89** |
| 12 | URBANCO | 177.51 | 179.06 | 164.20 | 8.30% | 19.58% | 28 | 0.754 | 0.87% | 0.52 | 96.4 | 205.92 | **1.81** |
| 13 | IOLCP | 196.43 | 202.98 | 186.10 | 8.32% | 17.41% | 21 | 0.461 | 3.23% | 0.66 | 31.7 | 233.43 | **1.80** |
| 14 | CGCL | 272.10 | 272.70 | 249.00 | 8.69% | 17.70% | 26 | 0.871 | 0.22% | 0.34 | 56.6 | 313.60 | **1.73** |
| 15 | MANALIPETC | 89.00 | 90.88 | 82.45 | 9.28% | 24.24% | 13 | 0.832 | 2.07% | 0.77 | 7.1 | 104.51 | **1.62** |

**Boundary passes — 4 of 15 cleared a filter by its last decimal, not by a margin:**

| Symbol | Flag |
|---|---|
| LICHSGFIN | `pct_of_60d_high` 97.3% vs floor 97.0 |
| INOXINDIA | `pct_of_60d_high` 97.2% vs floor 97.0 |
| LALITHAA | `max_bar_share` 0.50 vs cut 0.50 |
| MANALIPETC | `max_bar_share` 0.50 vs cut 0.50 |

A boundary pass is not the same evidence as a margin pass.

---

## Stop-inside-base check — read this before the tiers

`risk_pct_to_base_low` is the distance from the entry (base high) down to the base low:
the *real* structural stop. A fixed 3% stop is compared against it below.

| Symbol | 3% stop | Structural stop (`risk_pct_to_base_low`) | Compatible? |
|---|---:|---:|---|
| ENTERO | 3.00% | 3.89% | **No** — 3% stop sits inside the base |
| ENGINERSIN | 3.00% | 3.90% | **No** — 3% stop sits inside the base |
| MANINFRA | 3.00% | 4.73% | **No** — 3% stop sits inside the base |
| SAIL | 3.00% | 5.17% | **No** — 3% stop sits inside the base |
| BALAMINES | 3.00% | 5.32% | **No** — 3% stop sits inside the base |
| LICHSGFIN | 3.00% | 5.39% | **No** — 3% stop sits inside the base |
| INOXINDIA | 3.00% | 5.50% | **No** — 3% stop sits inside the base |
| SETL | 3.00% | 6.01% | **No** — 3% stop sits inside the base |
| LALITHAA | 3.00% | 7.18% | **No** — 3% stop sits inside the base |
| GIPCL | 3.00% | 7.34% | **No** — 3% stop sits inside the base |
| MOL | 3.00% | 7.93% | **No** — 3% stop sits inside the base |
| URBANCO | 3.00% | 8.30% | **No** — 3% stop sits inside the base |
| IOLCP | 3.00% | 8.32% | **No** — 3% stop sits inside the base |
| CGCL | 3.00% | 8.69% | **No** — 3% stop sits inside the base |
| MANALIPETC | 3.00% | 9.28% | **No** — 3% stop sits inside the base |

**15 of 15 are incompatible.** Every single name has its base low further than 3% below
the entry, so a 3% stop would be triggered by ordinary movement *within* the base that
the pattern is built on — it is noise, not protection. The shallowest base on the list
(ENTERO, 3.89%) is still 30% wider than a 3% stop; the widest (MANALIPETC, 9.28%) is
more than three times it. Either size the position against the structural stop, or don't
take the setup. The `sl` field in `hits_clean.json` is that same fixed-% stop and carries
the same problem.

---

## Visual pass — every panel was looked at

The panels were examined one by one. Sorting, with reasons.

### Clean structural match — 4 of 15

**ENTERO** — 29.6% rally spread across 45 bars with no single bar carrying it
(`max_bar_share` 0.22): a genuine staircase from ~1,400 to ~1,850, not a step. The
19-bar base holds 1,790–1,863 on a real volume dry-up (`vol_ratio` 0.13) and price is
pressing the lip at the close. The base is a tight flat shelf rather than a deep cup —
the rounding is shallow — but that is the *good* version of this pattern, not the
degenerate one. Fast EMAs run under the base and rise through it. Best name on the page.

**GIPCL** — the most developed base here: 30 bars, a clear dip to 196 and a curve back
to 208, sitting under a 211.54 lip. The rally is the best-distributed of all fifteen
(`max_bar_share` 0.17), and there's a legitimate rounded bottom to the left of it on
13–21 Aug. Caveat: ₹10.5cr/day is thin, only just over the ₹5cr floor.

**SETL** — 30.3% over 45 bars, the second-best-distributed rally (0.23). The advance from
~300 to ~390 is a real multi-week staircase, and the base is a shallow, tidy consolidation
at 370–394 lifting into the close. Structurally sound.

**SAIL** — a steady 170→200 climb across the entire window, then a genuine rounded
pullback to 190 and back to 197 over 28 bars. By a wide margin the most liquid name on
the list (₹239cr/day), which matters for actually getting filled. R² of 0.565 understates
this one; the curve is real on the chart.

### Marginal — 5 of 15

**URBANCO** — the rounded pullback is real and liquidity is good (₹96cr), but 46% of the
rally sits in one bar around 21 Aug, and an 8.3% base depth makes the structural stop
uncomfortably wide relative to the 15% target.

**MANINFRA** — a genuine, steady uptrend, but R² 0.497 is the second-worst here and the
15-bar "base" is a two-session pause, not a structure. Not enough base to define a stop
with confidence.

**LICHSGFIN** — there *is* a real rounded bottom on 21–25 Aug, but price is already
extending vertically at the right edge of the chart. An entry at 555.15 against a 554.00
close means chasing an hour that has already happened. Also an edge pass on the at-highs
floor (97.3% vs 97.0).

**BALAMINES** — a short 13-bar base sitting 3.26% below the lip, with obvious overhead
supply left behind at the 2,506 spike high. The 21–27 Aug leg was near-vertical; the
chop since is digestion, not a base yet.

**CGCL** — carries the highest R² on the page (0.871), which is precisely the warning the
routine flags: a V fits a parabola better than a rounded base does. On the chart the
base's right side is a near-vertical ramp into the lip rather than a curve, the last
candles are extended, and the structural stop is 8.69% away for a 1.73 RRR.

### Distrust despite passing every filter — 6 of 15

**ENGINERSIN** (ranked #2 by RRR) — textbook one-candle-plus-drift. A single bar on
31 Aug runs 255 → 290; price then drifts down and sideways in the 275–285 range. 48% of
the rally is that one bar (`max_bar_share` 0.48) and R² is 0.550. What the detector
calls a base is the decay off a spike. **The second-highest RRR on this list is a name
I would not trade.**

**INOXINDIA** — the same failure, more extreme. Flat at ~1,950 from 13 to 27 Aug, then
one vertical candle to ~2,250, then a descending drift to 2,100–2,150. 46% in one bar,
plus a boundary pass on the at-highs floor. Not a base; a hangover.

**IOLCP** — worst R² on the page (0.461). Price fell from 200 to 186, chopped, and
recovered on one violent bar at the right edge. Nothing in that sequence is a rounded
base, and it sits 3.23% under its lip.

**LALITHAA** — the series only starts 24 Aug: roughly two weeks of hourly history, versus
the ~3 weeks every other panel shows, with one monster candle at the left edge. Combined
with a boundary pass on `max_bar_share` (0.50 vs a 0.50 cut), there is not enough chart
here to judge the pattern.

**MOL** — `rally_bars` is 8. The shaded window shows price ramping upward, not basing,
and at ₹6.0cr/day it is the thinnest name that cleared the liquidity floor.

**MANALIPETC** — shortest base (13 bars ≈ 1.9 sessions), widest structural stop (9.28%),
worst structural RRR (1.62), and a boundary pass on `max_bar_share`. The base's right
side is another vertical push into the lip.

---

## Notes on thresholds

Nothing was loosened to manufacture hits, and no threshold was re-run at a different
setting. The only change made this session was the `fetch_universe.py` user-agent string,
which was required to reach NSE's symbol-list host at all.

One observation worth recording, **not acted on**: the `max_bar_share` cut of 0.50 let
two names through at exactly 0.50, and the two worst gap-driven charts on the list
(ENGINERSIN 0.48, INOXINDIA 0.46) sit just under it. On this session's evidence that cut
appears too loose to do the job it exists for. Flagging it here; leaving it alone.

Similarly, the detector's R² is doing less work than its rank suggests — the highest-R²
name (CGCL, 0.871) is a marginal chart and the fourth-highest (LALITHAA, 0.768) is
untrustworthy, while two of the four cleanest charts sit at 0.565 and 0.689. That is the
V-fits-a-parabola problem, and it is why the visual pass is not optional.
