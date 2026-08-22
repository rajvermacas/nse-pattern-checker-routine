# RSI-ranked rally-then-cup pass (no mechanical filters)

Run date: 2026-08-22. As-of bar: **2026-08-21**.

## What this run does

Deliberately **no mechanical pattern filter**. All 107 Chartink screener stocks are
ranked by daily Wilder RSI(14), the top 15 are plotted as daily candlestick charts,
and every one of those 15 is read **visually** for a rally-then-cup structure.

    107 stocks  ->  rank by daily RSI(14)  ->  top 15  ->  plot  ->  visual read

## Data normalisation (matters)

Yahoo's daily series lags the hourly by a session for roughly half the symbols
(53 of 107 ended 2026-08-20, 54 ended 2026-08-21). Ranking on the raw daily series
therefore compares stocks as of different dates. `daily_series.load_all()` rebuilds
the missing trailing daily bar by aggregating that date's hourly bars, with a scale
guard (>2% close mismatch on the last common day => rescale) for split-corrupted
series such as TDPOWERSYS.

The correction is not cosmetic. Un-patched, BANARISUG ranked #1 at RSI 90.5 and
HAPPYFORGE #2 at 90.3; both had a sharp down day on 08-21 that the stale daily
series had not yet recorded. Patched they fall to 74.0 and 74.4. The top-15
membership changes by three names.

TDPOWERSYS reads RSI 32.4 (last of 107) purely because its daily series carries an
uncorrected split step; every other symbol sits in 60-85, consistent with the
screen's own monthly-RSI>60 rule.

## Result

Grades from the visual pass: **0 A, 2 B, 8 C, 5 D**. See `results/visual_verdicts.txt`.

The reason is structural, not incidental. 14 of the 15 highest-RSI names printed
their 110-bar high within the last 7 bars. A cup is a *base* — it is what suppresses
RSI while it forms. Ranking by RSI descending therefore selects against the pattern
being looked for: it surfaces stocks that have already completed and left any base
behind. The single name with a real, still-live cup (APLAPOLLO) is also the only one
in the fifteen whose 110-bar high is old (88 bars back).

To surface cups, rank by *distance below* a prior high with RSI recovering, not by
RSI descending.

## Files

- `scripts/daily_series.py` — patched daily series loader, EMA, RSI
- `scripts/rank2.py` — ranks all 107 by daily RSI(14)
- `scripts/plot.py` — 4-panel daily charts (year / RSI / 110-bar zoom / volume)
- `scripts/context.py` — descriptive stats used to sanity-check the visual verdicts
- `scripts/sheet.py` — 15-chart contact sheet
- `scripts/annot.py` — annotated charts for the selected candidates (rally / base / rim / trigger / invalidation)
- `results/ranking.json` — all 107 ranked
- `results/visual_verdicts.txt` — the visual read of the top 15

## Selected candidates (annotated)

| | APLAPOLLO | BLISSGVS |
|---|---|---|
| rally | +45.8%, 114 bars | +212%, 104 bars |
| rim | 2301.40 (12 Feb) | 553.00 (30 Jun) |
| base low | 1736.00 (2 Jun), -24.6% | 447.20 (22 Jul), -19.1% |
| base length | 73 bars down / 58 up | 16 down / 22 up |
| position | right side, 7.1% below rim | broken out, 4.7% above rim |
| trigger | above 2175 (rim confirm 2301) | above 602.45 |
| invalidation | 1980 (dead below 1800) | 447 |

BLISSGVS's rim is 553, not the 602.45 printed on the unannotated chart — that dashed
line is the 110-bar high, which here is the 20 Aug spike, not the base's left rim.
