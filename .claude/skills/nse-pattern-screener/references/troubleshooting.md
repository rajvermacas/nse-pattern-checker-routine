# Troubleshooting

## Zero hits

Run the diagnostic for the detector that returned nothing — they are separate
scripts with separate gates:

```bash
python scripts/screener.py     --parquet all_closed.parquet --diagnose   # rally_cup
python scripts/momentum_dip.py --parquet all_closed.parquet --diagnose   # momentum_dip
```

Each prints which gate rejected each symbol plus the universe-wide distribution
of the metrics its thresholds sit on.

Common causes, in order of likelihood:

1. **`min_curvature` an order of magnitude too high.** Curvature ≈ fractional
   cup depth under the fit's normalization, so it lives around 0.005–0.04, not
   0.15. See `parameters.md`.
2. **EMA stack rejecting most of the universe.** In a weak tape, 350 of 500
   names failing `close > EMA20 > EMA50` is normal and correct — the setup
   requires an uptrend. Report it as a market observation rather than loosening.
3. **The shape gates ate the funnel.** `screener.py` writes every candidate
   that cleared all the legacy gates and died only on `vee_gain` /
   `bottom_frac` to `shape_rejects.json`, and `run_screener.sh` prints the
   count next to the raw hit count. A long shape-reject list beside zero
   survivors means the saucer-vs-checkmark thresholds are the constraint, not
   the market. Open the file: if the rejects sit at vee_gain 0.05-0.08 they are
   boundary calls worth reporting as marginals; if they sit at 0.3 they are
   real V-bounces and the screen is working.
4. **Thresholds stacked too tight.** Each gate is reasonable alone; eight of
   them at p90 leaves nothing. Loosen one at a time and watch the funnel.

If you loosen anything to produce hits, **say so in the report**. A loosened
screener returning six names is not the same evidence as a strict one returning six.

## Zero hits on momentum_dip specifically

The gate histogram is usually decisive here, because the rejections stack in a
fixed order. Read it top down:

- **`ema_not_stacked` dominating (50-60% of the universe)** — normal and
  correct. EMA20 under EMA50 means the stock is not in an advance, and this
  screen only buys dips inside advances. Report it as a market observation.
- **`advance_too_small` catching everything that got past the dip gates** —
  this is the failure mode `min_advance` was calibrated to avoid. See
  `parameters.md`: on hourly bars the universe's available advance runs p90 at
  about 10%, so a floor of 15% returns zero on every input while looking like a
  quiet market. On any other timeframe, re-read the `advance_pct` percentiles
  the diagnostic prints and set the floor near p90.
- **`dip_too_shallow` dominating** — genuinely quiet: strong names are not
  pulling back. Nothing to fix.
- **`not_stabilised` dominating** — things are falling and have not turned yet.
  That is the screen doing its job. `--no-stabilised` will produce hits, but
  they are falling knives by construction; it prints a warning, and any report
  built on it must repeat that warning.

## yfinance quirks

**Intraday history caps.** 1h and below: ~60 days. 1m: 7 days. Requesting more
returns a shorter frame without erroring. For longer intraday history the user
needs a broker feed (Kite, Dhan, Upstox).

**Coverage gaps.** Expect ~90–93% of the EQ list to return usable data. Recent
listings lack history; some NSE symbols don't map to `SYMBOL.NS` on Yahoo. Count
what actually came back (`df.symbol.nunique()`) and report that number, not the
universe size.

**Suspect volume.** yfinance NSE volume is occasionally stale or zero-filled. A
volume ratio below ~0.10 is more likely a data artifact than a genuine dry-up —
flag it rather than treating it as the strongest signal in the batch.

**Rate limits.** Batches above ~50 tickers start returning partial frames
silently. Stay at 40–50 with a 0.4s sleep. The retry loop in `fetch_data.py`
handles transient failures; persistent `FAIL batch N` lines mean back off.

**Adjusted vs raw.** `auto_adjust=False` keeps raw OHLC, which is what you want
for pattern geometry — adjustment retroactively rewrites price history around
corporate actions and distorts the shape.

## Timeouts

A full 2,300-symbol hourly fetch takes 15–40 minutes and will exceed most
command timeouts. This is expected. `fetch_data.py` writes per-batch parquets
and skips completed batches, so just run the same command again — 2–4
invocations is normal. Don't rewrite it as a single download.

## Zombie hits that survive every filter

Two shapes still get through the numbers on the cup screen and need the visual
pass. The shape gates catch roughly three V-bounces in four, not all of them:

**V-bounce.** Sharp decline, sharp recovery. Fits a parabola better than a real
cup does — R² can top the batch. Tell it by the base looking like a checkmark
rather than a saucer, and by the two halves having very different slopes.
Tightening `vertex_window` to ~0.4 helps; looking is what actually catches it.

**Drift with noise.** R² near the 0.45-0.55 floor, curvature barely over
threshold. Not really a base, just sideways chop that happens to fit. Treat
anything under R² 0.55 as unconfirmed until the chart says otherwise.
`k_pass` is the fast tell: drift usually fits at one or two window lengths, a
real base at three to eight.

On the dip screen the zombie is different: **a pullback that is really a top.**
Every gate can pass while the stock is rolling over — the advance is real, the
dip is shallow so far, and one up-bar satisfies the trigger. What the numbers
cannot see is that the advance's own momentum has been fading for days. Check
the panel for a sequence of lower highs before the swing high, and for the dip's
volume being lower only because the whole tape is thinner.

## Detector changes that did not break anything (and one that did)

If a run behaves oddly after a code change, these are the moving parts:

- **EMAs are computed on the full symbol history**, then sliced, by
  `indicators.ema` — not on the 120-bar detector window or the 110-bar plot
  window. That is why the chart's EMA50 and the gate's EMA50 are now the same
  line. Anything that recomputes an EMA on a slice reintroduces the mismatch.
- **The rally leg is measured close-to-close.** It used to take the low from
  closes and the high from `high`, which mixed two series and inflated every
  rally by a wick. Rallies now read slightly smaller than they used to; that is
  the fix, not a regression.
- **`screener.py` always writes its JSON**, including `[]` for a zero-hit run.
  It previously returned early without writing, so a stale `hits.json` from an
  earlier run in the same `work/` directory could be counted as today's.
- **The one that did break something:** the dip screen's first EMA50 test used
  the dip's *low*. A pullback that wicks through a rising EMA50 is the classic
  entry, so that gate rejected exactly the setups the screen exists to find. It
  now tests dip *closes* with a 2% slack, plus requiring the entry bar to close
  back above the line.

## Verifying a change without waiting for a market

```bash
python scripts/selftest_patterns.py
```

Builds synthetic bars whose shapes are known — a rounded base, a V-bounce, a
downtrend, an orderly dip, a falling knife, a one-candle gap-down — pushes them
through the real detectors and asserts on what comes out. No network, no market,
deterministic, a few seconds. Run it after touching any threshold or detector:
a screener's failure mode is silence, and this is the only check that fails
loudly instead.

## Sanity checks before reporting

- Is the last bar a *closed* bar? (Market open → drop the newest one.)
- Does coverage match what you're claiming?
- Did you actually `view` **both** PNGs, or only generate them?
- Is `stop_inside_base` true for most hits? (It usually is — say so.)
- Did you check `shape_rejects.json` before calling a thin cup list a quiet market?
- Are the two patterns' shortlists reported separately, with their RRRs never
  compared against each other?
- Are you presenting candidates, or implying recommendations?
