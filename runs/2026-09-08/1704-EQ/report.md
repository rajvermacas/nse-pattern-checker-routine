# NSE hourly screen — rally + rounded base near highs

**Executed at:** 2026-09-08 **17:04 IST** (`run_ts_ist`; data snapshot completed 17:09 IST)
**Latest data bar:** 2026-09-08 **15:15 IST** — the **2026-09-08 session**, `session_age_days = 0`

The bar screened is the current session's final hourly close. NSE hourly bars run
09:15 → 15:15, the last being a 15-minute stub; the market was closed at run time, so
that stub is a genuine close and was kept rather than dropped.

**Charts:** https://claude.ai/code/artifact/ec5ae771-2e9b-452b-a279-347e8389523e
(all 14 panels at native resolution, with the per-name verdicts below repeated alongside them)

---

## 1. Coverage

| | |
|---|---|
| Universe | **EQ** — the full NSE rolling-settlement equity list (the skill's default, not a narrowed slice) |
| Symbols in universe | 2,304 |
| Symbols with usable data | **2,272 (98%)** |
| Dropped by the fetch | 62 — 32 returned nothing from Yahoo, 30 had too few bars for a 60-day hourly window |
| Interval / period | 1h / 60d |
| Last closed bar | 2026-09-08 15:15:00 IST |

This is a near-complete scan of the EQ universe, better than the ~92% the skill's notes
treat as typical. It is still not all 2,304 names: 32 symbols (ALFREDHE, APOORVA, ARYAMAN,
ASSAMENT, ASTAR, AUGMONT, DEEPA, ESDS, GFSTEELS, KANCOTEA and 22 others) are absent from
Yahoo entirely and were never screened.

**Staleness check.** 2,141 of 2,272 symbols (94.2%) carry the 15:15 bar, which is just under
the pipeline's 95% warning threshold, so the pipeline printed a WARN. That warning does not
apply to anything in this report: **all 14 hits have `bars_behind_universe = 0`** and every
level quoted below is priced at the 2026-09-08 15:15 bar.

## 2. Funnel

```
2,304 EQ symbols
  └─ 2,272  fetched with usable 60d hourly data          (−32 absent, −30 too short)
      └─ 41  raw detector hits                            (−2,231 failed the nine gates)
          └─ 14  after context filters                    (−27)
              └─ 5  clean after looking at every chart    (−9: 5 marginal, 4 distrusted)
```

**What the context filters cut (27 names, reasons overlap):**

| Filter | Names cut | What it caught |
|---|---:|---|
| `turnover < ₹5cr/day` | 15 | KANANIIND (₹0.01cr), BLBLIMITED (₹0.12cr), SPCENET (₹0.16cr), NRAIL, ASIANHOTNR, PROZONER, GLOBAL, OAL, VPRPL, AYMSYNTEX, SURAKSHA, INNOVACAP, HATSUN (₹4.96cr), IZMO, VENKEYS — pretty geometry, unfillable entries |
| `max_bar_share > 0.5` (gap-driven) | 14 | GODREJAGRO (0.99), HBLENGINE (0.96), BLBLIMITED (1.88), VENKEYS (1.21), GRAPHITE (0.83), IZMO, ALEMBICLTD, RUBICON, NRAIL, KANANIIND, HINDOILEXP, ASIANHOTNR, PARAGMILK, SPCENET — one candle carrying more than half the "rally" |
| `base_high < 97% of 60d high` | 10 | KIRLOSENG (84.0%), GMRP&UI (89.3%), HBLENGINE (86.9%), KANANIIND (87.8%), VPRPL (88.5%), CLEANMAX (92.7%), CPPLUS (94.2%), AEGISVOPAK (94.3%), SPCENET (81.7%), IZMO (81.7%) — downtrend bounces reading as "base near the window high" |

The detector's own 2,272 → 41 cut is not itemised: the per-gate rejection histogram is only
produced by `--diagnose`, which runs when raw hits are zero. They were not, so it did not run.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ base depth, descending. Entry is the lip
(`base_high`); the structural stop is `base_low`.

| # | Symbol | RRR | Close | Entry (lip) | Base low | Depth % | Risk to base low | Dist from lip | Base | Vol ratio | R² | Curv | Vertex | Rally % | ₹cr/day | % of 60d high |
|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | JINDRILL | 3.72 | 677.00 | 684.00 | 656.45 | 4.03 | 4.03% | 1.02% | 12b ≈1.7s | 0.65 | 0.861 | 0.019 | −0.04 | 13.1 | 13.0 | 99.6 |
| 2 | CHENNPETRO | 3.71 | 1457.80 | 1474.90 | 1415.30 | 4.04 | 4.04% | 1.16% | 19b ≈2.8s | 0.54 | 0.656 | 0.021 | −0.06 | 10.8 | 87.5 | 99.1 |
| 3 | SSWL | 3.61 | 373.10 | 377.00 | 361.35 | 4.15 | 4.15% | 1.03% | 12b ≈1.7s | 0.15 | 0.559 | 0.019 | +0.08 | 31.8 | 13.7 | 98.3 |
| 4 | WELSPUNLIV | 3.27 | 208.55 | 214.37 | 204.54 | 4.59 | 4.59% | 2.71% | 12b ≈1.7s | 0.73 | 0.805 | 0.019 | +0.48 | 13.9 | 55.0 | 99.2 |
| 5 | KLBRENG-B | 2.91 | 459.70 | 475.95 | 451.40 | 5.16 | 5.16% | 3.41% | 14b ≈2.0s | 0.60 | 0.890 | 0.018 | +0.36 | 20.8 | 7.8 | 100.0 |
| 6 | WELENT | 2.87 | 788.70 | 818.70 | 775.95 | 5.22 | 5.22% | 3.66% | 16b ≈2.3s | 0.54 | 0.605 | 0.025 | +0.21 | 24.2 | 17.2 | 99.2 |
| 7 | SAILIFE | 2.77 | 1650.00 | 1657.00 | 1567.40 | 5.41 | 5.41% | 0.42% | 17b ≈2.5s | 0.57 | 0.832 | 0.023 | −0.54 | 11.6 | 36.6 | 100.0 |
| 8 | SHILPAMED | 2.65 | 960.50 | 978.55 | 923.05 | 5.67 | 5.67% | 1.84% | 21b ≈3.1s | 0.36 | 0.647 | 0.033 | +0.07 | 12.4 | 56.2 | 100.0 |
| 9 | DHOOTTRANS | 2.45 | 1589.70 | 1631.00 | 1531.10 | 6.13 | 6.13% | 2.53% | 15b ≈2.2s | 0.44 | 0.614 | 0.017 | −0.38 | 16.6 | 385.7 | 98.0 |
| 10 | DEEPINDS | 2.18 | 818.70 | 821.55 | 765.00 | 6.88 | 6.88% | 0.35% | 17b ≈2.5s | 0.74 | 0.782 | 0.019 | −0.54 | 19.4 | 15.7 | 100.0 |
| 11 | DCBBANK | 2.10 | 229.55 | 234.79 | 218.05 | 7.13 | 7.13% | 2.23% | 27b ≈3.9s | 0.68 | 0.716 | 0.034 | −0.28 | 10.4 | 24.8 | 100.0 |
| 12 | MANINDS | 1.86 | 822.50 | 843.90 | 776.00 | 8.05 | 8.05% | 2.54% | 22b ≈3.2s | 0.55 | 0.715 | 0.023 | −0.64 | 13.6 | 33.2 | 100.0 |
| 13 | MANALIPETC | 1.76 | 90.08 | 92.70 | 84.80 | 8.52 | 8.52% | 2.83% | 22b ≈3.2s | 0.18 | 0.667 | 0.043 | −0.15 | 28.4 | 9.4 | 100.0 |
| 14 | AEROFLEX | 1.57 | 573.50 | 584.15 | 528.35 | 9.55 | 9.55% | 1.82% | 30b ≈4.4s | 0.63 | 0.767 | 0.028 | −0.53 | 16.4 | 37.9 | 100.0 |

Base width in sessions assumes ~7 hourly bars per NSE trading day.

## 4. Tiers from the visual pass

Every name below cleared all nine detector gates and all three context filters. The tier is
where looking at the chart agrees with that — or does not.

### Clean structural match (5)

**SSWL** — the best trend on the page. A 31.8% advance over 42 bars with no single dominant
candle (max bar share 0.22), EMAs turning up and riding under the whole leg, and volume dried
to 0.15× into a tight hold 1.03% under the lip. *Caveat:* the base is a flat shelf rather than
a saucer, and at 1.7 sessions it is young.

**WELSPUNLIV** — the cleanest advance: orderly higher lows from 180 to 214 across three weeks,
EMAs beneath price throughout, largest bar only 17% of the move — the lowest gap-dependence in
the batch. *Caveat:* base is 1.7 sessions and the vertex sits late (+0.48), meaning the low is
near the right edge of the window. The pullback may not be finished.

**SHILPAMED** — the most genuinely *rounded* base here: 3.1 sessions, a real dip to 923 and a
recovery to 960, with the fast EMA dipping and curling back up through it. Volume ratio 0.36.
*Caveat:* a volatile name — the 01 Sep bar ranged 878 to 950.

**WELENT** — sustained staircase from 570 to 818 with EMAs beneath throughout, then a 2.3-session
shelf. *Caveat:* price is still 3.66% below the lip, the furthest of the clean names, so the
setup needs more work before it triggers.

**KLBRENG-B** — best fit in the batch (R² 0.89) on a real 20.8% staircase, base a tight two-session
flat consolidation. *Caveats:* the 475.95 lip is a single spike wick from 07 Sep, and ₹7.8cr/day
is the thinnest turnover that cleared the ₹5cr floor. The `-B` suffix is the genuine NSE symbol,
but confirm it maps to what you expect on your platform.

### Marginal (5)

**CHENNPETRO** (rank 2) — the base itself rounds well and the EMAs rise through it. The context is
the problem: this is a snapback off a three-week decline from 1,440 to 1,325, not a base built
inside an uptrend. It passed the `pct_of_60d_high` filter at 99.1% because the recovery reclaimed
the mid-August range, which is exactly the situation that filter is weakest against.

**SAILIFE** (rank 7) — genuinely strong trend, but the shaded window holds a dip and then a vertical
push that closes 0.42% from the lip. That is a breakout in progress, not a base waiting to break,
and one bar carries 42% of the rally — just under the 0.5 gap-driven cutoff.

**DCBBANK** (rank 11) — longest, flattest shelf in the batch (3.9 sessions) and the EMAs do rise
through it. But the 234.79 lip is one spike wick, and the final bar is a vertical thrust straight
at it: entering here is entering after the move.

**MANALIPETC** (rank 13) — volume dry-up is real (0.18×) and the rally is sustained across several
sessions. The base drifts down rather than rounding, and the last bar is a one-candle ~6% snap
back to the lip. Depth 8.52% makes it expensive to hold properly.

**AEROFLEX** (rank 14) — it does round: a 4.4-session saucer from 545 down to 528 and back to 573,
the longest base here. But 9.55% deep is a correction, not a base, which is precisely why it ranks
last, and the lip is being tested by the current bar.

### Distrust despite passing every filter (4)

**JINDRILL** (rank 1) — **the top-ranked name is the one I trust least.** Its R² of 0.861 is the
second-highest in the batch and it is the exact trap the skill warns about: the 12-bar window is a
V — 684 down to 656 and back to 677 — which a parabola fits beautifully and which is not a rounding.
Zoom out and the stock was 665 three weeks ago, fell to 608, and has round-tripped back into its own
mid-August supply. The "13.1% rally" is a recovery leg, not an advance.

**DEEPINDS** (rank 10) — there is no base. The shaded window sits entirely inside a near-vertical
19% run: price rose from ~750 to 821 within it and closed at the high, 0.35% from the lip. The
parabola is fitting an accelerating up-leg, and the 6.88% "structural risk" is simply where that leg
started two sessions ago — not a floor the structure defends.

**DHOOTTRANS** (rank 9) — the 1,631 lip is a single spike, and what follows is a fade off it rather
than a rounding. The EMAs flatten through the window instead of rising through it. ₹386cr/day of
turnover, the deepest liquidity in the batch, does not fix the shape.

**MANINDS** (rank 12) — same failure as DEEPINDS. The window holds the final up-leg, not a pause,
and the vertex at −0.641 sits right on the |vx| ≤ 0.65 boundary: the fit is "flat, then up", which
is not a cup. Closed near its high after a vertical push.

## 5. Risk reality check — the stop-inside-base problem

**All 14 names have a 3% stop landing inside the base.** Not one of them supports it.

| Symbol | Entry (lip) | 3% stop | Base low (real stop) | Structural risk | 3% stop compatible? |
|---|--:|--:|--:|--:|---|
| JINDRILL | 684.00 | 663.48 | 656.45 | 4.03% | No — 3% sits 1.1% above the base low |
| CHENNPETRO | 1474.90 | 1430.65 | 1415.30 | 4.04% | No |
| SSWL | 377.00 | 365.69 | 361.35 | 4.15% | No |
| WELSPUNLIV | 214.37 | 207.94 | 204.54 | 4.59% | No |
| KLBRENG-B | 475.95 | 461.67 | 451.40 | 5.16% | No |
| WELENT | 818.70 | 794.14 | 775.95 | 5.22% | No |
| SAILIFE | 1657.00 | 1607.29 | 1567.40 | 5.41% | No |
| SHILPAMED | 978.55 | 949.19 | 923.05 | 5.67% | No |
| DHOOTTRANS | 1631.00 | 1582.07 | 1531.10 | 6.13% | No — 3% is barely half the base |
| DEEPINDS | 821.55 | 796.90 | 765.00 | 6.88% | No |
| DCBBANK | 234.79 | 227.75 | 218.05 | 7.13% | No |
| MANINDS | 843.90 | 818.58 | 776.00 | 8.05% | No |
| MANALIPETC | 92.70 | 89.92 | 84.80 | 8.52% | No |
| AEROFLEX | 584.15 | 566.63 | 528.35 | 9.55% | No — 3% is under a third of the base |

A 3% stop off the lip sits mid-base on every one of these names and gets taken out by ordinary
chop **without the pattern having failed**. Honouring the structure means risking 4.0% to 9.6%,
which roughly halves to a third the position size a 3% assumption would imply, and changes the
reward/risk arithmetic accordingly.

**Wick check.** `base_low_is_wick` is false for all 14 — no base low is set by a single outlier
bar, so `base_low` and the ranking stand as computed. Two names have a closing-basis floor
meaningfully tighter than the wick low, worth knowing if you size off closes:

- **JINDRILL** — base low 656.45 (4.03%) vs closing-basis 663.75 (**2.96%**). The only name in
  the batch where a 3% stop is roughly compatible on a closing basis. It is also the name I
  distrust most, so this is not an argument for taking it.
- **DEEPINDS** — base low 765.00 (6.88%) vs closing-basis 777.50 (5.36%).

The other twelve differ by less than 1.5 percentage points between the two readings.

## 6. What this is, and is not

- **These are candidates matching a geometry, not recommendations.** The screen says a shape is
  present on the 2026-09-08 hourly chart. It says nothing about whether the shape resolves upward,
  and nothing about whether you should hold any of it.
- **RRR ranks the geometry, not the odds.** `rrr_structural` reduces to inverse base depth. It
  states what a trade pays if it works and is silent on how often it works. A 3.72 at a 20% hit
  rate is worse than a 2.10 at 50%. The top-ranked name here (JINDRILL) is in the distrust tier.
- **No threshold was loosened.** Every parameter ran at its default — `min_curvature` 0.015,
  `min_r2` 0.45, `vertex_window` 0.65, `min_rally` 0.10, `base_max_depth` 0.10,
  `max_dist_from_high` 0.04, turnover floor ₹5cr, target 15%. The funnel (2,272 → 41 → 14) sits
  in the healthy range the skill describes, so no retuning is indicated. If anything, the four
  distrusted names suggest the vertex window at 0.65 is loose enough to admit "flat, then up" as
  a base — that is an observation, not a change; the thresholds were left alone.
- **Regime matters.** Bases near highs resolve upward far more often in a trending index than a
  choppy one. The same screener on the same universe has a very different hit rate in the two, and
  only a backtest split by index trend state addresses it.
- **The charts are matplotlib renderings of yfinance data**, not screenshots from any platform.
  EMA seeding and session handling differ from TradingView and Kite. Confirm every price on your
  own platform before acting.
