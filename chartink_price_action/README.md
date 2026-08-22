# Chartink screener → hourly price-action analysis

Pipeline that takes a Chartink screener URL, resolves it to a stock list, pulls
real OHLCV, renders a candlestick chart for every hit, and hands the charts to
LLM analysts for 1-hour price-action judgement — followed by an adversarial
pass that tries to refute every buy call.

Run of 2026-08-22 against
[`monthly-rsi-60-6112092`](https://chartink.com/screener/monthly-rsi-60-6112092)
(107 stocks, data through Fri 21-Aug-2026 close).

## Pipeline

| Step | Script | What it does |
|---|---|---|
| 1 | *(inline curl)* | GET the screener page, parse `atlas_query` out of the embedded `scan-json`, POST it back to `/screener/process` with the CSRF token |
| 2 | `scripts/fetch_yahoo.py` | 6mo hourly + 1y daily bars per symbol |
| 3 | `scripts/metrics.py` | EMA stack, RSI, ADX/DI, ATR, pivots, volume ratios, daily extension |
| 4 | `scripts/render_charts.py` | 3-panel candlestick PNG per symbol (hourly + volume + daily) |
| 5 | `scripts/make_batches.py` | Splits metrics into per-analyst batches |
| 6 | *(agents)* | 9 analysts read the chart images; 5 skeptics refute the top calls |
| 7 | `scripts/build_report.py` | Renders the HTML report with charts embedded |

## Getting Yahoo data through the agent proxy

Two gotchas cost real time here, both recorded in `fetch_yahoo.py`:

- **`yfinance` does not work.** It uses `curl_cffi` with browser TLS
  impersonation, which the egress proxy resets (`curl: (35) Recv failure`).
  Plain `requests` against the v8 chart endpoint works fine.
- **Yahoo returns HTTP 429 without a session.** You need a cookie from
  `fc.yahoo.com` plus a crumb from `/v1/test/getcrumb`, then the crumb on every
  chart request. Without it every symbol 429s. With it, 107/107 succeeded.

## Data defects this run surfaced

Worth re-checking on any future run — two of these silently distort indicators:

- **09:15 bars report volume 0** in 2,512 of 3,078 sampled bars (81.6%). Every
  "Nx the 20-bar average volume" statistic is inflated because the denominator
  includes zero bars. Use daily volume as the denominator instead.
- **Split adjustment can corrupt one series.** TDPOWERSYS hourly is exactly
  2.000x its daily from 12-Aug (1:2 split applied to daily only). Chartink's
  official close matched the *hourly*, so the daily block was the bad one.
  `metrics.py` cross-checks hourly-derived daily closes against the daily series.
- **8 symbols end Friday at a 14:15 bar** rather than 15:15. This is a labelling
  artifact, not missing data — all 8 match Chartink's official close exactly.
  Three adversarial reviews wrongly treated it as a truncated session.

Cross-checking every close against Chartink's `close` field is the cheapest way
to settle all three; it costs one comparison and caught all of them.

## Output

`output/all_verdicts.json` — 107 entries, one per stock: setup classification,
grade, entry/stop/targets, volume read, red flags, invalidation.
`output/all_challenges.json` — 20 adversarial reviews with recomputed levels,
stop-vs-ATR, turnover, and overhead supply.
