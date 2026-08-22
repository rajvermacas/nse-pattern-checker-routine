---
name: nse-pattern-screener
description: Screen the full NSE equity universe for chart patterns on intraday or daily timeframes using real market data — fetch the official NSE symbol list, pull OHLCV from yfinance, detect geometric patterns (rally-then-cup, rounded base, flat base, breakout consolidation, and pullbacks in strong momentum names) with a least-squares parabola fit and shape discrimination, filter out false positives, and render candlestick charts to visually verify every hit. Use this skill whenever the user asks to scan, screen, or find NSE/Indian stocks matching a chart pattern or setup — including when they paste or describe a TradingView screenshot and ask "find stocks like this", ask about cup-and-handle / rounded bases / consolidation near highs, ask for stocks to buy on dips or pullbacks / momentum names that have retraced / "strong stocks that pulled back to the 20 EMA", mention hourly or 15-minute screening of Nifty 500 or all NSE stocks, or want a shortlist of candidates with entry and stop levels. Also use it when they want to modify, re-run, or re-tune a screener built this way.
---

# NSE Pattern Screener

Build and run pattern screeners over the real NSE universe, then **look at the charts before reporting anything**.

The screener produces a number; the chart tells you whether the number means what you think. Most of the value in this skill is in the filters and the visual check, not in the pattern math — the math is twenty lines and it will happily match a V-shaped bounce, a gap-up, or a dead-cat rally into resistance.

Two detectors ship here, and they are different trades rather than variants of one:

| | `rally_cup` (`screener.py`) | `momentum_dip` (`momentum_dip.py`) |
|---|---|---|
| what it finds | a rally into a rounded base near the highs | a shallow, orderly pullback inside an advance |
| when you buy | the breakout above the lip of a **finished** base | **inside** an unfinished move, while price is still below the swing high |
| the entry | `base_high` (a level to trade through) | the last close, or above the reversal bar's high |
| the stop | the base low, 4–8% away | the dip low, 1–3% away |
| what kills it | the base was a V-bounce all along | the dip was the start of a top |
| you are paid for | patience | precision |

Run both. Report them as two lists. Their ranking numbers are not on the same scale — see "The two RRRs are not comparable" in step 7.

## Workflow

Steps 1–3 are plumbing, 4 is the detector, 5–6 are where false positives die.
The funnel is roughly 350:1 end to end. Two checkpoints — dropping the partial
bar, and actually viewing the PNG — produce output that *looks* fine when
skipped, so neither is optional.

```
  "find NSE stocks with a rally + cup on hourly"   │  [TradingView screenshot]
                              ▼
┌─ ① UNIVERSE ─────────────────────────── fetch_universe.py ──────────────────┐
│   NSE archives → EQUITY_L.csv                                               │
│     EQ ~2293  rolling settlement   ✔ DEFAULT — scan all of it               │
│     BE  ~232  trade-to-trade       ✘ no intraday                            │
│     BZ   ~28  surveillance         ✘ suspended                              │
│   narrow ONLY if asked: --index nifty500 / nifty200 (or when testing code)  │
└──────────────────────────────── universe.txt ───────────────────────────────┘
                              ▼
┌─ ② FETCH ⟲ RESUMABLE ──────────────────── fetch_data.py ────────────────────┐
│   symbols ─chunk 40─► yfinance ─► parts/pNNNNN.parquet                      │
│                 ▲                                                           │
│                 └── part exists? → SKIP    ← why timeouts are survivable    │
│   ⚠ 15–40 min full EQ; WILL exceed timeout → rerun SAME command 2–4×        │
│   ⚠ yfinance caps: 1h ≤ 60d │ 1m ≤ 7d                                       │
│   ⚠ coverage ≈ 92% (2110/2293) ← report it, don't imply a full scan         │
└──────────────────────────────── all.parquet ────────────────────────────────┘
                              ▼
┌─ ③ DROP IN-PROGRESS BAR ────────────────────────────────────────────────────┐
│   09:15 10:15 11:15 12:15 13:15 14:15 15:15(stub)   ≈ 7 bars/day            │
│    ███   ███   ███   ███   ███   ███   ▒▒▒ ← partial: its close is NOT      │
│                                              a close.  ✘ DROP IT            │
└───────────────────── all_closed.parquet (state the ts) ─────────────────────┘
                              ▼
┌─ ④ DETECT ── rally_cup ───────────────────── screener.py ───────────────────┐
│   price ÷ mean, x ∈ [-1,1]     fit  y = ax² + bx + c                        │
│      ╲   rally       ╭─╮ ← base (k bars)     a  ≈ FRACTIONAL DEPTH          │
│       ╲    leg     ╭─╯ ╰──╮                  r² = fit quality               │
│        ╲__       ╱         ╰╮                vx = where the turn sits       │
│           ╲_____╱                                                           │
│  ┌───────────────────────────────────────────────────────────────┐          │
│  │ ⚠⚠ CALIBRATION TRAP: 5% cup → a ≈ 0.05. Universe p99 ≈ 0.043. │          │
│  │    min_curvature 0.015 ✔ │ 0.15 ✘ → ZERO HITS ON EVERY INPUT. │          │
│  │    Fails silently. Looks like "quiet market", is a bug.       │          │
│  └───────────────────────────────────────────────────────────────┘          │
│   gates (first failure wins, counted by --diagnose):                        │
│   EMA stack ─┬─ EMA rising ─┬─ depth ≤10% ─┬─ a ≥.015 ─┬─ r² ≥.45           │
│   |vx| ≤.65 ─┼─ rally ≥10% ─┼─ at-top ─────┼─ lip ≤4% ─┼─ vol ≤.85          │
│   dd ≤½ leg ─┴─ SHAPE: vee_gain ≤.05 ─┴─ btm_frac ≥.30 ─┴─ k_pass ≥2        │
│   (EMA stack is usually the biggest cut — correct: the setup needs trend)   │
│   SHAPE is the numeric half of ⑥ and cuts ~5 in 6. What it cut goes to      │
│   shape_rejects.json — read that before believing a quiet day.              │
└─────────────────────── hits.json      ~2100 ──► ~10 ────────────────────────┘
        ── ④ and ④b are PARALLEL passes over the same all_closed.parquet ──
        ── two different trades, two shortlists, never one merged table ──
┌─ ④b DETECT ── momentum_dip ───────────── momentum_dip.py ───────────────────┐
│   buy the pullback, not the breakout — entry sits INSIDE a live move        │
│        swing high ●                                                         │
│                  ╱ ╲          ← dip 3–12%, ≤15 bars, orderly, quiet         │
│    advance ≥10% ╱   ╲   ●     ← last bar closes UP, off its low             │
│                ╱     ╲ ╱                                                    │
│     ──────────╱       ●       ← dip low = THE STOP, EMA50 under it          │
│   gates: EMA20>EMA50 ─┬─ EMA50 rising ─┬─ advance ≥10% ─┬─ dip 3–12%        │
│   retrace ≤50% of leg ─┼─ no candle >60% of the fall ─┼─ vol ≤ leg's        │
│   closes hold EMA50 ───┴─ stabilised ─────────────────┴─ ≤80% recovered     │
│  ┌───────────────────────────────────────────────────────────────┐          │
│  │ ⚠ THE FAILURE MODE IS A FALLING KNIFE. `stabilised` is the    │          │
│  │   gate that prevents it: the last bar must close up, off the  │          │
│  │   low, and not be the low. --no-stabilised removes it and     │          │
│  │   returns whatever is dropping fastest. Say so if you use it. │          │
│  └───────────────────────────────────────────────────────────────┘          │
└─────────────────────── dip_hits.json  ~2100 ──► ~10 ────────────────────────┘
                              ▼
┌─ ⑤ CONTEXT FILTERS ─────────────────────── postfilter.py ───────────────────┐
│   pattern-agnostic: reads canonical keys, so BOTH screens use these         │
│                                                                             │
│   turnover ≥ ₹5cr/day    → thin names: pretty geometry, unfillable entry    │
│                                                                             │
│   base_high ≥ 97% of     → caught ZEEL: a 20% FALL then a bounce reads      │
│   60d high                 as "rally + base near the WINDOW high" — but     │
│                            it's a downtrend bounce into overhead supply     │
│                                                                             │
│   max_bar_share ≤ 0.5    → caught ASTRAL: one gap candle = 64% of the       │
│         ┃                  move. gap-and-base ≠ rally-and-base:             │
│    _____┃╭────╮            different setup, different odds                  │
└──── *_clean.json  ~10 ──► ~5 each, ranked by RRR (NOT comparable across) ───┘
                              ▼
┌─ ⑥ PLOT ── then VIEW ── ★ MANDATORY ────── plot_hits.py → view(png) ────────┐
│   a V-bounce fits a parabola BETTER than a real cup:                        │
│                                                                             │
│      REAL BASE               V-BOUNCE (SUDARSCHEM r²=.85 — best fit in      │
│        ╭───╮ saucer                   the entire batch, and worthless)      │
│      ╭─╯   ╰─╮                    ╲    ╱  checkmark                         │
│     ╱ r²=.78  ╲                    ╲  ╱                                     │
│                                     ╲╱                                      │
│     ✔ rounds, symmetric        ✘ two halves, different slopes               │
│                                                                             │
│   No threshold reliably separates these. LOOKING does.                      │
│   Per panel: rally sustained or one candle? base ROUNDS or V/wedge/shelf?   │
│              EMAs run UNDER it and rise through? supply to the left?        │
└──── BOTH pngs: hits.png + dip_hits.png ──► 1–5 trustworthy each ────────────┘
                              ▼
┌─ ⑦ REPORT ──────────────────────────────────────────────────────────────────┐
│   1 coverage + last closed bar ts   2 funnel, naming what each filter cut   │
│   3 table   4 TIERS from the visual pass, incl. names you distrust that     │
│   PASSED   5 risk reality check ↓                                           │
│  ┌───────────────────────────────────────────────────────────────┐          │
│  │ STOP-INSIDE-BASE:  entry 245.29 ═══ lip                       │          │
│  │                    3% sl 237.93  ← mid-cup, dies to chop      │          │
│  │                    base_low 229.05 ← real stop = 6.6%         │          │
│  │ Bases run 4–8% deep, so a 3% stop is almost never compatible. │          │
│  └───────────────────────────────────────────────────────────────┘          │
│   candidates, NOT recommendations. say so if a threshold was loosened.      │
└─────────────────────────────────────────────────────────────────────────────┘

  ZERO HITS? → screener.py --diagnose BEFORE saying "quiet market"
               ├ per-gate rejection histogram
               └ universe p50/75/90/95/99 for a, r², |vx|
                 → is your threshold above p99? that's the bug, not the market.
```

## Setup

```bash
pip install yfinance polars pandas pyarrow numpy matplotlib --break-system-packages -q
```

## Step 1 — Universe

NSE publishes the authoritative equity list. Never hardcode a symbol list or rely on a blog's count.

**Default to the full EQ universe.** When the user asks for an NSE scan without naming a universe, run the whole ~2,293-symbol EQ list — don't narrow to an index to save time, and don't ask which universe to use. Tell them up front that the fetch takes roughly 30 minutes and runs across several invocations, then get on with it.

```bash
python scripts/fetch_universe.py --series EQ --out universe.txt
```

Series matters for what's tradable:
- **EQ** (~2,293) — normal rolling settlement. The only series worth screening for intraday patterns.
- **BE** (~232) — trade-to-trade, delivery only. No intraday, so hourly patterns aren't actionable.
- **BZ** (~28) — surveillance/suspended. Skip.

Narrow only when the user asks for it — `--index nifty500`, `--index nifty200`, `--index midcap150`, etc. A smaller index is also the right choice when testing a change to the detector or filters, where a 5-minute fetch beats a 30-minute one and the exact hit list doesn't matter yet.

## Step 2 — Fetch data

yfinance caps intraday history: **1h and below is limited to ~60 days**, 1m to 7. If the user wants more history they need daily bars or a broker feed (Kite, Dhan, Upstox).

```bash
python scripts/fetch_data.py --universe universe.txt --period 60d --interval 1h --out-dir parts
```

The fetch **must be resumable**. A full 2,300-symbol pull takes 15–40 minutes and will exceed most single-command timeouts. The script writes one parquet per batch to `parts/` and skips batches already on disk, so re-running the same command continues where it stopped. Expect to invoke it 2–4 times. Don't rewrite this as a single monolithic download.

Batch at 40–50 tickers with a short sleep. Larger batches hit rate limits and silently return partial frames.

Then merge:

```bash
python scripts/fetch_data.py --merge parts --out all.parquet
```

**Expect coverage gaps.** A recent run returned usable data for 2,110 of 2,293 EQ symbols — recent listings lack 60 days of history, and some NSE symbols don't map cleanly to `SYMBOL.NS` on Yahoo. Always report actual coverage rather than implying a complete scan.

## Step 3 — Drop the in-progress bar

If the market is open, the newest bar is partial. Its close is not a close, and every "distance from the lip" and volume calculation built on it is wrong.

```bash
python -c "
import polars as pl
df = pl.read_parquet('all.parquet'); mx = df['ts'].max()
df.filter(pl.col('ts') < mx).write_parquet('all_closed.parquet')
print('last closed bar:', pl.read_parquet('all_closed.parquet')['ts'].max())
"
```

Always state the timestamp of the last closed bar in the final report. NSE hourly bars run 09:15, 10:15, ... 15:15, where the last is a 15-minute stub — roughly 7 bars per trading day. Useful for translating "20-bar base" into "about three sessions."

## Step 4 — The rally_cup detector

```bash
python scripts/screener.py --parquet all_closed.parquet --json hits.json \
    --shape-rejects shape_rejects.json
```

The core is a least-squares fit of `y = ax² + bx + c` over the base window, with x normalized to [-1, 1] and price divided by its own mean.

**The critical calibration:** with that normalization, `a` comes out approximately equal to the cup's *fractional depth*. A 5% cup gives a ≈ 0.05. Across the whole NSE universe the 99th percentile of `a` is about 0.043. So the threshold belongs near **0.015**, not 0.15 — an order-of-magnitude error here silently returns zero matches on every input, which looks like "no setups today" rather than a bug.

### Telling a saucer from a checkmark, numerically

Curvature and R² cannot do it — a V-bounce fits the parabola *better* than a real cup. Two extra metrics can, and both are gated:

- **`vee_gain`** — fit the base twice, once with the parabola and once with the best two-straight-line "V", and compare their errors. Negative means the curve wins (a saucer); positive means two straight legs win (a checkmark). Rejected above **0.05**.
- **`bottom_frac`** — share of the base's closes in the lower third of its range. A parabola loiters at the bottom (~0.58); straight legs pass straight through it (~0.33). Rejected below **0.30**.

Measured on synthetic bases at realistic hourly noise, `vee_gain > 0.05` removes about 80% of symmetric V-bounces and 68% of asymmetric ones, at a cost of about 10% of genuine cups. On a live nifty500 session it cut 5 of 6 raw hits, and reading the charts afterwards confirmed four were plainly V-bounces or one-gap "rallies"; one was a boundary call and the survivor was the best chart in the batch.

**Everything the shape test cuts is written to `--shape-rejects`.** That file is what makes a too-tight threshold visible instead of silent: a long reject list next to zero survivors means the shape gates are the constraint, not the market. `run_screener.sh` prints the count on every run.

Two more gates address problems that are not about shape:

- **`min_k_stability`** (default 2) — the detector tries 19 window lengths and keeps the best-scoring one, so every symbol gets 19 chances to fit. `k_pass` counts how many windows *actually* passed. One passing window out of nineteen is a multiple-comparisons artifact; genuine bases score 3–8.
- **`max_rally_dd_share`** (default 0.5) — rejects a leg that gave back more than half its own gain mid-way. Low-to-high measurement cannot see that shape: a spike and its retracement read as one clean rally.

If a run returns zero hits, don't assume the market is quiet. Run the diagnostic to see which filter is eating everything:

```bash
python scripts/screener.py --parquet all_closed.parquet --diagnose
```

It prints a per-filter rejection histogram, the shape-rejects that cleared every other gate, and the actual percentile distribution of curvature, R², vertex position, `vee_gain` and `bottom_frac` across the universe — which tells you where your thresholds sit relative to reality.

Parameters worth knowing (all overridable on the CLI, full list in `references/parameters.md`):

| Param | Default | Meaning |
|---|---|---|
| `min_curvature` | 0.015 | ≈ minimum fractional cup depth |
| `min_r2` | 0.45 | fit quality; below ~0.5 the "base" is usually drift plus noise |
| `vertex_window` | 0.65 | where the turn happens within the base |
| `max_vee_gain` | 0.05 | reject above: the base fits two straight lines better than a curve |
| `min_bottom_frac` | 0.30 | reject below: the base never loiters at its low |
| `min_k_stability` | 2 | window lengths that must independently agree |
| `min_rally` | 0.10 | rally leg size, close to close |
| `max_rally_dd_share` | 0.5 | deepest give-back inside the leg, as a share of the leg |
| `base_max_depth` | 0.10 | shallow base = healthy; deep = a correction |
| `max_dist_from_high` | 0.04 | how close price must sit to the lip |

## Step 4b — The momentum_dip detector

```bash
python scripts/momentum_dip.py --parquet all_closed.parquet --json dip_hits.json
```

Same plumbing, opposite timing. `rally_cup` waits for a base to finish and buys the breakout; this buys *into* a pullback that is still open. That is a better price and a worse confirmation, so every gate answers one of two questions: **is the trend still intact**, and **has the fall actually stopped?**

Is the trend intact:

- EMA20 above EMA50, EMA50 higher than it was 30 bars ago
- an advance of ≥10% close-to-close into the swing high, over ≥8 bars
- the swing high must *be* the window's high — not a lower high in a rollover
- the dip retraces ≤50% of that advance — deeper than half is a trend change, not a pause
- dip closes hold within 2% of the rising EMA50, and the entry bar closes back above it

Has the fall stopped:

- the last bar is not the low of the dip, and
- it closes above the prior bar's high, **or** closes up and in the top half of its own range, **or** reclaims EMA20 after dipping under it
- price has not already recovered more than 80% of the dip — at that point it is a breakout, not a dip

Deliberately **not** required: `close > EMA20`. The premise is that price has fallen back into the fast average; requiring it to stay above would only return names that never dipped.

**The failure mode is a falling knife**, and three gates exist specifically to prevent it: `max_retrace`, `max_dip_bar_share` (one candle doing most of the damage is news, and news does not respect chart structure), and the stabilisation trigger. `--no-stabilised` removes the last one — it is a diagnostic tool, it prints a warning, and any report built on it must repeat that warning.

`min_advance` is the gate most likely to empty this screen, and it was calibrated rather than guessed: at 0.15, 39 candidates on a live nifty500 session reached it and none passed. The universe's available advance runs p90 ≈ 10% on hourly bars, so the floor sits at **0.10**, below which it stops binding at all. On any other timeframe, read the `advance_pct` percentiles from `--diagnose` and re-set it near p90.

Beyond the levels, each hit carries the context the eye would otherwise have to reconstruct: `retrace_of_advance`, `dip_vol_ratio`, `recovered_frac`, `rsi` and `rsi_at_dip_low`, `trigger` (which stabilisation condition fired), `touched_ema_fast`, and `risk_pct_buffered` — the risk to half an ATR *below* the dip low, which is what a stop has to be to survive ordinary noise.

## Step 5 — Context filters

The detector sees a window. These filters supply the context it lacks, and they are the difference between a usable shortlist and a list of things that merely curve.

```bash
python scripts/postfilter.py --hits hits.json     --parquet all_closed.parquet --out hits_clean.json
python scripts/postfilter.py --hits dip_hits.json --parquet all_closed.parquet --out dip_hits_clean.json
```

One script, both patterns. It reads only four canonical keys that every detector emits — `pattern_bars`, `leg_bars`, `struct_high`, `risk_pct` — so adding a pattern never means forking the context filters. That matters because the context filters, not the pattern math, are what decide whether a shortlist is usable.

Three checks, each earned from a real false positive:

**Liquidity** (`--min-turnover 5`, ₹ crore/day). Thin names produce beautiful geometry and unfillable entries. The volume dry-up ratio is also meaningless when the denominator is noise.

**Is it actually at a high?** (`--min-pct-60d-high 97`) The detector's lookback is ~120 bars. A stock that fell 20% and bounced will show a "rally" and a base near the *window* high while sitting far below the real one. This is what a downtrend bounce into supply looks like to a short-window detector — the check compares the base high against the full 60-day high.

**Rally participation** (`--max-bar-share 0.5`) The rally is measured low-to-high, so a single gap-up candle registers as a multi-bar rally. This rejects any leg where one bar contributed more than half the move. A gap-and-base is a different setup with different odds than a rally-and-base, and shouldn't be silently mixed in.

A healthy funnel is roughly 2,000 symbols → 5–20 raw hits → 3–12 clean, per pattern. (The cup screen's raw count used to be 30–50; the shape and stability gates cut roughly five in six, deliberately.) If you're getting 80+ clean hits, the thresholds are describing "went up and paused" rather than a specific structure.

### Ranking: structural RRR

The clean list comes out sorted by **structural reward-to-risk**, not by the detector's internal score:

```
rrr_structural = target_pct / risk_pct              (default target 15%)

  rally_cup:    entry = base_high (the lip)   risk = entry → base_low
  momentum_dip: entry = the last close        risk = entry → dip_low
```

For the cup this reduces to inverse base depth, which looks crude but is the right criterion: base depth *is* the risk, because the base low is the only stop the structure supports. So this single number ties the geometry to position sizing, which nothing else in the output does. Override the numerator with `--target-pct` if the user's target differs from 15%.

**The two patterns' RRRs are not comparable.** A dip entry sits 1–3% above its stop, so its RRR lands around 5–15 against the cup's 2–5. That is arithmetic, not edge — and the tighter stop is also the likelier stop, because the entry is inside a move that has not finished. Rank within a pattern; never merge the two lists into one sorted table. `postfilter.py` prints this warning itself whenever it processes dip hits.

Other plausible rankers — proximity to the lip, volume dry-up, fit quality, rally strength — mostly correlate with depth anyway. A weighted composite of all five was tested against pure RRR on a live batch and disagreed by an average of 1.7 places, agreeing on both the top and bottom name. The added complexity bought nothing, so rank on RRR and report the other columns alongside for context.

**RRR ranks the geometry, not the odds.** It states what a trade pays if it works and is silent on how often it works. A 4.85 RRR at a 20% hit rate is worse than 2.0 at 50%. Never present the top-ranked name as most likely to succeed, and never present the ordering as a buy list. Only a backtest establishes hit rate — see the regime note in step 7.

## Step 6 — Plot and actually look

Non-negotiable. Render the survivors and open the PNG with the `view` tool.

```bash
python scripts/plot_hits.py --hits hits_clean.json     --parquet all_closed.parquet --out hits.png
python scripts/plot_hits.py --hits dip_hits_clean.json --parquet all_closed.parquet --out dip_hits.png
```

Then `view` **both** files. Read the panels before writing a word of the report.

The plotter draws what each pattern's judgement actually needs. A cup panel overlays *both* competing models on the base — a solid curve for the parabola, a dashed line for the best two-segment V — so "is this round or is this a bounce" becomes something you can see rather than infer. A dip panel instead shades the advance and the dip separately and draws three levels: the swing high being retraced, the dip low that is the stop, and the entry.

The EMAs on the chart are computed by the same function, on the same full history, as the ones the detector gated on. They used to be computed on the plot's own 110-bar slice, so the line you checked was not quite the line that decided.

**Why this step exists:** a V-shaped reversal fits a parabola *beautifully* — often better than a genuine rounded base. In one run the highest-R² name in the batch (0.85) was a stock that had rolled over into a real decline and snapped back. Curvature cannot distinguish "rounded" from "sharp reversal"; only vertex position hints at it, and the default window is loose enough to let it through. There is no numeric fix that reliably catches this. Looking does.

What to check in each `rally_cup` panel:
- Is the rally *sustained*, or one candle plus drift?
- Does the base **round**, or is it a V, a descending wedge, or a flat shelf? Where the dashed V hugs the candles more tightly than the curve, distrust it even though it passed.
- Do the fast EMAs run *under* the base and rise through it?
- Is the base near the panel's high, or is there overhead supply to the left?

What to check in each `momentum_dip` panel — different questions, because you are buying an unfinished move:
- Is the advance a real trend, or one gap and a drift?
- Is the dip *orderly* — a stair-step down — or a cliff with one huge candle?
- Are the highs before the swing high already rolling over? A pullback inside a topping pattern passes every gate here.
- Does the last bar genuinely turn, or is the trigger one small up-close inside a downtrend?
- Is the dip low a stop you could actually carry? At 1–3% it will be tested by ordinary noise.

The charts are matplotlib renderings of the yfinance data, not screenshots from any platform. EMA seeding and session handling differ from TradingView and Kite, so treat them as shape verification and tell the user to confirm prices on their own platform before acting.

## Step 7 — Report

Structure the answer as:

1. **Coverage** — symbols with usable data out of the universe, and the last closed bar timestamp
2. **Funnel, per pattern** — raw hits → clean hits, and what the filters removed by name. For `rally_cup`, include the shape-reject count and name any reject that sat within ~0.02 of the `vee_gain` threshold: those are boundary calls the reader deserves to see.
3. **Two tables, never merged** — each ranked by `rrr_structural` descending within its own pattern. For `rally_cup`: depth, risk-to-base-low, distance from lip, volume ratio, R², `vee_gain`, `k_pass`, turnover. For `momentum_dip`: advance, dip depth, retrace, `dip_vol_ratio`, `recovered_frac`, RSI, trigger, `risk_pct` and `risk_pct_buffered`.
4. **Tiers from the visual pass** — which are clean structural matches, which are marginal, which you'd distrust and why. Do this per pattern; the disqualifying flaws are different.
5. **Risk reality check** (below)

### The stop-inside-base problem

Always compute this and always surface it. A fixed-percentage stop (say 3% off the lip) lands *inside* any base deeper than 3% — and most qualifying bases are 4–8% deep. Such a stop sits mid-cup and gets taken out by ordinary chop without the pattern having failed at all.

Report `risk_pct_to_base_low` alongside the fixed stop so the user can see the real structural risk. On a 6.6% base, honoring the structure means 6.6% risk, which roughly halves position size versus the 3% assumption and changes the whole reward/risk calculation. Never present a fixed-% stop as if it were compatible with the pattern when it isn't.

**The dip screen has the mirror-image problem.** Its structural stop is 1–3% away, so a fixed 3% stop is usually *wider* than the structure rather than inside it — and the tight stop is the danger, not the comfort. The dip low is the most-tested price in the setup; a stop sitting exactly on it is the one most likely to be taken out by a wick that does not break the pattern. Quote `risk_pct_buffered` (half an ATR below the dip low) as the risk a real position carries, and say plainly that the resulting RRR is far below the headline number.

### Regime dependence

Say this once, without belaboring it: bases near highs resolve upward far more often in a trending index than a choppy one. The same screener on the same universe has a very different hit rate in the two. Presence of a pattern today is a different question from whether it's worth trading today, and only a backtest split by index trend state answers the second.

## Adapting to other patterns

`momentum_dip.py` is the worked example: a second detector, no fork of anything else. The recipe it followed —

1. Write a detector that emits the four canonical keys (`pattern`, `pattern_bars`, `leg_bars`, `struct_high` / `struct_low`, `risk_pct`) alongside whatever pattern-specific columns it wants. `postfilter.py` and `plot_hits.py` key off those and need no changes.
2. Add a panel function to `plot_hits.py` that draws what *that* pattern's judgement needs — the questions differ, so the chart should too.
3. Add a `--diagnose` mode printing the rejection histogram plus the universe distribution of whatever your tightest gates measure. Then actually read it, and set the thresholds from the distribution rather than from intuition.
4. Add synthetic cases to `scripts/selftest_patterns.py` — one that must hit, and one per failure mode that must not.
5. Register the pattern in `run_screener.sh`'s `PATTERNS` loop.

For other shapes: to detect a **rounding bottom**, keep the curvature and R² tests and invert the context filter — require the base near the *low* of the window with a preceding decline rather than a rally. For a **flat base**, drop the curvature requirement and test for a low standard deviation of closes plus a tight high-low range. For a **descending wedge**, fit two lines to swing highs and lows and test for convergence.

The plumbing (universe → fetch → drop partial bar → detect → context filter → plot → view) is identical in every case, and the context filters matter more than the pattern math regardless of which pattern you're after.

### Verifying a detector without a market

```bash
python scripts/selftest_patterns.py
```

Synthetic bars with known shapes — a rounded base, a V-bounce, a downtrend, an orderly dip, a falling knife, a one-candle gap-down — pushed through the real detectors, asserting on what comes out. Deterministic, no network, a few seconds. A screener's failure mode is silence; this is the check that fails loudly instead. Run it after touching any threshold.

## Honesty requirements

These are the things a user acting on this output most needs to be true:

- Never present the screener as having run live if it hasn't; say what data was actually fetched and when.
- Report real coverage, never imply a complete scan when symbols are missing.
- Flag names you distrust even when they passed every filter — the visual pass exists to produce exactly this kind of disagreement with the numbers.
- Don't dress a shortlist up as a recommendation. It's a list of candidates matching a geometry; entry, sizing, and whether to trade at all are the user's calls.
- If a threshold had to be loosened to produce any hits, say so explicitly — a loosened screener returning six names is not the same evidence as a strict one returning six.
- Keep the two patterns' shortlists apart, and never present their RRRs on one scale. A dip's 11.2 and a cup's 3.4 do not mean the dip is three times the trade.
- The dip screen buys into an open move. Say that plainly: it has no breakout confirmation, its stop is tight enough to be hit by noise, and "the trend is intact" is an observation about the past.

## Reference files

- `references/parameters.md` — full parameter list for both patterns, tuning guidance, measured calibration notes, and the expected funnel
- `references/troubleshooting.md` — zero hits (per detector), yfinance quirks, rate limits, timeouts, coverage gaps, and what changed in the detectors
- `scripts/indicators.py` — the shared EMA/RSI/ATR and the curve fits, including the saucer-vs-V discriminator
- `scripts/selftest_patterns.py` — synthetic end-to-end assertions for both detectors
