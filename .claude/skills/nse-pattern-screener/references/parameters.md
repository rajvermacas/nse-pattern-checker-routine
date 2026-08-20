# Parameters and tuning

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

## Detector parameters

| Param | Default | Raise it to... | Lower it to... |
|---|---|---|---|
| `base_min` | 12 | demand a longer, more developed base | catch quick pauses |
| `base_max` | 30 | allow multi-week bases | keep bases tight |
| `base_max_depth` | 0.10 | tolerate deeper pullbacks | insist the base is shallow |
| `min_curvature` | 0.015 | demand pronounced rounding | catch flatter bases (more noise) |
| `min_r2` | 0.45 | demand a clean fit | let ragged bases through |
| `vertex_window` | 0.65 | allow off-center turns | force the turn mid-base |
| `min_rally` | 0.10 | require a bigger prior move | catch smaller setups |
| `rally_max_bars` | 45 | look further back for the leg | require a recent, tight rally |
| `min_slope_ratio` | 1.5 | demand the rally clearly outpace the base | allow gentler contrast |
| `base_top_vs_rally_high` | 0.97 | force the base right at the high | allow a deeper pullback |
| `max_dist_from_high` | 0.04 | catch names further from the lip | only names about to break out |
| `max_base_vol_ratio` | 0.85 | ignore volume | demand a real dry-up |
| `lookback` | 120 | more context per symbol | faster, more myopic |

`vertex_x` deserves attention. It's where the parabola's minimum sits within the
normalized base. Near 0 means the turn happened mid-base — a real cup. Values
beyond ±1 mean the vertex is outside the window entirely, so the fit is a
one-directional curve, not a cup. Tightening `vertex_window` to about 0.4 is the
most direct numeric defense against V-bounces, at the cost of rejecting
legitimate asymmetric cups.

## Context filter parameters

| Param | Default | Note |
|---|---|---|
| `--min-turnover` | 5.0 (₹ cr/day) | ~1,200–1,500 NSE names clear ₹5cr. Raise to 20 for a large-cap-only scan |
| `--min-pct-60d-high` | 97.0 | how close the base high must be to the true 60-day high |
| `--max-bar-share` | 0.5 | max fraction of the rally from any single bar |
| `--bars-per-day` | 7 | NSE hourly. Use 25 for 15-minute, 1 for daily |
| `--target-pct` | 0.15 | profit target off the lip; the RRR numerator |

## Ranking

Clean hits are sorted by `rrr_structural = target_pct / base_depth_pct`.

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

## Timeframe notes

NSE hourly bars: 09:15, 10:15, ... 15:15, where the last is a 15-minute stub —
about **7 bars per trading day**. Translate for the user: a 21-bar base is
roughly three sessions.

For 15-minute bars, scale bar counts by ~3.5 (`base_min` 40, `rally_max_bars`
150) and set `--bars-per-day 25`. yfinance gives ~60 days of 15m.

For daily bars, `base_min` 10, `base_max` 40, `rally_max_bars` 60,
`--bars-per-day 1`, and `--period 2y` since the 60-day intraday cap doesn't apply.

## Expected funnel

For the full ~2,100-symbol EQ universe on hourly at defaults:

- raw detector hits: 30–50
- after context filters: 10–15
- clean structural matches after the visual pass: 3–6

If clean hits exceed ~30, the thresholds are describing "went up and paused"
rather than a specific structure. If they're zero, run `--diagnose` before
concluding the market is quiet.
