# NSE hourly pattern screen — rally + rounded base near highs

| | |
|---|---|
| **Executed at** | **2026-09-08 02:52 IST** (`run_ts_ist`) |
| **Latest data bar** | **2026-09-07 15:15 IST** — the **2026-09-07** (Monday) session |
| **Session age** | 1 day behind the run date (`session_age_days = 1`) |
| **Universe / interval** | NSE **EQ**, 1h candles |
| **Charts** | https://claude.ai/code/artifact/889b219e-ebb9-40f9-9fd7-53f885304085 |

**This report covers the 2026-09-07 session, not "today".** The run fired at
02:52 IST on 2026-09-08, i.e. after midnight IST but before the 2026-09-08
market opened, so the newest closed hourly candle available is Monday's 15:15
close. That is the expected post-midnight timing artifact, not a stale feed —
an age of 1 day is exactly one calendar rollover, well inside the range where
the data is trustworthy.

These are **candidates matching a geometry, not recommendations.** Entry,
sizing, and whether to trade at all are your calls.

---

## 1. Coverage

| Metric | Value |
|---|---|
| Symbols in universe (EQ series) | 2,305 |
| Symbols with usable data | **2,267 (98.4%)** |
| Symbols carrying the last closed bar | 2,145 / 2,267 (**94.6%**) |
| Universe consensus last bar | 2026-09-07 15:15:00 (2,145 symbols) |
| Market open at run time | No — final bar kept, not dropped |

38 symbols were dropped: 11 returned no data from Yahoo at all, 27 had too few
bars. A rate-limit burst around batches 37–38 was recovered by the gap-fill
rounds; the second gap-fill round recovered nothing, which is the pipeline's
signal that the remaining names are genuinely absent from the feed rather than
throttled. Missing names include ALFREDHE, APOORVA, ARYAMAN, ASSAMENT, ASTAR,
AUGMONT, ESDS, GKB, GRAVISSHO, KANCOTEA. **This is a 98% scan, not a complete
one.**

`pct_at_last_bar` is 94.6, so the universe's last bar is not every symbol's
price time — but all 11 hits below have `bars_behind_universe = 0`, meaning
every quoted level is priced at 2026-09-07 15:15:00. No hit needs a
different timestamp.

## 2. Funnel

```
2,305 symbols in EQ universe
2,267 with usable hourly data          (-38: no data / too few bars)
   29 raw pattern hits                 (detector: rally + parabolic base, R² + curvature)
   11 clean hits                       (-18 by context filters)
```

The 18 rejections, with the filter that cut each:

| Symbol | Cut by |
|---|---|
| HBLENGINE | not-at-high 84.0%, gap-driven 1.04 |
| NORTHARC | not-at-high 93.2%, gap-driven 1.28 |
| AEGISVOPAK | not-at-high 93.4% |
| NGLFINE | illiquid ₹1.67cr, not-at-high 82.6% |
| BALRAMCHIN | not-at-high 92.5%, gap-driven 0.66 |
| AVADHSUGAR | not-at-high 96.1%, gap-driven 0.79 |
| GODREJAGRO | gap-driven 0.92 |
| JINDALPOLY | illiquid ₹0.47cr, not-at-high 95.0%, gap-driven 0.63 |
| BLBLIMITED | illiquid ₹0.10cr, gap-driven 1.88 |
| DEEDEV | not-at-high 90.8% |
| ZIMLAB | illiquid ₹0.52cr |
| NAGREEKCAP | illiquid ₹0.00cr, not-at-high 80.0%, gap-driven 0.55 |
| RPTECH | not-at-high 91.7% |
| UNICHEMLAB | illiquid ₹3.48cr, not-at-high 85.6% |
| RENUKA | not-at-high 92.4%, gap-driven 1.23 |
| BROOKS | illiquid ₹0.05cr, not-at-high 87.8%, gap-driven 0.90 |
| VINCOFE | gap-driven 0.67 |
| 3BBLACKBIO | illiquid ₹1.37cr |

Two filters did most of the work: **not-at-high** (the base has to sit within
3% of the 60-day high — 12 names failed it, several badly: NGLFINE at 82.6%,
NAGREEKCAP at 80.0%) and **illiquid** (7 names under the turnover floor).
**gap-driven** removed 8 names whose "rally" was one outsized candle. Note that
the three highest-R² raw hits — ZIMLAB 0.819, RPTECH 0.839, NGLFINE 0.855 —
were all rejected. Fit quality on its own predicts nothing.

## 3. Ranked table

Ranked by `rrr_structural` (target ÷ risk-to-base-low), best first. All levels
as of the 2026-09-07 15:15 bar.

| # | Symbol | Close | Entry | RRR | Base depth | Risk to base low | Dist from lip | Base bars | R² | Vol ratio | Turnover |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CAPLIPOINT | 2814.00 | 2874.30 | 3.76 | 3.99% | 3.99% | 2.10% | 19 (≈2.8 sess) | 0.518 | 0.53 | ₹12.9cr |
| 2 | UFLEX | 682.70 | 707.60 | 2.72 | 5.51% | 5.51% | 3.52% | 22 (≈3.2) | 0.567 | 0.45 | ₹9.9cr |
| 3 | ATLANTAELE | 1942.10 | 1958.00 | 2.67 | 5.62% | 5.62% | 0.81% | 18 (≈2.6) | 0.712 | 0.64 | ₹17.8cr |
| 4 | AEROFLEX | 558.15 | 561.70 | 2.53 | 5.94% | 5.94% | 0.63% | 29 (≈4.2) | 0.635 | 0.45 | ₹37.3cr |
| 5 | KENNAMET | 4693.00 | 4799.80 | 2.50 | 6.01% | 6.01% | 2.23% | 28 (≈4.1) | 0.545 | 0.53 | ₹11.8cr |
| 6 | MANINDS | 822.00 | 826.95 | 2.44 | 6.16% | 6.16% | 0.60% | 16 (≈2.3) | 0.541 | 0.66 | ₹32.4cr |
| 7 | YATHARTH | 994.80 | 1019.00 | 2.40 | 6.26% | 6.26% | 2.37% | 30 (≈4.4) | 0.686 | 0.24 | ₹16.7cr |
| 8 | UNIPARTS | 902.10 | 908.00 | 2.35 | 6.39% | 6.39% | 0.65% | 21 (≈3.1) | 0.654 | 0.62 | ₹7.6cr |
| 9 | MOREPENLAB | 118.88 | 122.00 | 1.95 | 7.70% | 7.70% | 2.56% | 17 (≈2.5) | 0.539 | 0.63 | ₹136.3cr |
| 10 | TECHNOCRAF | 390.00 | 397.20 | 1.75 | 8.56% | 8.56% | 1.81% | 22 (≈3.2) | 0.698 | 0.70 | ₹29.3cr |
| 11 | SSWL | 369.85 | 383.45 | 1.65 | 9.11% | 9.11% | 3.55% | 21 (≈3.1) | 0.588 | 0.21 | ₹11.6cr |

**RRR ranks the geometry, not the odds.** It states what the trade pays if it
works and is silent on how often it works. CAPLIPOINT tops the table only
because its base is the shallowest — which, as the visual pass below finds, is
mostly because it has had the least *time*, not because it is the soundest
structure.

## 4. Tiers from the visual pass

I opened `hits.png` and read all eleven panels. The tiers below are my
disagreement with the ranking where I have one.

### Clean structural match (4)

- **UFLEX** — the best rally in the batch: a genuine staircase from ~580 to 710
  across three weeks, no single candle carrying it (max bar share 0.34). The
  base drifts down to 668 and flattens 670–685 with the fast EMAs pinned under
  it and now curling up through the right edge. Little overhead supply above
  the 2 Sep lip. Ranks second, and I would rank it first.
- **AEROFLEX** — 29-bar base, the second-longest, on a clean 458→568 climb.
  Down, flat, then up: it actually rounds. EMAs run under the base and rise
  into it. The only caveat is the 1 Sep spike high at ~568 that forms the lip;
  price is already 0.63% from it, so there is very little room before entry.
- **KENNAMET** — 3,560→4,800 with several sizeable but not dominant candles
  (max bar share 0.43). The base is a proper dip-and-recover U from 4,700 to
  4,450 and back, and the last bars are pressing the lip. Lowest R² in the top
  five (0.545), which here is fine — a rounded base with real chop in it fits
  a parabola worse than a clean V does.
- **YATHARTH** — the longest base (30 bars, ≈4.4 sessions) and the driest
  volume (ratio 0.24), which is what you want in a base. Shape rounds properly.
  The one real concern is **overhead supply**: the 1,000–1,020 zone was heavily
  traded on 31 Aug–1 Sep, and that is exactly where the entry sits.

### Marginal (4)

- **CAPLIPOINT (rank 1)** — this is a **flag, not a rounded base.** The stock
  went sideways at 2,500–2,550 for two weeks, then made one near-vertical move
  on 2 Sep from ~2,700 to ~2,870. The "base" is three sessions of digestion
  directly under that thrust. It is orderly and it is holding, but the shallow
  3.99% depth that gives it the top RRR is an artifact of the base having had
  no time to develop, not of a tight, mature structure. Treat the 3.76 RRR as
  the least trustworthy number in the table.
- **MANINDS** — base is only 16 bars (≈2.3 sessions), the shortest in the
  batch, and the final candle is an outsized push straight into the lip. Entry
  at 826.95 is 0.60% above the close, so acting on it means chasing a bar that
  has already moved. Not enough base to call it a base yet.
- **MOREPENLAB** — 7.7% of drawdown compressed into 2.5 sessions is a sharp
  pullback, not a rounded base; the panel shows a V from 122 down to 112.6 and
  back to 119. The underlying 88→122 advance is genuinely sustained and the
  liquidity is by far the best here (₹136cr/day), which is why I have it
  marginal rather than distrusted — but the base shape is not what the
  screener claims it is.
- **TECHNOCRAF** — the cleanest *rally* in the batch (300→400, textbook
  staircase across the whole window), but it passed **exactly on the boundary**
  of the max-bar-share filter (0.50 vs a cut of 0.50). A boundary pass is not
  the same evidence as a margin pass. It is also already thrusting into the
  lip on the final bars, so the 8.56% structural risk is being taken from a
  point that has already run.

### Distrust despite passing every filter (3)

- **ATLANTAELE (rank 3, highest R² at 0.712)** — textbook case of the
  parabola-fits-a-V problem. The prior structure is whippy, not trending:
  1,750 → 1,720 → 1,870 → 1,660 on 27 Aug → and only then a fast run to 1,950.
  The "base" is a sharp drop to 1,848 and an equally sharp recovery — a V, and
  the high R² is *because* of that, not despite it. It also only cleared the
  at-high filter by three-tenths of a point (97.3% vs a 97.0% floor). Two
  independent reasons to stand back.
- **UNIPARTS** — dead flat at 815–825 for nine sessions, then a two-day
  vertical from 810 to 910. That profile is an event, not an accumulation. The
  base that follows is a V down to 850 and straight back to 902, and the 850
  low is set by **a single wick** (see §5). Skip.
- **SSWL** — a 26% rally compressed into roughly three sessions off a *falling*
  base (the stock was drifting 315→295 until 29 Aug), then a 9.11% V-shaped
  pullback. This is a pullback inside an extended vertical move, not a base
  near highs after an orderly advance. It ranks last on RRR and I would rank it
  last on structure too — the two agree here.

## 5. Risk reality check — the stop-inside-base problem

**A 3% stop is incompatible with all eleven names.** Every base here is deeper
than 3%, so a fixed 3%-off-the-lip stop lands *inside* the cup and gets taken
out by ordinary chop with the pattern completely intact. The pipeline confirms
this: `stop_inside_base = true`, 11 of 11.

| Symbol | Entry | 3% stop level | Base low (structural stop) | 3% assumed risk | **Real structural risk** | Multiple |
|---|---|---|---|---|---|---|
| CAPLIPOINT | 2874.30 | 2788.07 | 2759.60 | 3.00% | **3.99%** | 1.3× |
| UFLEX | 707.60 | 686.37 | 668.60 | 3.00% | **5.51%** | 1.8× |
| ATLANTAELE | 1958.00 | 1899.26 | 1847.90 | 3.00% | **5.62%** | 1.9× |
| AEROFLEX | 561.70 | 544.85 | 528.35 | 3.00% | **5.94%** | 2.0× |
| KENNAMET | 4799.80 | 4655.81 | 4511.10 | 3.00% | **6.01%** | 2.0× |
| MANINDS | 826.95 | 802.14 | 776.00 | 3.00% | **6.16%** | 2.1× |
| YATHARTH | 1019.00 | 988.43 | 955.20 | 3.00% | **6.26%** | 2.1× |
| UNIPARTS | 908.00 | 880.76 | 850.00 | 3.00% | **6.39%** | 2.1× |
| MOREPENLAB | 122.00 | 118.34 | 112.60 | 3.00% | **7.70%** | 2.6× |
| TECHNOCRAF | 397.20 | 385.28 | 363.20 | 3.00% | **8.56%** | 2.9× |
| SSWL | 383.45 | 371.95 | 348.50 | 3.00% | **9.11%** | 3.0× |

Honoring the structure means position sizes between **1.3× and 3.0× smaller**
than a 3%-stop assumption implies. On SSWL and TECHNOCRAF the gap is close to
threefold, which changes the reward/risk arithmetic entirely — and both are
names I have already flagged on shape grounds.

**Wick-set base low — UNIPARTS.** Its base low of 850.00 sits **1.02% of entry**
below the next lowest bar in the base. The closing-basis floor is 867.60, i.e.
**4.45% risk instead of 6.39%**. The wick is a real traded price, so `base_low`
and the RRR ranking correctly keep using it as the conservative stop — but that
single bar is also what pushed UNIPARTS down to rank 8, so its low placement is
not by itself evidence of poor structure. **The sizing above assumes the wick
(6.39%).** If you size off the closing basis instead, say so explicitly to
yourself; you are accepting that a repeat of that wick stops you out.

**Boundary passes.** Two names cleared a filter by nothing at all:
ATLANTAELE (`pct_of_60d_high` 97.3% vs a 97.0% floor) and TECHNOCRAF
(`max_bar_share` 0.50 vs a cut of 0.50). Both are tiered below "clean" above,
partly for that reason.

## 6. Regime dependence

Bases near highs resolve upward far more often in a trending index than in a
choppy one; the same screener on the same universe has a very different hit
rate in the two. **Whether this pattern is present today is a different
question from whether it is worth trading today**, and only a backtest split by
index trend state answers the second. I have not run one.

## 7. What was not changed

No detector threshold, filter parameter, or ranking rule was touched on this
run. The screener ran once, exited 0, and produced 11 clean hits from 29 raw
ones under the standing configuration.

Two calibration observations, recorded and **not acted on**:

- `max_bar_share` at a 0.50 cut lets a name through on exact equality
  (TECHNOCRAF). Whether the cut should be exclusive is a judgement call worth
  making deliberately — not mid-run.
- The 12-bar minimum base length admits bases of ~2.3 sessions (MANINDS), which
  on visual inspection are hard to distinguish from ordinary pullbacks. Three
  of the four names I tiered "marginal" have bases under 3 sessions. If this
  keeps recurring across runs, the floor is the parameter to look at.

---

*Charts (all 11 panels, full resolution):
https://claude.ai/code/artifact/889b219e-ebb9-40f9-9fd7-53f885304085*

*Data: yfinance hourly OHLCV, fetched 2026-09-08 02:57 IST. Chart EMAs are
matplotlib renderings and seed differently from TradingView/Kite — verify every
price on your own platform before acting.*
