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

I opened `hits.png` and read all nine panels, then re-rendered six of them one and two to a page,
because the 3×3 grid is too small to judge EMA behaviour through a base. **Two names moved up on
that second look — see the note at the end of this section.** Five of the nine are downgraded.

The tier boundary is *"would I act on this chart"*, not *"is this a textbook cup"*. Those are
different questions, and the first is the one worth reporting: an orderly trend with a shallow,
controlled pullback that holds its moving averages and turns back up is a setup, even when the
parabola fitted to it is not a saucer.

### Top tier — 4

**MANIPALHOS** (panel 9) — the best trend in the batch. A 60-bar orderly staircase from 655 to 755
with no gaps and no dominant candle (`max_bar_share` 0.28), both EMAs rising underneath it the
whole way. The pullback then holds the slow EMA at ~712, curls, and the fast EMA turns back up
through it as price makes a new high on the final bar. ₹88.93cr/day, the most liquid name here, so
the entry is fillable at size, and it sits at 100% of its 60-day high with no supply overhead. Its
R² 0.804 is the highest in the batch and — unlike the V-bounce trap the skill warns about — it is
fitting a genuine down-curl-up, not a checkmark. **One caveat that survives the promotion:** the
9.0% `risk_pct_to_base_low` is inflated by a single wick. `base_low` 699.35 is the low of one bar
(21 Aug 09:15); no other bar in the window trades below 710.60 and the lowest close is 714.80. The
honest structural stop is ~710 (7.5%) or 714.80 on a closing basis (7.0%), which also means its
last-place RRR rank understates it.

**TFCILTD** (panel 7) — the only textbook cup in the batch. A 55-bar flat floor at 110–117, then a
sustained multi-bar rally to 137, then a 21-bar base that genuinely rounds: down to 130, curls, and
comes back to a new high on the last bar. Both EMAs run under the base and rise through it. Second
most liquid here (₹86.8cr/day). Caveat: at 0.32% from the lip the breakout is effectively happening
now, so there is no patient entry left.

**GLAXO** (panel 2) — a 50-bar floor at 2,600, a genuine multi-bar thrust to 3,040 (no single candle
above 32% of the move), then a 27-bar consolidation that drifts down to 2,900 and rounds back up.
The base is closer to a downward-sloping shelf than a true saucer, but the structure is honest and
the rally is real.

**SGMART** (panel 3) — same shape as MANIPALHOS and the weaker copy of it. A 45-bar shelf at
710–720, a clean staircase to 825, then a shallow pullback to ~805 and new highs at 845 on the
final bars. The fast EMA never rolls over — it keeps rising straight through the base, which is
about as healthy as a continuation gets. Marked down relative to MANIPALHOS on two counts:
₹11.79cr/day is an order of magnitude thinner, and R² 0.592 is the lowest of the nine because
there is barely a curve to fit.

### Marginal — 3

**HAPPSTMNDS** (panel 1, top-ranked) — the "base" is a 15-bar (≈2 session) flag after a vertical
thrust to 452, and the left half of the window is chop with a dip to 388, not trend. `max_bar_share`
0.48 against a 0.5 gate: nearly half the rally is one candle. It is a legitimate high-tight
pullback; it is ranked first only because a shallow flag mechanically produces the best RRR.

**THELEELA** (panel 5) — the rally leg is the best-looking part of the batch (sustained 500 → 575
over 30 bars). The base is a sharp 15-bar pullback that hasn't stabilised: the fast EMA has rolled
over and is flat-to-declining with price chopping underneath it, and at 3.49% this is the furthest
from its lip of the nine. Too early — this is the one to re-check in a session or two.

**TIMEX** (panel 6) — a flat 585–608 shelf, not a saucer, and the final hourly candle is already a
vertical push from 600 to 623. `vol_ratio` 0.81 means there was no volume dry-up in the base. The
rally leg also begins from a 10% drawdown (575 → 520), so a good part of it is recovery rather than
advance, even though it has now cleared to a new 60-day high.

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

### Revision note

MANIPALHOS and SGMART were originally filed as *marginal* on the grounds that the parabola was
fitted to a trend rather than a base. That was the wrong test. Re-rendered at full size, both show
the thing that actually matters — a controlled pullback that holds its moving averages and turns
back up into new highs — and MANIPALHOS does it with the best trend and the best liquidity in the
batch. The original call also misdescribed MANIPALHOS as having "no consolidation of substance";
there is a real four-session pullback (743 → 715 → 764). Both are now top tier. The three names
left in *marginal* were re-checked at the same size and stay where they were.

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
| MANIPALHOS | 768.50 | 745.44 | 699.35 | 9.00% | 3% stop is a third of the way in — incompatible. **9.00% is a single wick; see below** |

Honoring the structure means risking 4.3–9.0%, not 3%. On TFCILTD that is 7.08% against an assumed
3% — position size has to come down by roughly 58% for the same rupee risk, and the reward/risk
arithmetic changes with it. A 3% stop on any of these sits mid-base and gets taken out by ordinary
chop **without the pattern having failed at all**.

**MANIPALHOS is the one case where the pipeline's own risk number overstates the structure.**
`base_low` 699.35 is the low of a single bar (21 Aug 09:15); the next-lowest low in the window is
710.60 and the lowest close is 714.80. A stop under the wick costs 9.0%; a stop under the body of
the pullback costs 7.0–7.5%. That also means its 1.67 RRR — last of the nine — is computed off the
wick and understates it: on a 7.0% stop the same 15% target gives ~2.14, which would place it
mid-pack rather than bottom. The pipeline is not wrong to use the wick (it is the lowest price the
structure actually traded); it is just worth knowing which of the two numbers you are sizing off.

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
