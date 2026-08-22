# Backtesting the screen

Chartink does not hand you historical screen membership. It does not have to:
the scan clause is pure arithmetic on OHLCV, so membership can be **rebuilt from
bars** for any past date.

Validated against the live 2026-08-21 run, over 697 symbols with data:

| | |
|---|---|
| Recall | **92.0%** (92 of 100 Chartink hits reproduced) |
| Precision | **98.9%** (1 false positive in 597 non-hits) |

The 8 misses are RSI-boundary cases (monthly RSI 59.9 vs the 60 threshold) plus
TDPOWERSYS, whose daily series is split-corrupted. That is close enough to treat
reconstructed membership as ground truth.

## The one fix that mattered

Yahoo's daily series frequently lags the hourly by a session. Evaluating the
screen on a stale final bar cost **10 points of recall and 7 of precision**
(87.8% / 92.3% before, 97.6% / 100% after on the same subset). `engine.load()`
now rebuilds missing trailing daily sessions from the hourly bars.

## Scope and known biases

- **Universe**: 820 stocks with market cap > ₹5,000 cr, taken from Chartink so it
  matches the screen's own eligibility rule. 765 fetched, 697 with enough history.
- **Window**: ~3 years (Sep 2023 – Aug 2026). `range=730d` returns ~1,075 days of
  hourly bars; `range=2y` returns only 729. Use the former.
- **The 30-minute leg is dropped.** Yahoo serves 60 days of 30m bars. It is a
  near-duplicate of the 1-hour leg, but its absence makes this screen slightly
  *looser* than the real one.
- **Survivorship.** The universe is *today's* >₹5,000cr list. Names that fell out
  or delisted are absent, which biases returns upward.
- **Market cap is approximated** as today's shares outstanding × historical price;
  share-count changes are not modelled. 25 of 820 had no share count and are
  treated as always eligible.
- **Costs**: 0.30% round trip (STT 0.2 + brokerage/charges ~0.05 + slippage).

## Statistics

Screen entries cluster hard on market-wide up days, so trades are not independent.
Every t-statistic here is **clustered by signal date** — reduce to one mean excess
return per date, then test across dates. Per-trade t-stats on 11,606 overlapping
trades would call almost anything significant.

## Running it

```
python fetch_shares.py          # shares outstanding, for the market-cap leg
python fetch_universe_bars.py   # ~3y hourly + 5y daily -> bars/*.npz
python run_backtest.py          # layers 1 and 2 -> results.json, trades.json
python analyse.py               # stop survivability, regime, expectancy
python analyse2.py              # does selection rescue a tight stop?
```
