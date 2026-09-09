# NSE hourly screen — rally + rounded base near highs

**Executed at:** 2026-09-09 **17:04 IST** (`run_ts_ist`; data snapshot completed 17:09 IST)
**Latest data bar:** 2026-09-09 **15:15 IST** — the **2026-09-09 session**, `session_age_days = 0`

The bar screened is the current session's final hourly close. NSE hourly bars run
09:15 → 15:15, the last being a 15-minute stub; the market was closed at run time, so
that stub is a genuine close and was kept rather than dropped.

**Charts:** https://claude.ai/code/artifact/ac851904-d835-48bb-bd5f-500145fa3565
(all 9 panels at native resolution, with the per-name verdicts below repeated alongside them)

---

## 1. Coverage

| | |
|---|---|
| Universe | **EQ** — the full NSE rolling-settlement equity list (the skill's default, not a narrowed slice) |
| Symbols in universe | 2,298 |
| Symbols with usable data | **2,271 (98%)** |
| Dropped by the fetch | 27 — absent from Yahoo entirely, or too few bars for a 60-day hourly window |
| Interval / period | 1h / 60d |
| Last closed bar | 2026-09-09 15:15:00 IST |

This is a near-complete scan of the EQ universe, better than the ~92% the skill's notes treat
as typical. It is still not all 2,298 names: 27 symbols (APOORVA, ASSAMENT, ASTAR, AUGMONT,
DEEPA, ESDS, GFSTEELS, KDGREEN, LUMINO, MUKESHB and 17 others) returned nothing usable and were
never screened. The fetch ran 58 batches with zero failures and two gap-fill rounds.

**Staleness check.** 2,188 of 2,271 symbols (96.3%) carry the 15:15 bar, above the pipeline's
95% warning threshold, so no WARN was printed. **All 9 hits have `bars_behind_universe = 0`** —
every level quoted below is priced at the 2026-09-09 15:15 bar, not an older one.

## 2. Funnel

```
2,298 EQ symbols
  └─ 2,271  fetched with usable 60d hourly data          (−27 absent or too short)
      └─ 21  raw detector hits                            (−2,250 failed the nine gates)
          └─ 9  after context filters                     (−12)
              └─ 2  clean after looking at every chart    (−7: 4 marginal, 3 distrusted)
```

**What the context filters cut (12 names, reasons overlap):**

| Filter | Names cut | What it caught |
|---|---:|---|
| `turnover < ₹5cr/day` | 8 | ONEGLOBAL (₹0.40cr), AAREYDRUGS (₹0.44cr), ZIMLAB (₹0.53cr), PROZONER (₹0.54cr), INSECTICID (₹0.86cr), ONEPOINT (₹1.37cr), ZOTA (₹3.93cr), INNOVACAP (₹4.32cr) — pretty geometry, unfillable entries |
| `base_high < 97% of 60d high` | 7 | BAJAJCON (76.4%), ZOTA (77.6%), INSECTICID (88.0%), TORNTPOWER (88.9%), ONEPOINT (94.1%), ONEGLOBAL (94.8%), AEGISVOPAK (96.1%) — downtrend bounces reading as "base near the window high" |
| `max_bar_share > 0.5` (gap-driven) | 4 | ZIMLAB (0.80), TORNTPOWER (0.72), INSECTICID (0.69), HINDOILEXP (0.60) — one candle carrying more than half the "rally" |

The detector's own 2,271 → 21 cut is not itemised: the per-gate rejection histogram is only
produced by `--diagnose`, which runs when raw hits are zero. They were not, so it did not run.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ base depth, descending. Entry is the lip
(`base_high`); the structural stop is `base_low`.

| # | Symbol | Tier | RRR | Close | Entry (lip) | Base low | Depth % | Risk to base low | Dist from lip | Base | Vol ratio | R² | Curv | Vertex | Rally % | Max bar | ₹cr/day | % of 60d high |
|--:|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | SHREEJISPG | Marginal | 5.36 | 713.10 | 715.00 | 695.00 | 2.80 | 2.80% | 0.27% | 14b ≈2.0s | 0.41 | 0.788 | 0.015 | −0.11 | 11.6 | 0.32 | 34.9 | 100.0 |
| 2 | GKSL | **Clean** | 3.45 | 176.40 | 180.60 | 172.75 | 4.35 | 4.35% | 2.33% | 12b ≈1.7s | 0.60 | 0.660 | 0.017 | −0.02 | 12.7 | 0.29 | 5.4 | 100.0 |
| 3 | PAISALO | Marginal | 3.30 | 79.92 | 80.43 | 76.78 | 4.54 | 4.54% | 0.63% | 16b ≈2.3s | 0.76 | 0.674 | 0.019 | −0.37 | 21.2 | 0.21 | 29.9 | 100.0 |
| 4 | INDOMIM | Distrust | 3.04 | 994.00 | 998.00 | 948.80 | 4.93 | 4.93% | 0.40% | 12b ≈1.7s | 0.84 | 0.642 | 0.027 | +0.03 | 16.6 | 0.45 | 119.0 | 100.0 |
| 5 | SMLMAH | Marginal | 2.71 | 6525.00 | 6629.00 | 6262.00 | 5.54 | 5.54% | 1.57% | 17b ≈2.5s | 0.47 | 0.663 | 0.020 | −0.53 | 25.8 | 0.21 | 23.9 | 100.0 |
| 6 | KLBRENG-B | Marginal | 2.50 | 466.40 | 479.00 | 450.25 | 6.00 | 6.00% | 2.63% | 22b ≈3.2s | 0.65 | 0.496 | 0.032 | −0.04 | 20.8 | 0.23 | 8.1 | 100.0 |
| 7 | SAILIFE | **Clean** | 1.89 | 1677.00 | 1696.80 | 1562.10 | 7.94 | 7.94% | 1.17% | 28b ≈4.1s | 0.79 | 0.826 | 0.028 | −0.62 | 11.6 | 0.46 | 40.7 | 100.0 |
| 8 | PCJEWELLER | Distrust | 1.84 | 13.91 | 14.37 | 13.20 | 8.14 | 8.14% | 3.20% | 15b ≈2.2s | 0.73 | 0.496 | 0.020 | −0.25 | 40.1 | 0.34 | 246.2 | 100.0 |
| 9 | LALITHAA | Distrust | 1.68 | 336.20 | 339.90 | 309.55 | 8.93 | 8.93% | 1.09% | 21b ≈3.0s | 0.75 | 0.802 | 0.038 | −0.38 | 25.5 | 0.30 | 229.6 | 100.0 |

Base width in sessions assumes ~7 hourly bars per NSE trading day. T1/T2 targets, for reference:
SHREEJISPG 736.45 / 822.25 · GKSL 186.02 / 207.69 · PAISALO 82.84 / 92.49 · INDOMIM 1027.94 / 1147.70 ·
SMLMAH 6827.87 / 7623.35 · KLBRENG-B 493.37 / 550.85 · SAILIFE 1747.70 / 1951.32 ·
PCJEWELLER 14.80 / 16.53 · LALITHAA 350.10 / 390.88.

**Every one of the nine sits at 100.0% of its 60-day high.** That is unusual and worth noting:
the near-high filter did no work at this stage, because everything that survived the other gates
was already making a new window high on the screened bar.

## 4. Tiers from the visual pass

Every name below cleared all nine detector gates and all three context filters. The tier is
where looking at the chart agrees with that — or does not.

### Clean structural match (2)

**SAILIFE** (rank 7) — **the only genuine saucer in the batch.** A three-week advance from 1,430,
then a real dip to 1,562 and a rounded recovery to a new high at 1,700, with the fast EMAs dipping
under the base and curling back up through it. Highest R² here at 0.826, and unlike LALITHAA below
the fit is describing something that is actually on the chart. Longest base too, at 4.1 sessions.
*Caveats:* one bar carries 46% of the rally, just under the 0.5 gap-driven cutoff — the closest call
in the batch. The recovery half of the saucer is a near-vertical push into the lip, so entering now
is entering into that thrust. Structural risk of 7.94% is the second-widest on the page.

**GKSL** (rank 2) — the most orderly advance here: 12.7% over 42 bars from 152 to 178 with no
dominant candle at all (largest bar 29% of the move, second-lowest gap-dependence), EMAs beneath
price the whole way, and a quiet hold 2.33% under the lip so the setup has not yet triggered.
*Caveats:* ₹5.37cr/day is a **boundary pass** over the ₹5cr floor — the thinnest name that cleared,
and a boundary pass is not the same evidence as a margin pass. The base is a flat shelf rather than
a saucer, and at 1.7 sessions it is the youngest here.

### Marginal (4)

**SHREEJISPG** (rank 1) — **the top-ranked name is ranked there for the wrong reason.** RRR is
15% ÷ base depth, so the narrowest shelf wins by construction, and at 2.80% this is the narrowest.
The stock sat flat near 640 for three weeks, then ran to 710 in four sessions; the shaded window is
a two-session flat shelf pinned at the high, not a rounding. What it genuinely has is the only
defensible stop on the page — see section 5.

**SMLMAH** (rank 5) — the strongest trend in the batch by some distance: 25.8% over 38 bars from
5,200 to 6,600, largest bar only 21% of the move, EMAs rising steeply underneath throughout. The
problem is that the shaded window is not a base. It is the final leg of that run, drifting upward
and closing at a new high on the last bar. The vertex at −0.53 says the parabola is fitting
"flat, then up" rather than a cup. Entering at 6,629 is entering after a 25% move in five sessions.

**KLBRENG-B** (rank 6) — a real month-long staircase from 360 to 478 with a 3.2-session pause on
the end, the longest base except SAILIFE, and price still 2.63% under the lip. Against it: R² 0.496
is the joint-lowest in the batch, and the chart says why — the window is a choppy 450-to-478 range,
not a rounding. ₹8.1cr/day is thin. The `-B` suffix is the genuine NSE symbol, but confirm it maps
to what you expect on your platform before acting on it.

**PAISALO** (rank 3) — the launch is cleaner than it looks: 21.2% with the largest single bar at
only 21% of the move, the joint-lowest gap-dependence here, so this was a multi-candle advance and
not a gap. But it took three sessions off a flat 66-to-70 drift, and the shaded window is a
two-session shelf sitting on top of that near-vertical leg. The 76.78 "structural stop" is simply
where the thrust began, not a floor the structure has defended.

### Distrust despite passing every filter (3)

**INDOMIM** (rank 4) — **the V trap the skill warns about, in its clearest form.** The stock fell
from 960 on 19 August to 840 on 2 September, then snapped back to 994. The "16.6% rally" is a round
trip, not an advance, and price is re-entering its own mid-August supply between 950 and 985. One
bar carries 45% of the move, second-highest here. It passes `pct_of_60d_high` at 100% only because
the final bar just cleared the August high, which is precisely the case that filter is weakest
against. R² 0.642.

**PCJEWELLER** (rank 8) — a ₹13.91 stock that rose 40.1% in three sessions, most of it one vertical
thrust from 10.50 to 14.40. The shaded window is the shelf after a spike, which is where distribution
happens, not a base. R² 0.496 joint-lowest, depth 8.14% makes the stop meaningless, and price is 3.2%
below the lip — the furthest of the nine. The ₹246cr of daily turnover measures the spike, not a
liquidity profile that will still be there next week.

**LALITHAA** (rank 9) — third-highest R² on the page at 0.802, and it should not be trusted for that.
The 21-bar window swings between 310 and 340, an 8.93% range and the widest here. That is volatile
chop at the highs, and the parabola scores it well only because three sessions of chop happen to
trace a U. A base you cannot place a stop inside is not doing the job a base exists to do.

## 5. Risk reality check — the stop-inside-base problem

**Eight of the nine names have a 3% stop landing inside the base.** SHREEJISPG is the single
exception, and it is in the marginal tier.

| Symbol | Entry (lip) | 3% stop | Base low (real stop) | Structural risk | 3% stop compatible? |
|---|--:|--:|--:|--:|---|
| SHREEJISPG | 715.00 | 693.55 | 695.00 | 2.80% | **Yes** — 3% sits 0.21% below the base low |
| GKSL | 180.60 | 175.18 | 172.75 | 4.35% | No — 3% sits 1.4% above the base low |
| PAISALO | 80.43 | 78.02 | 76.78 | 4.54% | No |
| INDOMIM | 998.00 | 968.06 | 948.80 | 4.93% | No |
| SMLMAH | 6629.00 | 6430.13 | 6262.00 | 5.54% | No |
| KLBRENG-B | 479.00 | 464.63 | 450.25 | 6.00% | No — 3% is half the base |
| SAILIFE | 1696.80 | 1645.90 | 1562.10 | 7.94% | No |
| PCJEWELLER | 14.37 | 13.94 | 13.20 | 8.14% | No — 3% is a third of the base |
| LALITHAA | 339.90 | 329.70 | 309.55 | 8.93% | No — 3% is a third of the base |

On those eight, a 3% stop off the lip sits mid-base and gets taken out by ordinary chop **without
the pattern having failed**. Honouring the structure means risking 4.4% to 8.9%, which cuts to
roughly half or a third the position size a 3% assumption would imply, and changes the reward/risk
arithmetic accordingly. Note that the two names I rate clean, GKSL and SAILIFE, are both in this
group — the one name with a workable fixed stop is one whose structure I do not rate.

**Wick check.** `base_low_is_wick` is false for all nine — no base low is set by a single outlier
bar, so `base_low` and the ranking stand as computed. Two names have a closing-basis floor
meaningfully tighter than the wick low, worth knowing if you size off closes:

- **PCJEWELLER** — base low 13.20 (8.14%) vs closing-basis 13.41 (**6.68%**).
- **SAILIFE** — base low 1562.10 (7.94%) vs closing-basis 1571.00 (**7.41%**).

The other seven differ by less than 0.6 percentage points between the two readings. None of them
crosses the 3% line on a closing basis either.

## 6. What this is, and is not

- **These are candidates matching a geometry, not recommendations.** The screen says a shape is
  present on the 2026-09-09 hourly chart. It says nothing about whether the shape resolves upward,
  and nothing about whether you should hold any of it.
- **RRR ranks the geometry, not the odds.** `rrr_structural` reduces to inverse base depth. It
  states what a trade pays if it works and is silent on how often it works. Today the top-ranked
  name (SHREEJISPG) is marginal and the best-shaped name (SAILIFE) ranks seventh of nine.
- **Names I distrust despite a clean pass:** INDOMIM, PCJEWELLER and LALITHAA cleared every
  numeric gate and are, on the chart, a V-shaped round trip, a post-spike shelf and three sessions
  of wide chop respectively. Section 4 says why for each.
- **Names that only just cleared:** GKSL passed the turnover floor at ₹5.37cr against ₹5.00cr, and
  SAILIFE passed the gap-driven cutoff at 0.46 against 0.50. Both are in the clean tier, so both
  caveats matter.
- **No threshold was loosened.** Every parameter ran at its default — `min_curvature` 0.015,
  `MIN_TURNOVER` ₹5cr/day, near-high floor 97%, gap-driven cutoff 0.5, `MIN_COVERAGE` 80%,
  `TARGET_PCT` 15. Nine clean hits is what the defaults produced on this session; nothing was
  re-run to change that number.
- **One parameter observation, left alone.** Every surviving name sits at exactly 100.0% of its
  60-day high, meaning the 97% near-high filter cut nothing among the survivors and only bit on
  names that other filters were also rejecting. That is a note for whoever tunes this, not a change
  I made.
