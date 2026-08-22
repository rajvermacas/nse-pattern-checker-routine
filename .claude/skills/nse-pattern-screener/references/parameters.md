# Parameters and tuning

## The curvature scale (read this before touching thresholds)

The parabola `y = ax² + bx + c` is fit with x normalized to [-1, 1] and price
divided by its own mean. Under that normalization, for a symmetric cup with its
vertex at center:

    y(±1) − y(0) = a

so **`a` is approximately the cup's fractional depth** — but only for a cup
whose vertex sits at the centre. A 5% *centred* cup gives a ≈ 0.05.

Off-centre, the verified relation is:

    fractional depth ≈ a · (1 + |vertex_x|)²

At the admitted |vertex_x| ≤ 0.65 that is up to a 1.65² = **2.72× understatement**,
and it makes `a` unstable under the k-sweep: on one fixed 7%-deep cup, `a` runs
0.0121 → 0.0733 as k goes 12 → 28 (a 6× spread for the *same base*), while
`a·(1+|vx|)²` holds at 0.073 ±5%. So `a` is fine as the gate it has always
been, and wrong as a depth report or a ranking key — graded mode ranks on
`depth_from_fit_pct` instead. See "Graded mode" below.

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

Note also that **`min_r2` does nothing against drift**: the parabolic model
nests the linear term, so a pure straight line at any slope fits with
r2 = 1.000. R² measures absence of noise, not roundedness, and a high R² is not
evidence of a cup.

`vertex_x` deserves attention. It's where the parabola's minimum sits within the
normalized base. Near 0 means the turn happened mid-base — a real cup. Values
beyond ±1 mean the vertex is outside the window entirely, so the fit is a
one-directional curve, not a cup. Tightening `vertex_window` to about 0.4 is the
most direct numeric defense against V-bounces, at the cost of rejecting
legitimate asymmetric cups.

## Graded mode (`--preset`)

Without `--preset` nothing below applies and the screener behaves exactly as it
always has. With it, every gate becomes a 0-1 score on a soft ramp: full credit
past the ideal, partial credit through a tolerance band, zero beyond. The
ideals ARE the gated thresholds, so score 1.0 == "would have passed the old
gate", and `--preset strict` (band 0) reproduces the gated pipeline exactly.

The point is **recall**. The numeric stage should put 20-40 names in front of
the eye and let the chart do the rejecting; a binary verdict returning two
names is a worse tool even when both are right.

| Preset | tol | max_zero | min_composite | Shortlist on a 107-name universe |
|---|---|---|---|---|
| `strict` | 0.0 | 0 | 0.00 | 5 hourly / 6 daily — byte-identical to the gated run |
| `balanced` | 1.0 | 0 | 0.60 | 24 / 24 |
| `exploratory` | 2.0 | 1 | 0.82 | 37 / 32 |

- `tol` multiplies every band. 0 collapses the ramp back to a step function.
- `max_zero` — how many criteria may score exactly 0.0 and still be admitted.
- `min_composite` — floor on the weighted score. This is the knob that sets
  shortlist LENGTH; the bands set which *kinds* of near-miss get in.

Override any of them with `--tol`, `--max-zero`, `--min-composite`.

### Criteria, ideals and bands

Band is the 1x width; the score reaches 0.0 at `ideal ± band × tol`.

| Criterion | Ideal | Band (1x) | Weight | Group |
|---|---|---|---|---|
| `curvature` | `min_curvature` 0.015 | 0.007 | 0.6 | detector |
| `r2` | `min_r2` 0.45 | 0.12 | 0.5 | detector |
| `vertex` | `vertex_window` 0.65 | 0.55 | 1.2 | detector |
| `base_depth` | `base_max_depth` 0.10 | 0.05 | 1.0 | detector |
| `rally` | `min_rally` 0.10 | 0.04 | 0.8 | detector |
| `slope_ratio` | `min_slope_ratio` 1.5 | 0.80 | 0.5 | detector |
| `base_top` | `base_top_vs_rally_high` 0.97 | 0.04 | 1.0 | detector |
| `dist_from_lip` | `max_dist_from_high` 0.04 | 0.03 | 0.8 | detector |
| `ema_stack` | 1.0 (ratio) | 0.030 | 1.2 | detector |
| `vol_dryup` | `max_base_vol_ratio` 0.85 | 0.35 | 0.8 | detector |
| `bar_share` | `--max-bar-share` 0.50 | 0.30 | 1.0 | context |
| `turnover` | `--min-turnover-cr` 5.0 | 3.50 | 0.6 | context |
| `depth_fit` | 0.015 **to 0.060** | 0.007 / 0.040 | 1.2 | advisory |
| `centring` | 0.25 | 0.75 | 1.0 | advisory |
| `shape` | 1.0 | 1.00 | 1.5 | advisory |

**Detector** criteria are exactly `scan_symbol()`'s gate chain, so all ten at
1.0 == a raw hit; the JSON's `detector_pass_symbols` reproduces `hits.json`.
**Context** criteria are `postfilter.py`'s cuts, scored instead of deleting the
name. **Advisory** criteria never gate and are never counted as a miss — they
are always graded at 1x and only ever subtract from the composite ranking.

Two weights are deliberately low, for measured reasons:

- **`r2` is nearly worthless as shape evidence.** The parabolic model *nests*
  the linear term, so a pure straight line at any slope scores r2 = 1.000. R²
  measures absence of noise, not roundedness. Weighted 0.5, as a cleanliness
  term only.
- **raw `a` is the cup's fractional depth only when the vertex is CENTRED.**
  The verified relation is `depth ≈ a·(1+|vx|)²`. At the admitted |vx| ≤ 0.65
  raw `a` understates depth by up to 1.65² = 2.72×, and sweeping k moves `a` 6×
  on a fixed 7%-deep cup (0.0121 at k=12 to 0.0733 at k=28) while
  `a·(1+|vx|)²` holds at 0.073 ±5%. The raw-`a` gate is kept because strict
  must reproduce, but weighted down to 0.6; the vertex-corrected `depth_fit`
  carries the shape weight and is emitted as `depth_from_fit_pct`.

`depth_fit` is the only **sweet spot** criterion: full credit inside
[0.015, 0.060], ramping off on both sides. Deliberately non-monotone. A
monotone-in-depth reward is what drags the k-sweep onto the longest window
(the score-argmax lands on the longest k ~24% of the time vs ~5% expected)
and floats random walks up the ranking.

### Which window the k-sweep picks

`strict` breaks ties on the legacy `score`, i.e. whatever `scan_symbol()` would
have picked — including its known bias toward the longest, deepest qualifying
k, which disagrees with postfilter's shallowest-is-best ranking. Reproducing
today's output means reproducing today's bias.

Every other preset breaks ties on **the composite** — the same quantity the
shortlist is ranked by — so the chosen window and the ranking agree.

### Tiers

| Tier | Meaning |
|---|---|
| A | every gate at its ideal — would have passed strict today |
| B | misses exactly one gate, inside tolerance |
| C | everything else admitted |

Tier is strict-gate accounting, so **loosening can never produce a tier A**.
Rows carry a `costs` list and a `cost_summary` naming what took the points
("bar_share 0.57 vs 0.50"), so the list can be triaged before opening charts.

### What is NOT softened, and why

| Rule | Behaviour |
|---|---|
| `--min-pct-60d-high` | **Hard exclusion**, never scored. Moved to `hard_excluded` with its number attached. |
| `vertex` miss | Can never buy tier B; flagged `VERTEX_LOOSENED` and capped at C. |
| `curvature` ≤ 0, `vol_dryup` > ~1.5 | Never eligible for the preset's free failure. |

**The at-high test stays hard** because it is the one trap the eye cannot
correct for. A reviewer looking at a 120-bar window sees a clean rally into a
base; the 20% decline that preceded it, and the overhead supply the base is
sitting under, are off-screen (the ZEEL / HINDCOPPER case). Everything else in
this file is visible on the chart, so everything else is scored instead.

**`vertex_window` is the documented numeric defence against V-bounces**, so a
widened vertex band is precisely the loosening that would smuggle one in. It
still gets a band — the near-miss stays visible — but a vertex miss is capped
at tier C.

**`curvature` ≤ 0 is an inverted parabola.** A dome, not a loose cup. Likewise
`vol_dryup` past ~1.5 is base volume *expanding* against the rally, the
opposite of a dry-up. A zero there is the wrong shape, not a near-miss, so
neither may take the free failure. `bar_share` deliberately still can: a
one-candle leg is a real if different setup, so it is admitted with a
`GAP_DRIVEN` flag rather than deleted.

### The `shape` score — read the caveat

`shape` combines leg symmetry about the base low with a flat-shelf penalty
(bottom-third dwell above 0.55). It carries the largest single weight and it
**does not reliably separate a V from a cup.** Fitting an explicit two-segment
V model against the parabola and comparing residuals was tried on the labelled
batch and came out *backwards* — the kink-searched V fit PAYTM (a confirmed
cup) better than it fit BLISSGVS (a confirmed V-dip). SKILL.md is right that no
threshold separates these. `shape` merely correlates: the five
visually-confirmed names in the reference batch all measure ≥ 0.66 while most
of the visually-rejected ones measure lower. Good enough to RANK on, nowhere
near good enough to GATE on. Below 0.40 it raises `SHAPE_WEAK`.

### Noise floor

On pure random walks at NSE hourly volatility, **13.6% of 30-bar windows clear
all three fit gates** at current settings, and 1,654 of 5,000 random walks had
at least one qualifying k once the k-sweep is applied. At a 20-40 name
shortlist a substantial fraction WILL be noise. That is acceptable only
because a human looks at every chart, and only as long as noise does not
*outrank* real setups — which is what the sweet-spot `depth_fit`, the
`centring` penalty and the `shape` weight are there to prevent.

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
