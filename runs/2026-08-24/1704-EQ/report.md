# NSE hourly screen — rally + rounded base near highs

**Executed at:** 2026-08-24 17:04 IST (`run_ts_ist`; data snapshot completed 17:09 IST)
**Latest data bar:** 2026-08-24 15:15 IST — `session_date` 2026-08-24, `session_age_days` 0

The last closed bar is from **today's session**. This is a same-day screen, run after
the 15:30 close, so no in-progress bar was dropped — the 15:15 stub is a genuine close.

**Chart (full resolution, all 10 panels + per-name verdicts):**
https://claude.ai/code/artifact/eed52007-4b72-453b-baf3-8ddbc2929428

---

## 1. Coverage

| | |
|---|---|
| Universe | **EQ** (full NSE rolling-settlement list) — the skill's default, not a narrowed slice |
| Symbols in universe | 2,296 |
| Symbols with usable data | **2,108 (91.8%)** |
| Not examined | 188 — all dropped as `too_few_bars` (recent listings without 60 days of hourly history, plus symbols that do not map cleanly to `SYMBOL.NS` on Yahoo) |
| Interval / period | 1h / 60d |
| Last closed bar | 2026-08-24 15:15:00 IST |
| Symbols carrying that bar | 2,007 of 2,108 (**95.2%**) — also the universe consensus bar |

**This is not a complete scan of the NSE EQ universe.** 188 names were never examined.
A gap-fill pass was attempted and recovered zero symbols, which indicates the missing
names are genuinely absent from Yahoo rather than rate-limited.

All 10 hits below have `bars_behind_universe = 0`, so every one is priced at the
15:15 bar — no hit is quoted at a stale timestamp.

## 2. Funnel — what each stage removed

```
2,296  EQ universe
2,108  with usable data          −188  too_few_bars
   35  raw detector hits       −2,073  EMA stack / rising EMAs / rally ≥10% /
                                       curvature ≥0.015 / R² ≥0.45 / depth ≤10% /
                                       within 4% of the lip
   10  after context filters      −25  see below
    2  clean on sight              −8  4 marginal, 4 distrusted (section 4)
```

The 25 context-filter rejections, most failing on more than one count:

| Filter | Cut | What it catches |
|---|---|---|
| Liquidity < ₹5cr/day | **20** | Pretty geometry, unfillable entry. Worst: BEEKAY ₹0.04cr, SRD ₹0.05cr, TEXMOPIPES ₹0.07cr |
| Gap-driven (one bar > 50% of the rally) | **16** | Gap-and-base, not rally-and-base — a different setup with different odds. Worst: GIPCL 1.84, BEEKAY 1.50, TEXMOPIPES 1.45 |
| Not at the 60-day high (< 97%) | **5** | Downtrend bounce into overhead supply reading as "base near the window high": IFCI 87.1%, DLINKINDIA 82.8%, SIGMA 86.8%, MAYURUNIQ 86.9%, SRD 95.0% |

A 35 → 10 funnel is in the healthy range the method expects. **No threshold was
loosened at any stage**, and none should be on this evidence.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ risk-to-base-low, descending.

| # | Symbol | RRR | Entry (lip) | Base low | Depth % | **Real risk %** | From lip % | Vol ratio | R² | Curv. | Rally % | Base bars | ₹cr/day | 60d high % | Tier |
|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| 1 | KTKBANK | 4.49 | 338.20 | 326.90 | 3.34 | **3.34** | 1.46 | 0.84 | 0.492 | 0.0185 | 10.24 | 12 | 56.78 | 100.0 | Marginal |
| 2 | ACMESOLAR | 3.73 | 411.50 | 394.95 | 4.02 | **4.02** | 0.19 | 0.75 | 0.774 | 0.0198 | 12.61 | 12 | 33.32 | 100.0 | Marginal |
| 3 | MARINE | 3.47 | 386.15 | 369.45 | 4.32 | **4.32** | 0.69 | 0.52 | 0.740 | 0.0230 | 15.28 | 20 | 23.32 | 97.8 | **Clean** |
| 4 | PARAS | 3.21 | 1542.10 | 1470.00 | 4.68 | **4.68** | 1.37 | 0.60 | 0.687 | 0.0216 | 23.35 | 12 | 101.22 | 97.3 ⚠ | Distrust |
| 5 | CYIENTDLM | 2.65 | 745.15 | 703.00 | 5.66 | **5.66** | 1.09 | 0.73 | 0.588 | 0.0294 | 11.34 | 20 | 22.12 | 97.5 ⚠ | Distrust |
| 6 | CHENNPETRO | 2.56 | 1465.70 | 1380.00 | 5.85 | **5.85** | 3.66 | 0.79 | 0.672 | 0.0360 | 13.15 | 25 | 133.97 | 98.4 | Distrust |
| 7 | HEG | 2.29 | 745.00 | 696.10 | 6.56 | **6.56** | 2.68 | 0.49 | 0.565 | 0.0288 | 11.07 | 29 | 49.31 | 99.5 | Marginal |
| 8 | BDL | 2.26 | 1401.70 | 1308.50 | 6.65 | **6.65** | 2.40 | 0.52 | 0.570 | 0.0372 | 11.00 | 30 | 65.83 | 97.4 ⚠ | **Clean** |
| 9 | MANIPALHOS | 2.26 | 749.20 | 699.35 | 6.65 | **6.65** | 1.09 | 0.69 | 0.743 | 0.0347 | 10.50 | 19 | 88.75 | 99.2 | Marginal |
| 10 | MSTCLTD | 2.14 | 741.90 | 690.00 | 7.00 | **7.00** | 1.52 | 0.82 | 0.824 | 0.0385 | 26.39 | 25 | 9.33 | 99.7 | Distrust |

⚠ = boundary pass on the 60-day-high filter (97.0% floor). **A boundary pass is not
the same evidence as a margin pass.**

**RRR ranks the geometry, not the odds.** It states what a trade pays if it works and
is silent on how often it works — a 4.49 RRR at a 20% hit rate is worse than 2.26 at
50%. The ordering is not a preference ranking and the top name is not the most likely
to succeed.

## 4. Tiers from the visual pass

Every panel in `hits.png` was opened and examined. Panel positions are given as
row/column in the 3-wide grid.

### Clean structural match (2)

**MARINE** — panel R1C3. The cleanest structure in the batch. A sustained multi-week
advance from ~276 to 386 with no single dominant candle (max bar share 0.31), then an
orderly shallow pause at the high. The fast EMAs run under the base the whole way and
rise through it, and volume dries to 0.52 of its rally average. Nothing here needs an
excuse.

**BDL** — panel R3C2. A genuine saucer inside the base window: down to 1308 around
the middle of the shaded zone, then a clean curl back to 1368. Lowest gap dependence
in the batch (max bar share 0.22) and a good volume dry-up at 0.52. Two caveats that
keep it honest — the 1425 lip was set by a single spike candle, and the upward curl is
only a handful of bars old. Note it is also a 97.4% boundary pass on the 60d-high filter.

### Marginal (4)

**KTKBANK** — panel R1C1. Trend and liquidity are fine, but the shaded zone is 12 bars
of tight drift under the high, not a rounded base. R² 0.492 is the weakest in the batch,
barely over the 0.45 floor. Its 3.34% depth is exactly why it tops the RRR ranking —
that is an artifact of a shallow shelf, not evidence of a better setup. The high itself
was made on a long red rejection candle.

**HEG** — panel R3C1. The base does round — a dip to ~697 mid-window curling up to 725 —
and the EMAs sit under it correctly. What holds it back is the lip: 745 was printed by a
single spike candle that was immediately sold. Entry at that level means buying directly
into one bar's worth of trapped supply.

**MANIPALHOS** — panel R3C3. The most orderly uptrend on the page, and that is the
problem. The base window swallows part of the final rally leg, so the quoted `base_low`
of 699.35 is a point on the advance rather than a pullback low. The actual pullback low
is nearer 715 (~4.5%). R² 0.743 is fitting a rise-dip-rise, not a base — the structural
risk shown is overstated and the structure itself is thinner than the label suggests.

**ACMESOLAR** — panel R1C2. Genuinely at a 60-day high, and the move cleared the 380–391
supply shelf on the left rather than stalling under it. But the advance into it is
near-vertical off the bottom of a 60-bar range, and the shaded zone is 12 bars of chop
at the top. This is a momentum pause, not a cup — a different setup with different odds.
Max bar share 0.40 is close to the 0.50 cut.

### Distrust despite passing every filter (4)

**MSTCLTD** — panel R4C1. The highest R² in the batch at 0.824, and precisely the failure
mode this method warns about: a 50-bar decline into the 60-day low followed by a
near-vertical 30% recovery. The parabola is fitting the V, not a base — high fit quality
here is a symptom, not a recommendation. Thinnest name to clear the turnover floor at
₹9.33cr, and the weakest volume dry-up at 0.82.

**CHENNPETRO** — panel R2C3. A real drawdown from 1350 to 1230, a violent V-recovery to
1450, a drop to 1310, another push to 1490, now back at 1412. The shaded zone is a wide
band of large-range candles swinging 5% — churn, not rounding. It sits 3.66% below its
lip, the furthest of any name here, so the entry is not even close.

**CYIENTDLM** — panel R2C2. The base window is a W of sharp drops and bounces under a
failed high, not a rounding. Price fell from 755 to 703, bounced, fell again, and is
oscillating around flattening EMAs. R² 0.588 and max bar share 0.43 both sit near their
cuts, and it is a boundary pass on the 60-day-high filter at 97.5%. Three marginal
readings pointing the same direction.

**PARAS** — panel R2C1. The rally leg is real and sustained. The base is not. The 1580
high was a spike rejected on the same bar, price fell ~7% to 1470, and the last 12 bars
are chop underneath it. Entry at 1542 sits directly under that rejected spike. Also a
boundary pass on the 60-day-high filter at 97.3%.

## 5. Stop-inside-base check

**All 10 of 10 names put a 3% stop inside the base.** Not one qualifying base is shallow
enough for a fixed 3% stop to sit below it.

| Symbol | Entry (lip) | 3% stop | Base low | Clearance of 3% stop over base low | Real structural risk |
|---|--:|--:|--:|--:|--:|
| KTKBANK | 338.20 | 328.05 | 326.90 | +0.34% (₹1.15) — one ordinary hourly candle | **3.34%** |
| ACMESOLAR | 411.50 | 399.16 | 394.95 | +1.02% | **4.02%** |
| MARINE | 386.15 | 374.57 | 369.45 | +1.32% | **4.32%** |
| PARAS | 1542.10 | 1495.84 | 1470.00 | +1.68% | **4.68%** |
| CYIENTDLM | 745.15 | 722.80 | 703.00 | +2.66% | **5.66%** |
| CHENNPETRO | 1465.70 | 1421.73 | 1380.00 | +2.85% | **5.85%** |
| HEG | 745.00 | 722.65 | 696.10 | +3.56% | **6.56%** |
| BDL | 1401.70 | 1359.65 | 1308.50 | +3.65% | **6.65%** |
| MANIPALHOS | 749.20 | 726.72 | 699.35 | +3.65% | **6.65%** |
| MSTCLTD | 741.90 | 719.64 | 690.00 | +4.00% | **7.00%** |

A stop placed mid-base is taken out by ordinary chop **without the pattern having
failed**. Honoring the structure on BDL means 6.65% risk, not 3% — which roughly halves
the position size a 3% assumption would have suggested, and changes the reward side of
the calculation with it. The *real structural risk* column is the number to size from;
the *3% stop* column is here only to show that it does not work.

Even the shallowest name, KTKBANK, gives a 3% stop just 0.34% of clearance — well inside
the noise of a single hourly bar on a ₹333 stock.

## 6. Honesty notes

- **These are candidates matching a geometry, not recommendations.** The screener finds a
  shape. It has no view on the business, the news flow, or the tape tomorrow. Entry,
  sizing, and whether to trade at all are the reader's calls.
- **Coverage was 2,108 of 2,296 (91.8%).** 188 names were never examined. Do not read
  this as a full-universe scan.
- **No threshold was loosened.** The detector and context filters ran at their standard
  settings, and nothing here suggests any of them needs tuning — the 35 → 10 funnel is
  squarely in the expected range.
- **Four names are distrusted despite passing every numeric filter** (MSTCLTD,
  CHENNPETRO, CYIENTDLM, PARAS). Disagreeing with the numbers is the purpose of the
  visual pass, and MSTCLTD — the best fit in the batch by R² — is the clearest example
  of why fit quality alone cannot be trusted.
- **Three names are boundary passes** on the 60-day-high filter (PARAS 97.3%,
  CYIENTDLM 97.5%, BDL 97.4% against a 97.0% floor).
- **Regime matters and is not measured here.** Bases near highs resolve upward far more
  often in a trending index than a choppy one. The presence of a pattern today is a
  different question from whether it is worth trading today, and only a backtest split
  by index trend state answers the second.
- **Prices are matplotlib renderings of Yahoo data.** EMA seeding and session handling
  differ from TradingView and Kite. Treat the panels as shape verification and confirm
  every level on your own platform before acting.
