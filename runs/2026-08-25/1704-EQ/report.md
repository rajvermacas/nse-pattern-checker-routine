# NSE hourly screen — rally + rounded base near highs

- **Executed at:** 2026-08-25 17:04 IST (`run_ts_ist`, run start; data snapshot completed 17:10 IST)
- **Latest data bar:** `2026-08-25 15:15:00` — the **2026-08-25** session, `session_age_days = 0`, i.e. today's close. Market was closed at run time, so the 15:15 stub is a genuine close and was kept.
- **Universe:** NSE EQ (full default universe), hourly (`1h`), 60 days
- **Chart (all nine panels, full size):** https://claude.ai/code/artifact/042190f3-cb3e-4969-b508-88af1ffdceae

> These are **candidates matching a geometry, not recommendations.** The screen finds a shape;
> it says nothing about whether the shape resolves. Entry, sizing and whether to trade at all
> are your calls. Prices are yfinance hourly bars rendered in matplotlib — EMA seeding and
> session handling differ from TradingView/Kite, so confirm every level on your own platform.

---

## 1. Coverage

| | |
|---|---|
| Symbols in EQ universe (from NSE archives) | **2,296** |
| Symbols with usable hourly data | **2,108** |
| Coverage | **91.8%** (reported as 91% by the integer counter) |
| Symbols carrying the reported last bar `2026-08-25 15:15` | **2,008 / 2,108 (95.3%)** |
| Universe consensus last bar | `2026-08-25 15:15:00` (2,008 symbols) |

**188 symbols are missing.** The fetch logged 210 drops across its attempts, split
`no_data_returned = 23` / `too_few_bars = 187` — recent listings without 60 days of hourly history,
plus NSE symbols that don't map cleanly to `SYMBOL.NS` on Yahoo. Gap-fill round 1 recovered 22 of
them after waiting out the rate limiter; round 2 recovered zero, which is the signal that the
remaining 188 are genuinely absent from the feed rather than throttled. **This is not a
full-universe scan** — roughly one symbol in twelve was never looked at, and a qualifying setup
in that slice would not appear below.

All nine surviving hits carry `bars_behind_universe = 0`, so every level quoted below is priced
at the `2026-08-25 15:15` bar, not an earlier one.

## 2. Funnel

```
2,296 EQ symbols  →  2,108 with data  →  26 raw detector hits  →  9 clean
```

The detector's own gates (EMA stack, EMA rising, base depth ≤10%, curvature ≥0.015, R² ≥0.45,
vertex window, rally ≥10%, at-top, lip ≤4%, volume ≤0.85) took 2,108 down to 26.

The context filters removed 17 of those 26:

| Filter | What it cuts | Names removed (sole reason) | Total involving it |
|---|---|---|---|
| Turnover ≥ ₹5cr/day | pretty geometry, unfillable entry | JUNIPER (2.58cr), JAYSREETEA (0.37cr), RACLGEAR (3.02cr) | 12 |
| Base high ≥ 97% of 60d high | downtrend bounce reading as "base near the window high" | MARSONS (87.6%), AXISCADES (80.2%), WAKEFIT (92.3%) | 9 |
| Max single-bar share ≤ 0.5 of rally | gap-and-base ≠ rally-and-base | VINCOFE (0.52) | 9 |

Ten names failed on more than one count (e.g. DAICHI: 0.03cr turnover *and* one bar at 1.44× the
rally; SIGMA: illiquid, not at high, and gap-driven).

A 26 → 9 funnel is in the healthy band the skill describes (~40 raw → 10–15 clean). Nothing was
loosened to produce these nine; every threshold is at its default.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ base depth. **RRR ranks the geometry, not the odds** —
it says what the trade pays if it works and is silent on how often it does. The top name is not
the most likely to succeed.

| # | Symbol | Close | Entry (lip) | Base low | Depth / risk to base low | Dist. from lip | Rally | Base bars | Vol ratio | R² | Turnover ₹cr | RRR |
|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | HAPPSTMNDS | 445.95 | 452.25 | 432.75 | 4.31% | 1.39% | 13.1% | 15 | 0.42 | 0.691 | 27.6 | 3.48 |
| 2 | GLAXO | 2963.40 | 3023.40 | 2866.30 | 5.20% | 1.98% | 17.4% | 27 | 0.49 | 0.727 | 14.3 | 2.88 |
| 3 | SGMART | 837.40 | 846.80 | 802.00 | 5.29% | 1.11% | 14.9% | 19 | 0.45 | 0.592 | 11.8 | 2.84 |
| 4 | JYOTHYLAB | 212.88 | 215.21 | 202.58 | 5.87% | 1.08% | 11.3% | 30 | 0.42 | 0.578 | 10.0 | 2.56 |
| 5 | THELEELA | 554.90 | 574.95 | 540.55 | 5.98% | 3.49% | 12.7% | 15 | 0.42 | 0.651 | 17.3 | 2.51 |
| 6 | TIMEX | 617.65 | 623.95 | 584.80 | 6.27% | 1.01% | 16.3% | 17 | 0.81 | 0.764 | 9.8 | 2.39 |
| 7 | TFCILTD | 137.50 | 137.94 | 128.18 | 7.08% | 0.32% | 17.2% | 21 | 0.64 | 0.784 | 86.8 | 2.12 |
| 8 | SHREEJISPG | 645.50 | 660.80 | 610.00 | 7.69% | 2.32% | 11.1% | 30 | 0.58 | 0.631 | 34.5 | 1.95 |
| 9 | MANIPALHOS | 764.80 | 768.50 | 699.35 | 9.00% | 0.48% | 10.5% | 26 | 0.80 | 0.804 | 88.9 | 1.67 |

**Boundary pass:** SHREEJISPG cleared the 60-day-high filter at exactly **97.0% vs a 97.0% floor**.
A boundary pass is not the same evidence as a margin pass, and the chart confirms the suspicion —
see §4.

## 4. Tiers from the visual pass

I opened `hits.png` and read all nine panels. The numbers and the pictures disagree in six of the
nine cases, which is the point of this step.

### Clean structural match — 2

**TFCILTD** (panel 7) — the only textbook cup in the batch. A 55-bar flat floor at 110–117, then a
sustained multi-bar rally to 137, then a 21-bar base that genuinely rounds: down to 130, curls, and
comes back to a new high on the last bar. Both EMAs run under the base and rise through it. Highest
turnover-to-geometry quality here (₹86.8cr/day). Caveat: at 0.32% from the lip the breakout is
effectively happening now, so there is no patient entry left.

**GLAXO** (panel 2) — a 50-bar floor at 2,600, a genuine multi-bar thrust to 3,040 (no single candle
above 32% of the move), then a 27-bar consolidation that drifts down to 2,900 and rounds back up.
The base is closer to a downward-sloping shelf than a true saucer, but the structure is honest and
the rally is real.

### Marginal — 5

**HAPPSTMNDS** (panel 1, top-ranked) — the "base" is a 15-bar (≈2 session) flag after a vertical
thrust to 452, not a rounded base. `max_bar_share` is 0.48 against a 0.5 gate: nearly half the
rally is one candle. It is a legitimate high-tight pullback; it is not the pattern this screen is
named for, and it is ranked first only because a shallow flag mechanically produces the best RRR.

**SGMART** (panel 3) — a clean staircase uptrend with EMAs correctly stacked underneath, but the
19-bar "base" is a pause in trend rather than a distinct structure, and R² 0.592 reflects that.
Good chart, thin pattern.

**THELEELA** (panel 5) — the rally leg is the best-looking part of the batch (sustained 500 → 575
over 30 bars). The base is a sharp 15-bar pullback that hasn't stabilised: the fast EMA has rolled
over and is flat-to-declining through it, and at 3.49% this is the furthest from its lip of the
nine. Too early.

**TIMEX** (panel 6) — a flat shelf, not a saucer, and the final hourly candle is already a vertical
push from 600 to 623. `vol_ratio` 0.81 means there was no volume dry-up in the base. Also note the
rally leg begins from a 10% drawdown (575 → 520), so a good part of it is recovery rather than
advance, even though it has now cleared to a new 60-day high.

**MANIPALHOS** (panel 9) — the highest R² in the batch (0.804), fitted to a smooth uptrend rather
than to a base. There is no consolidation of substance; the parabola is describing the trend line.
The quoted 9% "risk to base low" is a month of trend, not a pattern stop, which makes it the
weakest RRR here for the right reason.

### Distrust despite passing every filter — 2

**JYOTHYLAB** (panel 4, ranked 4th) — this is the false positive the skill warns about. The whole
"11.3% rally" is essentially one enormous candle at bar 64 (200 → 216); `max_bar_share` 0.48 slipped
under the 0.5 gate. The base that follows is a **V**: straight down to 203, straight back to 213.
A V fits a parabola better than a real base does, which is exactly why R² and curvature cannot
catch it. Do not treat the 215.21 lip as a breakout level — it is one candle's high.

**SHREEJISPG** (panel 8) — a bounce inside a decline, not a base at a high. The panel opens at 650,
spikes to **680**, then collapses ~14% to 585 before rallying back to 660. The 680 high is direct
overhead supply sitting just above the 660.80 entry, and this is precisely what the 60-day-high
filter exists to reject — it passed at exactly the 97.0% boundary. The base itself is choppy and
V-ish, with a 610 low mid-window, and the fast EMA is flat through it.

## 5. Risk reality check — the stop-inside-base problem

**All 9 of 9 have a 3% stop landing inside the base.** Not one of these is compatible with a
fixed-percentage stop.

| Symbol | Entry (lip) | 3% stop | Base low (structural stop) | Real risk | Verdict |
|---|--:|--:|--:|--:|---|
| HAPPSTMNDS | 452.25 | 438.68 | 432.75 | 4.31% | 3% stop sits 1.4% inside the base — incompatible |
| GLAXO | 3023.40 | 2932.70 | 2866.30 | 5.20% | 3% stop is mid-cup — incompatible |
| SGMART | 846.80 | 821.40 | 802.00 | 5.29% | 3% stop is mid-cup — incompatible |
| JYOTHYLAB | 215.21 | 208.75 | 202.58 | 5.87% | 3% stop is mid-cup — incompatible |
| THELEELA | 574.95 | 557.70 | 540.55 | 5.98% | 3% stop is mid-cup — incompatible |
| TIMEX | 623.95 | 605.23 | 584.80 | 6.27% | 3% stop is mid-cup — incompatible |
| TFCILTD | 137.94 | 133.80 | 128.18 | 7.08% | 3% stop is mid-cup — incompatible |
| SHREEJISPG | 660.80 | 640.98 | 610.00 | 7.69% | 3% stop is mid-cup — incompatible |
| MANIPALHOS | 768.50 | 745.44 | 699.35 | 9.00% | 3% stop is a third of the way in — incompatible |

Honoring the structure means risking 4.3–9.0%, not 3%. On TFCILTD that is 7.08% against an assumed
3% — position size has to come down by roughly 58% for the same rupee risk, and the reward/risk
arithmetic changes with it. A 3% stop on any of these sits mid-base and gets taken out by ordinary
chop **without the pattern having failed at all**.

## 6. Regime note

Bases near highs resolve upward far more often in a trending index than in a choppy one. The same
screener on the same universe has a very different hit rate in the two. Whether this pattern is
present today and whether it is worth trading today are different questions; only a backtest split
by index trend state answers the second, and none was run here.

---

### Method notes

- No threshold, filter parameter or ranking rule was changed for this run. Everything is at the
  defaults in the `nse-pattern-screener` skill.
- Market was closed (17:04 IST run against a 15:30 close), so the 15:15 stub bar was kept as a
  genuine close rather than dropped as in-progress.
- Rankings are by structural RRR (15% target ÷ base depth). It reduces to inverse base depth, which
  is the right criterion for sizing and the wrong one for probability.
