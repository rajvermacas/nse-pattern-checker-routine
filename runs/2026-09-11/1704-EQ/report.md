# NSE hourly — rally + rounded base near highs

| | |
|---|---|
| **Executed at** | **2026-09-11 17:04 IST** (`run_ts_ist`) |
| **Latest data bar screened** | **2026-09-11 15:15:00 IST** — the 2026-09-11 session |
| Session age | 0 days. The newest closed bar is from today's session. |
| Data snapshot taken | 2026-09-11 17:09 IST (after the ~4½ min fetch) |
| Market state at run | Closed. The 15:15 stub is a genuine close and was kept, not dropped. |
| Universe | `EQ` — the full NSE rolling-settlement equity list (skill default, not a narrowed slice) |
| Interval | 1h |

**Chart of all 14 hits (view this before reading the table):**
<https://claude.ai/code/artifact/9b11b542-7739-48ff-bcb0-c7f883591806>

These are **candidates matching a geometry, not recommendations.** The screener
finds a shape. It does not know whether the shape is worth trading, and nothing
below is a view on that. Entry, sizing, and whether to trade at all are yours.

---

## 1. Coverage

| | |
|---|---|
| Symbols in EQ universe | 2,292 |
| Symbols with usable 60d hourly data | **2,269 (98%)** |
| Symbols carrying the 15:15 bar | 2,179 of 2,269 (**96.0%**) |
| Universe consensus last bar | 2026-09-11 15:15:00 (2,179 symbols) |

23 symbols returned no usable data (recent listings without 60 days of history,
and names that do not map to `SYMBOL.NS` on Yahoo) — e.g. APOORVA, ASSAMENT,
CRESTO, DEEPA, DOLLEX, ESDS, KDGREEN, LUMINO, MUKESHB, NEAGI. This is **not** a
complete scan of the universe; it is a scan of 98% of it.

**Per-hit staleness: none.** All 14 names below carry `bars_behind_universe = 0`
and a `last_ts` of 2026-09-11 15:15:00, so every level quoted here is priced at
the same bar. The 4% of the universe that lags the last bar produced no hits.

## 2. Funnel

```
  2,269 symbols with data
        │
        ├─ detector (EMA stack, EMA rising, rally ≥10%, depth ≤10%,
        │            curvature ≥0.015, R² ≥0.45, |vx| ≤0.65,
        │            at-top, lip ≤4%, vol ratio ≤0.85)
        ▼
     40 raw hits
        │
        ├─ context filters cut 26 (a name can fail more than one):
        │     not-at-high  (<97% of 60d high) ....... 15
        │     illiquid     (<₹5cr/day turnover) ..... 14
        │     gap-driven   (one bar >50% of rally) .. 12
        ▼
     14 clean hits
        │
        ├─ visual pass (below) cut 5 as untrustworthy, 4 as marginal
        ▼
      5 clean structural matches
```

**What each filter actually removed.**

- **not-at-high** — RAYMONDREL (79.6% of its 60d high), PWL (85.9%), ANGELONE
  (86.2%), EIEL (86.7%), UNITECH (84.2%), SIGNPOST (82.9%), MALUPAPER,
  GTPL, CLEANMAX, TEGA, CEIGALL, IONEXCHANG, TEMPSENS, TARC, TALBROAUTO.
  These are downtrend bounces that look like "rally + base near the high" to a
  120-bar window while sitting well below the real high.
- **illiquid** — AXTEL (₹0.08cr/day), MALUPAPER (₹0.02cr), GTPL (₹0.15cr),
  CPCAP (₹0.15cr), SAHYADRI (₹0.28cr), ZIMLAB, GLOBAL, SIGNPOST, UNITECH,
  GOCLCORP, CORDSCABLE, TALBROAUTO, TARC, MAXESTATES (₹4.67cr, the near miss).
  Pretty geometry, unfillable entries.
- **gap-driven** — SIGNPOST (0.95), SAHYADRI (0.92), GOCLCORP (0.91),
  VENKEYS (0.85), MANYAVAR (0.84), ANGELONE, UNITECH, INDSWFTLAB, EIEL,
  TEMPSENS, CORDSCABLE, TALBROAUTO. One gap candle carried most of the "rally".

No hit passed within an edge of a filter this run (`edge_flags` empty for all
14), so there are no boundary passes to discount.

## 3. Ranked table

Ranked by `rrr_structural` = 15% target ÷ base depth. **This ranks the geometry,
not the odds.** It says what the trade pays if it works and is silent on how
often it works. The top name is not the most likely to succeed.

| # | Symbol | RRR | Close | Entry (lip) | Base low | Depth % | Risk to base low | Dist from lip | Base bars | Rally % | Curv | R² | Vol ratio | %60d high | Turnover ₹cr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | JKPAPER | 3.57 | 414.25 | 423.85 | 406.05 | 4.20 | 4.20% | 2.26% | 30 (≈4.4 sess) | 10.25 | 0.0166 | 0.532 | 0.44 | 98.6 | 8.68 |
| 2 | INDOMIM | 3.21 | 1014.45 | 1028.00 | 979.85 | 4.68 | 4.68% | 1.32% | 12 (≈1.7) | 21.92 | 0.0240 | 0.742 | 0.70 | 100.0 | 97.34 |
| 3 | KLBRENG-B | 2.98 | 486.95 | 490.40 | 465.70 | 5.04 | 5.04% | 0.70% | 12 (≈1.7) | 14.90 | 0.0230 | 0.747 | 0.81 | 100.0 | 8.31 |
| 4 | UNIMECH | 2.88 | 1610.00 | 1614.90 | 1531.00 | 5.20 | 5.20% | 0.30% | 15 (≈2.2) | 15.78 | 0.0198 | 0.804 | 0.64 | 97.9 | 13.82 |
| 5 | AEROFLEX | 2.60 | 563.95 | 580.00 | 546.55 | 5.77 | 5.77% | 2.77% | 23 (≈3.3) | 11.52 | 0.0198 | 0.479 | 0.59 | 99.3 | 38.75 |
| 6 | SYMBIOTEC | 2.58 | 1138.00 | 1174.00 | 1105.75 | 5.81 | 5.81% | 3.07% | 12 (≈1.7) | 12.67 | 0.0286 | 0.866 | 0.64 | 98.4 | 149.51 |
| 7 | VENUSPIPES | 2.34 | 2015.60 | 2040.00 | 1909.40 | 6.40 | 6.40% | 1.20% | 22 (≈3.2) | 25.00 | 0.0243 | 0.787 | 0.55 | 100.0 | 13.89 |
| 8 | RISHABH | 2.31 | 829.60 | 850.05 | 795.00 | 6.48 | 6.48% | 2.41% | 21 (≈3.1) | 19.26 | 0.0347 | 0.581 | 0.42 | 100.0 | 9.48 |
| 9 | PCJEWELLER | 1.99 | 13.74 | 14.30 | 13.22 | 7.55 | 7.55% | 3.92% | 13 (≈1.9) | 42.99 | 0.0182 | 0.778 | 0.53 | 99.5 | 326.51 |
| 10 | WSTCSTPAPR | 1.89 | 713.80 | 721.70 | 664.40 | 7.94 | 7.94% | 1.09% | 29 (≈4.2) | 12.75 | 0.0313 | 0.674 | 0.70 | 100.0 | 10.06 |
| 11 | SMLMAH | 1.81 | 6591.00 | 6650.00 | 6098.50 | 8.29 | 8.29% | 0.89% | 17 (≈2.5) | 25.40 | 0.0487 | 0.913 | 0.42 | 100.0 | 24.79 |
| 12 | SAKAR | 1.63 | 1158.55 | 1195.00 | 1084.95 | 9.21 | 9.21% | 3.05% | 16 (≈2.3) | 28.55 | 0.0278 | 0.495 | 0.34 | 98.7 | 5.77 |
| 13 | SOLARA | 1.61 | 749.15 | 759.55 | 688.90 | 9.30 | 9.30% | 1.37% | 24 (≈3.5) | 15.55 | 0.0233 | 0.677 | 0.78 | 100.0 | 17.21 |
| 14 | MAHSEAMLES | 1.60 | 728.90 | 738.00 | 668.70 | 9.39 | 9.39% | 1.23% | 30 (≈4.4) | 11.38 | 0.0433 | 0.829 | 0.81 | 100.0 | 14.05 |

NSE hourly bars run 09:15 … 15:15, ~7 per session, so "30 bars" ≈ 4.4 sessions.

## 4. Tiers from the visual pass

Every panel was rendered at two-up and then re-rendered at **one-up**, because
four of the calls below flipped between the two resolutions. The ranking above
is untouched; this section is where I disagree with it.

### Tier A — clean structural match (5)

- **WSTCSTPAPR** (#10) — the best structure in the batch and the one the RRR
  ranking buries. A genuine 4.2-session saucer: decline into 27 Aug at 605, a
  long rounding recovery through 620/640/660, a thrust to 721 on 08 Sep, then a
  pullback to 664 and a steady round back up to the lip on the final bars. Both
  EMAs run under the base and rise through it. Rally sustained across three
  weeks. Caveat: price is already back at the lip, so the entry is essentially
  gone at 721, and the 7.94% structural stop is wide.
- **AEROFLEX** (#5) — upgraded from marginal after the one-up render. The rally
  from 490 to 580 is a proper three-week staircase with repeated
  pullback-and-continue, not a thrust. The base is a shallow saucer/shelf and
  both EMAs sit under it, rising. Its R² of 0.479 is the weakest fit in the
  batch and nearly the 0.45 floor, but the fit is weak because the base is
  *shallow*, not because it is the wrong shape. Furthest from its lip at 2.77%,
  which is the batch's best remaining entry room.
- **RISHABH** (#8) — three weeks of stair-step advance from 670 to 850, then a
  shallow rounding base that dips to 795 and drifts back to 830. EMAs under and
  rising. Unremarkable in every dimension, which here is a compliment.
- **MAHSEAMLES** (#14) — a real 4.4-session saucer (700 → 668 → 738) after the
  most modest rally in the batch (11.38%), with EMAs under and rising through.
  Structurally the soundest of the deep-base names. But its 9.39% depth is the
  deepest here, so honoring the structure means a 9.4% stop from a lip that
  price is already sitting 1.23% under.
- **KLBRENG-B** (#3) — the cleanest *trend* of the fourteen: a textbook staircase
  from 383 to 490 with repeated orderly pullbacks, EMAs under and rising, price
  0.70% from the lip. Two caveats keep it from being unqualified: the base is
  only 12 bars (1.7 sessions), which is a pause rather than a rounded base, and
  its `base_low` of 465.70 is set by a single wick (see §5). Note also the `-B`
  series suffix on the symbol — confirm the tradable series on your platform.

### Tier B — marginal (4)

- **INDOMIM** (#2) — the rally is genuine and sustained (845 → 1028 over five
  sessions, to a new high), but **there is no base**. The 12-bar window the
  detector called a base is price still advancing into new highs on the final
  bars. The curvature is being fitted to an ongoing leg, not a consolidation.
  Buying the 1028 lip is buying an extended move, not a breakout from a base.
- **UNIMECH** (#4) — three weeks of a 1450–1520 chop, then a near-vertical
  two-day rally to 1615 with a long upper wick on the high bar, then a 2.2-session
  pause. `max_bar_share` of 0.24 confirms no single candle carried it, so it is
  not a gap — but a two-day vertical out of a range is not the sustained rally
  leg this pattern wants. Closest to its lip of any name at 0.30%, so there is
  no entry room left either.
- **VENUSPIPES** (#7) — the shape is right: the base does round (2040 → 1910 →
  back to 2040) and the EMAs run under it, rising steeply. The problem is
  context. The stock added 25% in three sessions before the base formed and is
  now printing new highs on the last bar. This is a high-and-tight continuation,
  not a rounded base, and a 6.4% structural stop under a move that size is a
  different proposition than the geometry suggests.
- **SOLARA** (#13) — the base is a legitimate 3.5-session shelf with EMAs under
  and rising, but it is **resolving right now**: the final bar is a large green
  candle that ran to within 1.37% of the 759.55 lip. The setup has already
  happened. Combined with a 9.30% base depth, anyone entering here takes a
  near-10% structural stop on a move already underway.

### Tier C — passed every filter, and I do not trust them (5)

- **SYMBIOTEC** (#6) — **the clearest false positive in the batch.** It has only
  63 bars of history (first bar 2026-09-01): a recent listing. It opened near
  1190 on day one, crashed to 950 within the first bar, and has been grinding
  back up since. The "rally" is that recovery leg and the "base" is a pullback
  under the day-one high. The `pct_of_60d_high` filter reads 98.4% and passes it
  — but with nine sessions of history, that filter is comparing against a
  nine-session window, so the exact failure mode it exists to catch is invisible
  to it here. There is visible overhead supply at 1150–1190 from day one, and
  the fast EMA is sitting *above* price at the right edge. Its R² of 0.866 is the
  second-highest here, which is the documented trap: a V fits a parabola better
  than a cup does.
- **SMLMAH** (#11) — highest R² in the batch at 0.913, and that is the warning,
  not the endorsement. After a 25% five-day vertical run, the "base" is a sharp
  8.29% drop to 6098 and an almost symmetric snap back to 6591 across 2.5
  sessions. That is a V-shaped shakeout, not a saucer. The parabola fits it
  beautifully because a V is a parabola.
- **JKPAPER** (#1) — **the top-ranked name, and the one I trust least of the
  liquid ones.** Its 4.20% base depth wins the RRR ranking simply by being
  shallow. On the one-up render the base is not a base: price fell straight from
  428 to 406 and has chopped 408–418 since, and the fast EMA rolled *over* and
  ran flat-to-down through the window rather than under it and rising. That is
  the explicit EMA check failing visually while the numeric stack test passes.
  R² 0.532, and the rally is four sessions of a 10.25% move — the weakest rally
  in the batch.
- **PCJEWELLER** (#9) — a ₹14 stock that ramped 43% in five sessions and then
  paused for two. The 7.55% "base depth" is a handful of ticks at this price.
  Turnover of ₹326cr/day looks reassuring but is a product of the ramp itself.
  This is speculative momentum, and the pattern language does not apply to it.
- **SAKAR** (#12) — thinnest name that passed at ₹5.77cr/day turnover (the floor
  is ₹5cr), near-floor fit quality at R² 0.495, a 28.55% prior run, and a
  "base" that is a violent 9.21% swing across 2.3 sessions. Every individual
  reading is marginal and they are marginal in the same direction.

## 5. Risk reality check — the stop-inside-base problem

**All 14 of 14 hits have a 3% stop sitting inside the base.** This is not an
edge case this run; it is universal. A 3% stop off the lip lands mid-cup on
every single name here and gets taken out by ordinary chop without the pattern
having failed at all.

| Symbol | Entry (lip) | 3% stop | Base low | **Real structural risk** | 3% compatible? |
|---|---|---|---|---|---|
| JKPAPER | 423.85 | 411.13 | 406.05 | **4.20%** | No |
| INDOMIM | 1028.00 | 997.16 | 979.85 | **4.68%** | No |
| KLBRENG-B | 490.40 | 475.69 | 465.70 | **5.04%** | No |
| UNIMECH | 1614.90 | 1566.45 | 1531.00 | **5.20%** | No |
| AEROFLEX | 580.00 | 562.60 | 546.55 | **5.77%** | No |
| SYMBIOTEC | 1174.00 | 1138.78 | 1105.75 | **5.81%** | No |
| VENUSPIPES | 2040.00 | 1978.80 | 1909.40 | **6.40%** | No |
| RISHABH | 850.05 | 824.55 | 795.00 | **6.48%** | No |
| PCJEWELLER | 14.30 | 13.87 | 13.22 | **7.55%** | No |
| WSTCSTPAPR | 721.70 | 700.05 | 664.40 | **7.94%** | No |
| SMLMAH | 6650.00 | 6450.50 | 6098.50 | **8.29%** | No |
| SAKAR | 1195.00 | 1159.15 | 1084.95 | **9.21%** | No |
| SOLARA | 759.55 | 736.76 | 688.90 | **9.30%** | No |
| MAHSEAMLES | 738.00 | 715.86 | 668.70 | **9.39%** | No |

Honoring the structure on MAHSEAMLES means 9.39% risk, not 3% — roughly a third
the position size a 3% assumption would imply, and a completely different
reward/risk calculation. The same is true, to varying degrees, of all fourteen.

### Five names where `base_low` is set by a single wick

For these, the lowest low in the base window sits materially below every other
bar in it. The wick is a real traded price, so `base_low`, the quoted risk and
the RRR rank all keep using it — and that single bar therefore *depresses* the
rank. The closing-basis floor is shown so you can see how far the two readings
diverge and decide which one your sizing assumes.

| Symbol | `base_low` (wick) | Risk to wick | Closing-basis floor | Risk to close floor | Gap |
|---|---|---|---|---|---|
| KLBRENG-B | 465.70 | 5.04% | 475.00 | **3.14%** | 1.80% of entry |
| UNIMECH | 1531.00 | 5.20% | 1561.10 | **3.33%** | 1.36% |
| PCJEWELLER | 13.22 | 7.55% | 13.51 | **5.52%** | 1.61% |
| SMLMAH | 6098.50 | 8.29% | 6277.00 | **5.61%** | 2.35% |
| SAKAR | 1084.95 | 9.21% | 1113.55 | **6.82%** | 1.24% |

KLBRENG-B is the case that matters most: on a closing basis its risk is 3.14%,
which is the only reading in this entire run that comes close to a conventional
3% stop. It is a genuinely different proposition from, say, MAHSEAMLES at 9.39%,
even though both are "bases". The conservative stop remains the wick.

## 6. Regime

Bases near highs resolve upward far more often in a trending index than a choppy
one, and the same screener on the same universe has a very different hit rate in
the two. The presence of a pattern today is a different question from whether it
is worth trading today, and only a backtest split by index trend state answers
the second. Nothing here is such a backtest.

## 7. Method notes and honesty items

- **No threshold was loosened, tuned, or overridden this run.** Every parameter
  is at its documented default: `min_turnover ₹5cr`, `min_pct_60d_high 97`,
  `max_bar_share 0.5`, `target_pct 15`, `min_curvature 0.015`, `min_r2 0.45`.
  The only re-run performed was re-plotting existing hits at `--cols 1`, which
  changes no data.
- **One calibration gap worth recording, not acted on:** the
  `pct_of_60d_high` filter silently degrades for symbols with less than 60 days
  of history — it compares against whatever window exists. SYMBIOTEC (63 bars)
  passed at 98.4% on a nine-session window and is, on the chart, exactly the
  downtrend-bounce case that filter exists to reject. A minimum-history gate
  would catch this class. **I have not changed anything**; flagging it here is
  the correct action, and tuning it mid-run to improve today's list would not be.
- The charts are matplotlib renderings of yfinance hourly data. EMA seeding and
  session handling differ from TradingView and Kite. Treat them as shape
  verification and confirm every price on your own platform before acting.
- Turnover is a median-hourly estimate scaled to 7 bars/day, not an exchange
  figure.
