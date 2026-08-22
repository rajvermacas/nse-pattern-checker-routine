# Parameters and tuning

Two patterns share this skill's plumbing:

- **`rally_cup`** (`screener.py`) — a rally into a rounded base near the highs.
  Buys the breakout above the lip of a *finished* base.
- **`momentum_dip`** (`momentum_dip.py`) — a shallow, orderly pullback in a
  stock that is already advancing. Buys *inside* an unfinished move.

They are complements, not variants, and their numbers do not mean the same
things. Read the cross-pattern warning at the bottom before putting the two
shortlists in one table.

## The curvature scale (read this before touching thresholds)

The parabola `y = ax² + bx + c` is fit with x normalized to [-1, 1] and price
divided by its own mean. Under that normalization, for a symmetric cup with its
vertex at center:

    y(±1) − y(0) = a

so **`a` is approximately the cup's fractional depth**. A 5% cup gives a ≈ 0.05.

Measured across the NSE universe (hourly, 12–24 bar windows, EMA-stacked names):

| percentile | curvature | R² | \|vertex_x\| |
|---|---|---|---|
| p50 | 0.005 | 0.64 | 0.43 |
| p75 | 0.014 | 0.81 | 0.97 |
| p90 | 0.022 | 0.89 | 2.48 |
| p95 | 0.031 | 0.91 | 4.58 |
| p99 | 0.043 | 0.96 | 14.6 |

Set `min_curvature` above p99 and nothing can ever match. This is the single
easiest way to produce a screener that silently returns zero on every input and
looks like a quiet market.

## The shape scale (saucer vs checkmark)

Curvature and R² cannot tell a rounded base from a V-bounce — the V often fits
the parabola *better*. Two scale-free metrics can, and both are gated:

**`vee_gain`** — how much better the best two-straight-line "V" model fits the
base than the parabola does, as a fraction of the parabola's error:

    vee_gain = (rmse_parabola − rmse_vee) / rmse_parabola

Negative means the curve wins (a saucer). Positive means two straight legs win
(a checkmark). Reject **above** `max_vee_gain`.

**`bottom_frac`** — share of the base's closes sitting in the lower third of its
range. A parabola loiters at the bottom (~0.58); straight legs pass through it
(~0.33). Reject **below** `min_bottom_frac`.

Measured on synthetic bases with known shapes, at realistic hourly bar noise
(σ ≈ 0.8% per bar), rejection rates at `vee_gain >` each threshold:

| shape | > 0.00 | > 0.05 | > 0.10 | > 0.15 |
|---|---|---|---|---|
| genuine parabolic cup | 16% | **10%** | 5% | 3% |
| cup with a handle | 14% | **10%** | 5% | 2% |
| symmetric V-bounce | 89% | **80%** | 67% | 50% |
| asymmetric V-bounce | 82% | **68%** | 50% | 32% |

The default sits at **0.05**: it costs about one genuine cup in ten to remove
roughly three V-bounces in four. That trade is right for this screener
specifically, because the funnel is ~350:1 and the scarce resource is the
attention spent looking at charts, not the supply of candidates.

`limb_ratio` (shallower limb slope ÷ steeper limb slope) is computed and
reported but **not gated** — cups with handles are legitimately lopsided.

### What the shape gates did on a live batch

On a nifty500 hourly session (2026-08-21), the legacy gate set returned 6 raw
hits and the shape gates cut 5 of them. Reading the charts afterwards:

| name | vee_gain | verdict on the chart |
|---|---|---|
| AEGISLOG | +0.29 | V-bounce, and the whole window is a recovery from a fall |
| SOLARINDS | +0.15 | V, and the "rally" is one gap candle |
| PAYTM | +0.33 | textbook checkmark; also `k_pass` 1 |
| HFCL | +0.06 | **marginal** — a shallow saucer by eye, cut by 0.014 |
| KPIL | — | cut earlier, by the rally-drawdown gate: the leg gave back most of a spike |
| JYOTICNC | −0.14 | kept, and plainly the best chart in the batch |

HFCL is the honest cost of the threshold: a defensible name lost to a boundary.
Every such cut is written to `shape_rejects.json` on every run, so a marginal
rejection is visible rather than silent — read it before accepting a thin day.

## rally_cup detector parameters

| Param | Default | Raise it to... | Lower it to... |
|---|---|---|---|
| `base_min` | 12 | demand a longer, more developed base | catch quick pauses |
| `base_max` | 30 | allow multi-week bases | keep bases tight |
| `base_max_depth` | 0.10 | tolerate deeper pullbacks | insist the base is shallow |
| `min_curvature` | 0.015 | demand pronounced rounding | catch flatter bases (more noise) |
| `min_r2` | 0.45 | demand a clean fit | let ragged bases through |
| `vertex_window` | 0.65 | allow off-center turns | force the turn mid-base |
| `max_vee_gain` | 0.05 | tolerate more V-shaped bases | demand a rounder saucer |
| `min_bottom_frac` | 0.30 | demand more time spent at the low | allow sharper turns |
| `min_k_stability` | 2 | demand more window lengths agree | accept a single fitting window |
| `min_rally` | 0.10 | require a bigger prior move | catch smaller setups |
| `rally_max_bars` | 45 | look further back for the leg | require a recent, tight rally |
| `max_rally_dd_share` | 0.5 | tolerate a choppier leg | demand one clean move |
| `min_slope_ratio` | 1.5 | demand the rally clearly outpace the base | allow gentler contrast |
| `base_top_vs_rally_high` | 0.97 | force the base right at the high | allow a deeper pullback |
| `max_dist_from_high` | 0.04 | catch names further from the lip | only names about to break out |
| `max_base_vol_ratio` | 0.85 | ignore volume | demand a real dry-up |
| `suspect_vol_ratio` | 0.10 | flag more names as data artifacts | flag fewer |
| `lookback` | 120 | more context per symbol | faster, more myopic |

`vertex_x` deserves attention. It's where the parabola's minimum sits within the
normalized base. Near 0 means the turn happened mid-base — a real cup. Values
beyond ±1 mean the vertex is outside the window entirely, so the fit is a
one-directional curve, not a cup. Tightening `vertex_window` to about 0.4 used
to be the only numeric defense against V-bounces; `max_vee_gain` is a more
direct one and costs fewer legitimate asymmetric cups.

`min_k_stability` addresses a multiple-comparisons problem rather than a shape
one. The detector tries 19 window lengths (12–30) and keeps the best-scoring
one, so a symbol gets 19 chances to fit. `k_pass` counts how many of them
actually passed every gate; `k_span` reports the range. A base that fits at one
k and no other is an artifact of the search, not a structure. Genuine bases
score 3–8 here.

`max_rally_dd_share` rejects a leg that gave back more than half its own gain
mid-way. Low-to-high measurement cannot see that shape; it is what caught KPIL
above, where a spike and its retracement read as one 12% rally.

## momentum_dip detector parameters

| Param | Default | Meaning |
|---|---|---|
| `min_advance` | 0.10 | close-to-close advance into the swing high |
| `leg_max_bars` | 60 | how far back the advance may be measured |
| `min_leg_bars` | 8 | an advance shorter than this is a spike |
| `trend_bars` | 30 | EMA50 must be above where it was this many bars ago |
| `max_below_window_high` | 0.02 | the swing high must *be* the window's high |
| `min_dip` / `max_dip` | 0.03 / 0.12 | pullback depth from the swing high |
| `min_dip_bars` / `max_dip_bars` | 2 / 15 | pullback length |
| `max_retrace` | 0.50 | dip as a share of the advance it interrupts |
| `max_dip_bar_share` | 0.60 | most of the fall in one candle = news, not structure |
| `max_dip_vol_ratio` | 1.00 | dip volume vs advance volume |
| `max_close_below_ema_slow` | 0.02 | how far a dip *close* may sit under EMA50 |
| `require_reclaim_ema_slow` | True | the entry bar must close back above EMA50 |
| `require_stabilised` | True | the last bar must show the fall has paused |
| `min_close_pos` | 0.50 | where the last close sits in its own bar's range |
| `max_recovered` | 0.80 | how much of the dip may already be retraced |

**`min_advance` is the gate most likely to empty this screen**, and it was
calibrated rather than guessed. On a live nifty500 hourly session the available
advance distributed as p50 3.7% / p75 6.2% / p90 9.8% / p95 12.9% / p99 20.0%.
At the initial 0.15, exactly 39 candidates reached the gate and none passed it —
a screen that returns zero on every input. At 0.10 (≈p90, and the same floor
`rally_cup` uses for its rally leg) it stops binding: 0.10, 0.08 and 0.06 all
return the same hits, so nothing below 0.10 buys anything.

Note what is deliberately **not** required: `close > EMA20`. The whole premise
is that price has fallen back into or through the fast average; demanding it
stay above would only return names that never dipped.

`require_stabilised` is what separates this screen from a falling-knife
detector. Turning it off with `--no-stabilised` is a diagnostic tool only — the
script prints a warning when you do, and any report built on it must say so.

## Context filter parameters (both patterns)

`postfilter.py` reads only canonical keys (`pattern_bars`, `leg_bars`,
`struct_high`, `risk_pct`), so it applies unchanged to both screens.

| Param | Default | Note |
|---|---|---|
| `--min-turnover` | 5.0 (₹ cr/day) | ~1,200–1,500 NSE names clear ₹5cr. Raise to 20 for a large-cap-only scan |
| `--min-pct-60d-high` | 97.0 | how close the lip / swing high must be to the true 60-day high |
| `--max-bar-share` | 0.5 | max fraction of the rally / advance from any single bar |
| `--bars-per-day` | 7 | NSE hourly. Use 25 for 15-minute, 1 for daily |
| `--target-pct` | 15.0 | profit target off the entry, in percent; the RRR numerator |

## Ranking

Clean hits are sorted by `rrr_structural = target_pct / risk_pct`, where
`risk_pct` runs from the entry to the structural low. For `rally_cup` the entry
*is* the lip, so this is still exactly target ÷ base depth.

Base depth is the risk, because the base low is the only stop the structure
supports, so this is the one output column that connects the geometry to
position sizing. Typical values on hourly NSE bases (4-8% deep) land between
1.9 and 4.9 at a 15% target.

A weighted composite of depth, distance-from-lip, volume dry-up, R², and rally
strength was tested against pure RRR on a live 12-name batch: mean disagreement
1.7 places, same name top and bottom. Depth dominates the other components, so
the composite added complexity without changing the ordering. Rank on RRR;
report the rest as context columns.

RRR describes payoff, not probability. It cannot be presented as a likelihood
of success or as a buy ranking -- only a backtest gives hit rate.

### The two patterns' RRRs are not comparable

A `momentum_dip` entry sits 1–3% above its stop, so its RRR lands around 5–15
against the cup screen's 2–5. That is arithmetic, not edge. The dip's stop is
tighter *and* likelier to be hit: the entry is inside a move that has not
finished, where the cup screen waits for one that has. `risk_pct_buffered`
(half an ATR below the dip low) is the risk a real position has to carry, and
is the number to quote when the two lists appear near each other. Never merge
the two shortlists into one RRR-sorted table.

## Timeframe notes

NSE hourly bars: 09:15, 10:15, ... 15:15, where the last is a 15-minute stub —
about **7 bars per trading day**. Translate for the user: a 21-bar base is
roughly three sessions.

For 15-minute bars, scale bar counts by ~3.5 (`base_min` 40, `rally_max_bars`
150, `max_dip_bars` 50, `leg_max_bars` 200) and set `--bars-per-day 25`.
yfinance gives ~60 days of 15m.

For daily bars, `base_min` 10, `base_max` 40, `rally_max_bars` 60,
`max_dip_bars` 8, `leg_max_bars` 40, `--bars-per-day 1`, and `--period 2y`
since the 60-day intraday cap doesn't apply. Percentage gates (`min_dip`,
`min_advance`) need raising on daily bars — the same 60 bars covers three
months rather than nine sessions.

## Expected funnel

For the full ~2,100-symbol EQ universe on hourly at defaults:

| stage | rally_cup | momentum_dip |
|---|---|---|
| raw detector hits | 5–20 | 5–15 |
| after context filters | 3–12 | 3–10 |
| after the visual pass | 1–5 | 1–4 |

The `rally_cup` numbers are **lower than this skill's original 30–50 raw**. The
shape and stability gates cut roughly five in six on a measured live batch, and
that is the intended trade: the visual pass changes from triage (mostly
V-bounces, find the base) to confirmation (mostly bases, find the flaw). Expect
genuine zero-hit days, and expect `shape_rejects.json` to be non-empty on most
of them.

If clean hits exceed ~30 on either screen, the thresholds are describing "went
up and paused" rather than a specific structure. If they're zero, run
`--diagnose` on that detector before concluding the market is quiet.
