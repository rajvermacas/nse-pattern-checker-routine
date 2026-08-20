# Troubleshooting

## Zero hits

Run `python scripts/screener.py --parquet all_closed.parquet --diagnose` before
telling the user the market is quiet. It prints which gate rejected each symbol
plus the universe-wide distribution of curvature, R², and vertex position.

Common causes, in order of likelihood:

1. **`min_curvature` an order of magnitude too high.** Curvature ≈ fractional
   cup depth under the fit's normalization, so it lives around 0.005–0.04, not
   0.15. See `parameters.md`.
2. **EMA stack rejecting most of the universe.** In a weak tape, 350 of 500
   names failing `close > EMA20 > EMA50` is normal and correct — the setup
   requires an uptrend. Report it as a market observation rather than loosening.
3. **Thresholds stacked too tight.** Each gate is reasonable alone; six of them
   at p90 leaves nothing. Loosen one at a time and watch the funnel.

If you loosen anything to produce hits, **say so in the report**. A loosened
screener returning six names is not the same evidence as a strict one returning six.

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

Two shapes get through the numbers and need the visual pass:

**V-bounce.** Sharp decline, sharp recovery. Fits a parabola better than a real
cup does — R² can top the batch. Tell it by the base looking like a checkmark
rather than a saucer, and by the two halves having very different slopes.
Tightening `vertex_window` to ~0.4 helps; looking is what actually catches it.

**Drift with noise.** R² near the 0.45–0.55 floor, curvature barely over
threshold. Not really a base, just sideways chop that happens to fit. Treat
anything under R² 0.55 as unconfirmed until the chart says otherwise.

## Sanity checks before reporting

- Is the last bar a *closed* bar? (Market open → drop the newest one.)
- Does coverage match what you're claiming?
- Did you actually `view` the PNG, or only generate it?
- Is `stop_inside_base` true for most hits? (It usually is — say so.)
- Are you presenting candidates, or implying recommendations?
