# NSE hourly screen — rally + rounded base near highs

| | |
|---|---|
| **Executed at** | **2026-09-10 17:04 IST** (`run_ts_ist`) |
| **Latest data bar** | **2026-09-10 15:15 IST** — the 2026-09-10 session |
| Session age | 0 days. This is the current session, market closed at run time. |
| Data snapshot | 2026-09-10 17:10 IST |
| Universe | EQ (skill default, full series — not narrowed) |
| Interval | 1h, 60-day window |

**Charts:** https://claude.ai/code/artifact/398f9c99-1109-42be-91fb-dd600e3e8f68

Everything below is a list of **candidates matching a geometry, not recommendations.**
Entry, sizing, and whether to trade at all are your calls. The ranking orders the
shape's reward-to-risk; it says nothing about how often the shape works.

---

## 1. Coverage

| | |
|---|---|
| Symbols in EQ universe | 2,294 |
| Symbols with usable 60d hourly data | **2,267 (98%)** |
| Symbols carrying the 15:15 bar | 2,174 (95.9%) |
| Last closed bar | 2026-09-10 15:15:00 |

The market was closed at run time, so the 15:15 stub bar is a genuine close and was kept.

27 symbols returned no usable data — recent listings without 60 days of history, plus
a handful of NSE symbols that do not map cleanly to `SYMBOL.NS` on Yahoo. This is not
a full-universe scan; it is 98% of it.

`pct_at_last_bar` is 95.9, so the universe's last bar is not the price time for every
symbol. **All 18 clean hits have `bars_behind_universe` = 0**, so every price quoted
below is at 2026-09-10 15:15. No hit needed a per-symbol timestamp caveat.

## 2. Funnel

| Stage | Count | What it removed |
|---|---|---|
| Scanned | 2,267 | — |
| Raw detector hits | 40 | EMA stack, EMA rising, base depth ≤10%, curvature ≥0.015, R² ≥0.45, vertex inside ±0.65, rally ≥10%, at-top, lip ≤4%, volume dry-up ≤0.85 |
| Clean hits | **18** | 22 removed by the three context filters |

The 22 rejections, by filter (names fail more than one):

| Filter | Cut | Names |
|---|---|---|
| Illiquid (< ₹5cr/day turnover) | 14 | BEEKAY 0.03, GTPL 0.12, ORIENTPPR 0.24, ONEGLOBAL 0.40, SATIA 0.51, PROZONER 0.65, RANEHOLDIN 0.94, KAPSTON 1.64, RML 1.67, IRISDOREME 2.31, CRIZAC 2.60, AGL 2.73, MAXESTATES 4.93, EMSLIMITED 4.98 |
| Not at a real high (< 97% of 60d high) | 12 | AGL 73.1%, BAJAJCON 76.9%, PWL 81.9%, CRIZAC 81.4%, SFL 84.3%, EMSLIMITED 85.5%, GTPL 88.1%, RANEHOLDIN 91.8%, RELIGARE 93.4%, ONEGLOBAL 94.8%, KISSHT 96.5%, ORIENTPPR 96.8% |
| Gap-driven rally (one bar > 50% of the move) | 8 | INOXINDIA 0.52, WELCORP 0.52, SFL 0.51, KAPSTON 0.53, IOLCP 0.55, AGL 0.60, CRIZAC 0.85, EMSLIMITED 1.24 |

Liquidity did the most work today. The not-at-high filter caught the case it exists
for: BAJAJCON at 76.9% of its 60-day high shows a "rally into a base near the window
high" that is really a bounce inside a downtrend.

18 clean out of 2,267 is a normal funnel — slightly wide of the 10–15 the skill
expects, not wide enough to suggest the thresholds have drifted into describing
"went up and paused". **No threshold was loosened or changed for this run.**

## 3. Ranked table

Ranked by `rrr_structural` (15% target ÷ risk to base low), best first. This is the
panel order in the chart.

| # | Symbol | Close | Entry (lip) | Base low | Depth % | Risk to base low % | Dist from lip % | Rally % | Base bars | R² | Vol ratio | Turnover ₹cr | % of 60d high | RRR |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | GMMPFAUDLR | 1319.20 | 1325.30 | 1291.70 | 2.54 | 2.54 | 0.46 | 29.65 | 12 | 0.811 | 0.81 | 12.3 | 98.1 | 5.91 |
| 2 | WELENT | 797.95 | 802.00 | 776.25 | 3.21 | 3.21 | 0.50 | 23.83 | 19 | 0.731 | 0.22 | 19.0 | 97.2 | 4.67 |
| 3 | GCSL | 612.50 | 616.90 | 594.30 | 3.66 | 3.66 | 0.71 | 13.50 | 25 | 0.827 | 0.65 | 20.2 | 100.0 | 4.10 |
| 4 | NEPHROPLUS | 749.20 | 757.40 | 726.00 | 4.15 | 4.15 | 1.08 | 10.09 | 15 | 0.851 | 0.66 | 7.1 | 100.0 | 3.61 |
| 5 | CAPLIPOINT | 2795.40 | 2845.90 | 2707.90 | 4.85 | 4.85 | 1.77 | 14.23 | 22 | 0.713 | 0.22 | 16.5 | 99.0 | 3.09 |
| 6 | AEROFLEX | 567.00 | 576.30 | 548.10 | 4.89 | 4.89 | 1.61 | 11.52 | 15 | 0.676 | 0.54 | 38.8 | 98.7 | 3.07 |
| 7 | WELSPUNLIV | 210.50 | 215.45 | 204.54 | 5.06 | 5.06 | 2.30 | 13.88 | 27 | 0.456 | 0.84 | 47.1 | 99.7 | 2.96 |
| 8 | STAR | 1217.00 | 1222.30 | 1160.00 | 5.10 | 5.10 | 0.43 | 18.93 | 12 | 0.738 | 0.47 | 18.4 | 100.0 | 2.94 |
| 9 | KSHINTL | 1175.00 | 1196.95 | 1128.50 | 5.72 | 5.72 | 1.83 | 27.50 | 15 | 0.468 | 0.63 | 13.7 | 100.0 | 2.62 |
| 10 | CGCL | 273.95 | 285.20 | 268.15 | 5.98 | 5.98 | 3.94 | 17.32 | 27 | 0.688 | 0.50 | 78.2 | 99.4 | 2.51 |
| 11 | HERITGFOOD | 398.05 | 403.50 | 376.30 | 6.74 | 6.74 | 1.35 | 10.28 | 23 | 0.761 | 0.49 | 7.2 | 100.0 | 2.23 |
| 12 | WSTCSTPAPR | 714.00 | 714.80 | 664.40 | 7.05 | 7.05 | 0.11 | 13.27 | 21 | 0.731 | 0.72 | 8.9 | 100.0 | 2.13 |
| 13 | MAHSEAMLES | 718.00 | 724.00 | 668.70 | 7.64 | 7.64 | 0.83 | 11.38 | 25 | 0.839 | 0.72 | 12.4 | 100.0 | 1.96 |
| 14 | MILKYMIST | 278.83 | 284.47 | 262.18 | 7.84 | 7.84 | 1.98 | 37.95 | 20 | 0.789 | 0.32 | 199.1 | 98.8 | 1.91 |
| 15 | PAISALO | 82.75 | 83.50 | 76.78 | 8.05 | 8.05 | 0.90 | 19.93 | 24 | 0.872 | 0.83 | 34.1 | 100.0 | 1.86 |
| 16 | KLBRENG-B | 477.40 | 490.40 | 450.25 | 8.19 | 8.19 | 2.65 | 20.75 | 29 | 0.632 | 0.67 | 8.1 | 100.0 | 1.83 |
| 17 | INDOMIM | 1002.00 | 1028.50 | 941.75 | 8.43 | 8.43 | 2.58 | 16.58 | 29 | 0.657 | 0.61 | 103.9 | 100.0 | 1.78 |
| 18 | SUNSHINE | 511.00 | 522.00 | 472.25 | 9.53 | 9.53 | 2.11 | 31.25 | 26 | 0.681 | 0.51 | 51.3 | 100.0 | 1.57 |

Two boundary passes worth flagging, because a boundary pass is weaker evidence than
a margin pass:

- **WELENT** sits at 97.2% of its 60-day high against a 97.0% floor.
- **WELSPUNLIV** fits at R² 0.456 against a 0.45 floor, and **KSHINTL** at 0.468.

## 4. Tiers from the visual pass

I opened every panel. The parabola fit cannot separate a saucer from a V — a sharp
reversal fits it better than a genuine rounded base — so the two highest R² values in
this batch (PAISALO 0.872, NEPHROPLUS 0.851) both belong to names I do not trust.

### Clean structural match — 4

- **GCSL** (#3) — the best of the batch. An orderly staircase from 500 to 617 over three
  weeks with clean higher lows, then 3.6 sessions of tight consolidation between 595
  and 617, sitting right under the lip. Both EMAs run under the base and rise through
  it. At 3.66% depth this is also one of the few names where the stop is not absurd.
- **MAHSEAMLES** (#13) — the only genuine saucer here. A multi-week uptrend from 615,
  then a real U: down from 718, a flat rounded bottom near 670, and a rising right
  side back to 720 on the final bars. The fast EMA dipped, flattened, and turned up
  through the base. The 7.64% depth is the cost.
- **WELENT** (#2) — sustained rally from 575 to 820 with the leg partly off the left
  edge of the panel, then 2.8 sessions of tight range just under 800. EMAs under and
  rising. Downgraded slightly by the 60d-high boundary pass noted above.
- **MILKYMIST** (#14) — clear higher lows from 180 to 284 over three weeks, then a
  rounded pullback to 262 that is recovering toward the lip. The shape is real. It is
  also up 38% in three weeks, which is extended, and the base is 7.84% deep.

### Marginal — 7

- **GMMPFAUDLR** (#1) — the best reward-to-risk number in the batch and the shakiest
  claim to the pattern. The base is 12 bars, 1.7 sessions, and it follows a near-vertical
  run from 1150 to 1350. That is a high-tight flag, not a rounded base. The trend is
  genuine; the base has not had time to form.
- **AEROFLEX** (#6) — a real sustained staircase from 478 to 585, but the base is a
  two-day dip and the lip is set by a single spike candle at 585, so the breakout level
  is one bar's worth of evidence.
- **WSTCSTPAPR** (#12) — good trend, but the base is a V-dip (690 to 664 to 714), not a
  saucer. It also closed 0.11% from the lip, so there is no entry buffer left.
- **KLBRENG-B** (#16) — a real three-week uptrend from 355 to 490. The base rounds, but
  it reads more sawtooth than saucer, and 8.19% is a large structural stop.
- **CGCL** (#10) — the base is a flat shelf around 270 to 275 sitting 3.94% *below* the
  lip, the furthest from the lip in the batch. The fast EMA is flat and price is
  oscillating across it rather than being lifted through it. The 287 lip is one spike bar.
- **STAR** (#8) — a high-tight flag after a roughly 1.5-session vertical move from 1050
  to 1200, not a base. It is also the one name where `base_low_is_wick` is true: the
  wick low is 1160 but the closing-basis floor is 1186.70, a 2.12% gap. See section 5.
- **WELSPUNLIV** (#7) — R² 0.456 against a 0.45 floor, and the panel shows why. The
  "base" is jagged sawtooth chop between 204 and 215 with a spike back to the lip,
  not a structure.

### Distrust despite passing every filter — 7

- **PAISALO** (#15) — best fit in the batch (R² 0.872) and the worst shape. The left
  half of the panel is a downtrend from 70 to 65, then a vertical V-reversal to 83.5.
  The vertex sits at −0.565, near the edge of the ±0.65 window, meaning the turn is at
  the far left of the base rather than centred. This is a snapback, not a cup.
- **NEPHROPLUS** (#4) — R² 0.851, the second-best fit, on a V. The left half is
  trendless chop between 680 and 710, the "rally" is two days of vertical move, and
  the base is a dip to 726 followed by an immediate snap back to 750.
- **KSHINTL** (#9) — a clear downtrend from 1015 to 935 through 03 Sep, then a 27%
  near-vertical reversal in four days. The 15-bar "base" is chop at the top of that
  move. R² 0.468 is a boundary pass. Downtrend-bounce geometry, and it passes the
  60d-high test only because the snapback carried it to a new high.
- **INDOMIM** (#17) — same shape: a downtrend from 925 to 841, then a V-reversal. The
  rally leg is 19 bars, the shortest here. What the detector calls a 29-bar base is
  still making higher highs — it is an ongoing advance, not a consolidation.
- **HERITGFOOD** (#11) — the panel's left side is a decline from 392 to 351, so the
  10.28% "rally" is a recovery off that low. Overhead supply from the 26 Aug high sits
  right beneath current price, and the entire move above the base came on the single
  vertical last bar to 403.
- **CAPLIPOINT** (#5) — flat to declining until 01 Sep, then two days of vertical move
  to 2860. The base is a deep V-dip to 2708, and the fast EMA rolled over and ran
  through it rather than under it. Breakout-and-pullback, not rally-and-cup.
- **SUNSHINE** (#18) — the "base" is a rising staircase from 445 to 500 with a vertical
  spike to 521 on the last bar. Deepest base in the batch at 9.53%, worst RRR, and the
  data starts 25 Aug rather than 20 Aug, so it has a shorter history than everything
  else here and is likely a recent listing.

## 5. Stop-inside-base check

A fixed 3% stop off the lip lands **inside the base** for 17 of the 18 names. The base
low is the only stop the structure supports, so honouring the pattern means taking the
risk in the last column, which for most of this list is roughly double the 3% assumption
and roughly halves position size.

| Symbol | Entry (lip) | 3% stop | Base low (real stop) | 3% stop inside base? | Real risk % |
|---|---:|---:|---:|:---:|---:|
| GMMPFAUDLR | 1325.30 | 1285.54 | 1291.70 | **No** | 2.54 |
| WELENT | 802.00 | 777.94 | 776.25 | Yes | 3.21 |
| GCSL | 616.90 | 598.39 | 594.30 | Yes | 3.66 |
| NEPHROPLUS | 757.40 | 734.68 | 726.00 | Yes | 4.15 |
| CAPLIPOINT | 2845.90 | 2760.52 | 2707.90 | Yes | 4.85 |
| AEROFLEX | 576.30 | 559.01 | 548.10 | Yes | 4.89 |
| WELSPUNLIV | 215.45 | 208.99 | 204.54 | Yes | 5.06 |
| STAR | 1222.30 | 1185.63 | 1160.00 | Yes | 5.10 |
| KSHINTL | 1196.95 | 1161.04 | 1128.50 | Yes | 5.72 |
| CGCL | 285.20 | 276.64 | 268.15 | Yes | 5.98 |
| HERITGFOOD | 403.50 | 391.39 | 376.30 | Yes | 6.74 |
| WSTCSTPAPR | 714.80 | 693.36 | 664.40 | Yes | 7.05 |
| MAHSEAMLES | 724.00 | 702.28 | 668.70 | Yes | 7.64 |
| MILKYMIST | 284.47 | 275.94 | 262.18 | Yes | 7.84 |
| PAISALO | 83.50 | 81.00 | 76.78 | Yes | 8.05 |
| KLBRENG-B | 490.40 | 475.69 | 450.25 | Yes | 8.19 |
| INDOMIM | 1028.50 | 997.64 | 941.75 | Yes | 8.43 |
| SUNSHINE | 522.00 | 506.34 | 472.25 | Yes | 9.53 |

**GMMPFAUDLR is the only name where a 3% stop clears the base**, at 2.54% depth — and
that shallowness is exactly why its 12-bar base is too young to trust. The reward-to-risk
ranking and the structural quality point in opposite directions at the top of this table.

For every other name, a 3% stop sits mid-cup and gets taken out by ordinary chop
without the pattern having failed at all. Do not size as if 3% were the risk.

**Wick-set base low — STAR only.** `base_low` 1160.00 is a single wick; the
closing-basis floor is 1186.70. The two readings differ by 2.12% of entry, so the
structural risk is either 5.10% (wick) or 2.91% (closing basis) depending on which you
honour. The table and the ranking use the wick, which is the conservative reading and a
real traded price. If you size off the closing basis instead, STAR's effective RRR is
better than its #8 position suggests. No other name in the batch has this ambiguity.

## 6. Regime

Bases near highs resolve upward far more often in a trending index than a choppy one.
The same screener on the same universe has a materially different hit rate in the two.
Whether this pattern is present today and whether it is worth trading today are
different questions, and only a backtest split by index trend state answers the second.

---

*Data: Yahoo Finance hourly OHLCV, fetched 2026-09-10 17:04–17:10 IST. Charts are
matplotlib renderings, not screenshots from any trading platform; EMA seeding and
session handling differ from TradingView and Kite. Confirm prices on your own platform
before acting.*
