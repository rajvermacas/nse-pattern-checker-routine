# NSE hourly screen — rally + rounded base near highs

**Executed at:** 2026-09-04 **17:04 IST** (run wall-clock start; data snapshot completed 17:10 IST)
**Latest data bar:** **2026-09-04 15:15:00 IST** — `session_date` 2026-09-04, `session_age_days` **0**.
This is today's session. Market was closed at run time, so the 15:15 stub is a genuine close and was kept.

**Charts (all 12 panels, tiered):** https://claude.ai/code/artifact/eef7c503-4f94-46b9-8414-5df90f41c5b4

> **These are candidates matching a geometry, not recommendations.** Entry, sizing and whether to
> trade at all are your calls. No threshold was loosened for this run — the parameters are the
> repository defaults.

---

## 1. Coverage

| | |
|---|---|
| Universe | **EQ**, the full NSE rolling-settlement list (the skill's default — not a narrowed index) |
| Symbols in universe | 2,288 (NSE `EQUITY_L.csv`: EQ 2,288 / BE 254 / BZ 28) |
| Symbols with usable data | **2,248 — 98.3%** |
| Missing | 40, after two gap-fill rounds recovered 32 of an initial 72 (recent listings without 60d of hourly history, plus symbols that don't map to `SYMBOL.NS` on Yahoo). Examples: ALFREDHE, ANSALBU, APOORVA, ARYAMAN, ASSAMENT, ASTAR, AUGMONT, CRAVATEX, ESDS, GAJA |
| Interval / history | 1h / 60d |
| Last closed bar | 2026-09-04 15:15:00 |
| Symbols carrying that bar | 2,164 / 2,248 = **96.3%** (above the 95% warning floor, so no staleness warning was raised) |

**Per-hit staleness: none.** All 12 survivors have `bars_behind_universe = 0` and `last_ts = 2026-09-04 15:15:00`. Every level quoted below is priced at the same bar.

This is a 98% scan, not a complete one. Coverage came in better than the ~92% the skill documents as typical.

## 2. Funnel

```
2,288  EQ symbols from NSE
2,248  with usable 60d hourly data          (−40, fetch coverage)
   39  raw detector hits                    (−2,209, the geometry gates)
   12  after context filters                (−27)
```

**What the detector cut** — the gate stack is EMA stack → EMA rising → base depth ≤10% → curvature ≥0.015 → R² ≥0.45 → |vertex| ≤0.65 → rally ≥10% → at-top → distance from lip ≤4% → volume ratio ≤0.85. As usual the EMA-stack requirement does most of the work, which is correct: the setup is defined as a pause inside an uptrend.

**What the context filters cut (27 names).** Reasons overlap, so these sum to more than 27:

| Filter | Cut | What it caught |
|---|---|---|
| Illiquid (< ₹5cr/day turnover) | 19 names | Pretty geometry, unfillable entry. Worst offenders: SWARNSAR ₹0.0cr, HBSL ₹0.01cr, AKG ₹0.01cr, BVCL ₹0.03cr, DRCSYSTEMS ₹0.03cr |
| Not at high (base high < 97% of the 60d high) | 14 names | Downtrend bounces reading as "rally + base near the *window* high": RPTECH 88.2%, GANESHCP 84.3%, AKG 83.8%, SPAL 89.4%, RELIGARE 92.3% |
| Gap-driven (one bar > 50% of the rally leg) | 13 names | Gap-and-base, a different setup with different odds |

Three liquid, at-the-high names were cut **purely** for being gap-driven — **MEDANTA** (0.65), **IDEA** (0.69) and **GRAPHITE** (0.83). If a gap-and-go is a setup you trade, those are the three to look at separately; they are excluded here by design, not by weakness.

39 raw → 12 clean is a healthy funnel. Nothing about it suggests a mis-calibrated threshold.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ risk-to-base-low. **This ranks the geometry, not the odds** — it says what the trade pays if it works and is silent on how often it does. It is not a buy order.

| # | Symbol | Entry (lip) | Close | From lip | Base low | Depth % | RRR | Base bars | Curv. | R² | Vol ratio | % of 60d high | Max bar share | ₹cr/day |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | RISHABH | 750.00 | 738.45 | 1.54% | 716.10 | 4.52 | 3.32 | 13 (≈1.9 sess) | 0.0158 | 0.659 | 0.52 | 99.6 | 0.36 | 11.0 |
| 2 | KENNAMET | 4734.70 | 4688.50 | 0.98% | 4511.10 | 4.72 | 3.18 | 20 (≈2.9) | 0.0320 | 0.749 | 0.44 | **97.5** | 0.35 | 16.0 |
| 3 | SSWL | 366.60 | 360.90 | 1.55% | 348.75 | 4.87 | 3.08 | 13 (≈1.9) | 0.0206 | **0.498** | 0.22 | 100.0 | 0.22 | 11.1 |
| 4 | CRAFTSMAN | 11539.00 | 11398.00 | 1.22% | 10928.00 | 5.30 | 2.83 | 27 (≈3.9) | 0.0340 | 0.722 | 0.66 | 100.0 | **0.45** | 24.4 |
| 5 | YATHARTH | 1010.55 | 991.10 | 1.92% | 955.20 | 5.48 | 2.74 | 30 (≈4.4) | 0.0307 | 0.705 | 0.32 | 98.6 | 0.36 | 17.7 |
| 6 | QPOWER | 1499.90 | 1495.30 | 0.31% | 1398.60 | 6.75 | 2.22 | 23 (≈3.3) | 0.0475 | 0.609 | 0.49 | 99.8 | 0.35 | 17.1 |
| 7 | TIMEX | 687.80 | 669.85 | 2.61% | 639.25 | 7.06 | 2.12 | 29 (≈4.2) | 0.0384 | 0.783 | 0.58 | 100.0 | 0.22 | 11.7 |
| 8 | FCL | 52.10 | 51.70 | 0.77% | 48.01 | 7.85 | 1.91 | 30 (≈4.4) | 0.0530 | 0.771 | **0.84** | 99.8 | **0.48** | 36.5 |
| 9 | RATNAVEER | 308.00 | 308.00 | **0.00%** | 282.10 | 8.41 | 1.78 | 23 (≈3.3) | 0.0467 | 0.838 | 0.43 | 97.8 | 0.35 | **123.2** |
| 10 | IOLCP | 204.98 | 199.50 | 2.67% | 186.10 | 9.21 | 1.63 | 30 (≈4.4) | 0.0324 | **0.529** | 0.53 | 100.0 | 0.40 | 35.4 |
| 11 | OMAXE | 138.73 | 136.00 | 1.97% | 125.73 | 9.37 | 1.60 | 15 (≈2.2) | 0.0415 | 0.721 | 0.25 | 100.0 | 0.27 | 27.0 |
| 12 | SETL | 410.70 | 408.05 | 0.65% | 370.00 | 9.91 | 1.51 | 26 (≈3.8) | 0.0603 | **0.899** | 0.55 | 100.0 | 0.23 | 18.4 |

`base_low_is_wick` is **false for all 12** — no ranking here is distorted by a single outlier bar, and the closing-basis floors sit within 0.05–0.99% of the traded lows. Sizing below assumes the traded low.

**One boundary pass:** KENNAMET cleared the at-the-high filter at 97.5% against a 97.0% floor. A boundary pass is not a margin pass — its base high sits below a real 28 Aug spike to ~₹4,850, which is overhead supply directly above the proposed entry.

## 4. Tiers from the visual pass

I read all twelve panels. The numbers and my reading disagree in several places, and where they do, the reading is the point of this section.

### Clean structural match (4)

- **TIMEX** — the best structure in the batch and it is not the top-ranked name. A genuine multi-bar staircase from ₹525 to ₹688 (max bar share 0.22, the joint-lowest), then a 29-bar base that actually rounds: down to ₹639, a curved bottom, recovery to ₹670. The fast EMA runs under the base, flattens and turns up through it. Cost: a 7.06% base, so the structure is expensive to honor.
- **KENNAMET** — clean staircase rally ₹3,600 → ₹4,750, then an orderly, shallow (4.72%) 20-bar consolidation with the EMAs supporting. *Caveat:* the boundary pass above. The 28 Aug wick to ~₹4,850 is overhead supply the entry has to clear.
- **CRAFTSMAN** — a 27-bar base that genuinely rounds, sitting at the 60-day high, EMAs beneath and rising. *Caveat:* max bar share 0.45 against a 0.50 cut — nearly half the rally leg is one 28 Aug candle. It passed the gap filter, but only just.
- **RATNAVEER** — cleanest rally leg here (₹218 → ₹308 as a true staircase), a 23-bar base that rounds, and by far the most liquid name at ₹123cr/day. *Two caveats:* it closed **exactly at the lip** (0.00% away), so there is no cushion — the entry trigger is now, on a bar that has just arrived; and the 8.41% base makes it the widest structural stop in the top half.

### Marginal (4)

- **YATHARTH** — the 30-bar base is a reasonable length, but the rally is four very steep sessions off a three-week flat shelf, and the base is drifting sideways-down rather than closing its round. It sits 1.92% under the lip with the right side of the curve unfinished.
- **FCL** — the base is a long *flat shelf* at ₹48–49 with a late pop, not a saucer. Two boundary passes compound it: volume ratio 0.84 against a 0.85 cut (so volume never actually dried up — the thing the pattern is supposed to show) and max bar share 0.48 against 0.50.
- **RISHABH** — **ranked #1 and I do not trust the ranking.** The "base" is 13 bars, about 1.9 sessions: that is a two-day pullback after a spike, not a base. The rally leg is a choppy meander from ₹650 with repeated rejections around ₹720–730, not a trend. Curvature 0.0158 is barely over the 0.015 floor — the shallowest, weakest curve in the batch. It tops the table only because a shallow base mechanically produces a high inverse-depth RRR.
- **QPOWER** — two problems the filters didn't catch. There is a visible discontinuity in the 28 Aug leg (it passed max-bar-share at 0.35, but the panel shows a jump), and the right half of the "base" is a sharp dip to ₹1,399 on 03 Sep followed by a vertical snap back to ₹1,495 — a V, not a round. It is 0.31% from the lip, so the entry would trigger on that snapback.

### Distrust despite passing every filter (4)

- **SETL** — the R² trap the skill exists to catch: **the best parabola fit in the batch (0.899) on its deepest base (9.91%) and its worst RRR (1.51)**. The panel shows a 30% vertical off a three-week flat shelf, then one-and-a-half sessions down and one session straight back up. The two halves have very different slopes. A fit statistic cannot tell that from a saucer; looking can.
- **SSWL** — the "rally" is a *recovery from a decline*: ₹310 flat, down to ₹290 by 24 Aug, then a near-vertical rip to ₹366 over three sessions. The 13-bar "base" is a two-day pause at the top of that vertical, and R² 0.498 is the lowest here. Price is extended well above both EMAs. The at-the-high filter passed it because the decline stayed inside the window.
- **IOLCP** — a checkmark, not a saucer: a sharp 9.2% drop to ₹186 and an equally sharp snap back to ₹200. R² 0.529 and vertex at −0.393 both hint at it; the panel confirms it.
- **OMAXE** — a 38% run in roughly four sessions, then a 15-bar (≈2.2 session) 9.4% swing labelled a base. That is a violent pullback inside a parabolic move. A 9.4% "shallow consolidation" is a contradiction, and the name is far extended above its EMAs.

**Note on the ranking as a whole:** the top three by RRR (RISHABH, KENNAMET, SSWL) contain one name I distrust outright and one I call marginal, while the best-looking structure (TIMEX) ranks 7th. RRR is inverse base depth, so it systematically rewards short, shallow "bases" — including two-day pullbacks that have not earned the name. Read the tiers before the table.

## 5. Stop-inside-base check

**All 12 have a 3% stop inside the base.** Not some — all of them.

| Symbol | Entry (lip) | 3% stop | Base low (real stop) | Real risk | Verdict |
|---|---|---|---|---|---|
| RISHABH | 750.00 | 727.50 | 716.10 | **4.52%** | 3% lands mid-base — incompatible |
| KENNAMET | 4734.70 | 4592.66 | 4511.10 | **4.72%** | incompatible |
| SSWL | 366.60 | 355.60 | 348.75 | **4.87%** | incompatible |
| CRAFTSMAN | 11539.00 | 11192.83 | 10928.00 | **5.30%** | incompatible |
| YATHARTH | 1010.55 | 980.23 | 955.20 | **5.48%** | incompatible |
| QPOWER | 1499.90 | 1454.90 | 1398.60 | **6.75%** | incompatible — 3% stop sits less than halfway down |
| TIMEX | 687.80 | 667.17 | 639.25 | **7.06%** | incompatible |
| FCL | 52.10 | 50.54 | 48.01 | **7.85%** | incompatible |
| RATNAVEER | 308.00 | 298.76 | 282.10 | **8.41%** | incompatible |
| IOLCP | 204.98 | 198.83 | 186.10 | **9.21%** | incompatible — 3% is a third of the way down |
| OMAXE | 138.73 | 134.57 | 125.73 | **9.37%** | incompatible |
| SETL | 410.70 | 398.38 | 370.00 | **9.91%** | incompatible — 3% is under a third of the base |

A 3% stop on any of these sits mid-base and gets taken out by ordinary chop **without the pattern having failed at all**. Honoring the structure on TIMEX means 7.06% risk, which is roughly 2.3× the position-size assumption a 3% stop implies. On SETL it is 9.91% — 3.3×. If you size as though risk is 3%, you are running two to three times the intended exposure on every name here.

The closing-basis floors (`base_low_close`) are 4.36% / 4.28% / 4.53% / 4.97% / 5.10% / 6.46% / 6.82% / 7.49% / 8.07% / 8.48% / 8.25% / 9.54% in table order — none differs enough from the traded low to change the picture.

## 6. Regime

Bases near highs resolve upward far more often in a trending index than a choppy one. The same screener over the same universe has a materially different hit rate in each. Twelve names matching a geometry today says nothing about whether the geometry is paying today; only a backtest split by index trend state answers that.

---

*Charts are matplotlib renderings of yfinance hourly data. EMA seeding and session handling differ from TradingView and Kite — treat the panels as shape verification and confirm every price on your own platform before acting.*
