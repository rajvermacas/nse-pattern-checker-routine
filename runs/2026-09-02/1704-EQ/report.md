# NSE hourly screen — rally + rounded base near highs

**Executed at:** 2026-09-02 17:04 IST (`run_ts_ist`)
**Latest data bar:** 2026-09-02 15:15 IST — the **2026-09-02 session** (`session_age_days` = 0, i.e. current)
**Charts:** https://claude.ai/code/artifact/897cbec1-8c38-4dd1-9bc6-c1adcbf8f788

Data snapshot completed 17:10 IST; market was closed at run time. Both timestamps above are
from `run_meta.json` — this screen runs on intraday hourly candles and can fire more than once
a day, so quote the pair, not just the date.

---

## Coverage

| | |
|---|---|
| Universe | `EQ` — the skill's default full NSE equity series |
| Symbols in universe | 2,301 |
| Symbols with usable data | **2,247 (97.7%)** |
| Missing | 54 (e.g. ADDIND, ALFREDHE, ANSALBU, APOORVA, ARCL, ARYAMAN, ASSAMENT, ASTAR, AUGMONT, BENARAS) |
| Interval / period | 1h / 60d |

Dropped 112 symbols at fetch: 60 returned no data, 52 had too few bars (recent listings and
symbols that don't map cleanly onto `SYMBOL.NS`). **This is not a full-universe scan** — 54
EQ symbols were never screened.

`pct_at_last_bar` is 95.6%: 2,149 of 2,247 symbols carry the 15:15 bar, so the universe's
last closed bar is not the price time for every symbol. It is for every name below —
all nine have `bars_behind_universe = 0` and are quoted at 2026-09-02 15:15.

## Funnel

| Stage | Count | What it cut |
|---|---|---|
| Symbols scanned | 2,247 | — |
| Raw detector hits | 37 | rally → rounded-base geometry, parabola fit |
| After context filters | **9** | 28 cut |

The 28 rejections, by reason (names carry more than one flag):

- **Illiquid** (< ₹5cr/day turnover) — 19 names: ADOR, JUNIPER, RSL, LANCORHOL, ALEMBICLTD,
  SHREEPUSHK, GYFTR, KAMATHOTEL, VENKEYS, ULTRAMAR, SHIVAMAUTO, DIFFNKG, KAPSTON, TEAMGTY,
  TTL, PROZONER, MARATHON, PRABHA, LANCER. Several are extreme — TEAMGTY ₹0.01cr,
  SHIVAMAUTO ₹0.03cr, TTL ₹0.08cr.
- **Not at highs** (< 97% of the 60-day high) — 9 names: LICHSGFIN 95.0%, ATLANTAELE 93.2%,
  PARACABLES 87.8%, SPAL 89.1%, SHIVAMAUTO 92.3%, TEAMGTY 95.2%, TTL 93.4%, PROZONER 93.3%,
  BEPL 93.4%.
- **Gap-driven** (one bar carrying too much of the rally) — 14 names: VENKEYS, URBANCO,
  KIRIINDUS, ULTRAMAR, DIFFNKG, KAPSTON, QUESS, TTL, PROZONER, KLBRENG-B, MARATHON, BEPL,
  PRABHA, LANCER.

Liquidity did most of the work. That is the expected shape on a full-EQ scan — the geometry
fires readily on thin small-caps where a handful of trades makes the curve.

## Ranked candidates

Ranked by structural RRR (target ÷ risk-to-base-low), best first. Prices at 2026-09-02 15:15.

| # | Symbol | Close | Entry (lip) | Base low | RRR | Base depth | Rally | Base bars | R² | Turnover ₹cr | % of 60d high |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CGCL | 256.60 | 258.90 | 249.00 | 3.93 | 3.82% | 17.6% | 14 (~2.0 sess) | 0.452 | 51.7 | 97.9 |
| 2 | MOL | 65.93 | 67.00 | 63.30 | 2.72 | 5.52% | 14.0% | 12 (~1.7 sess) | 0.610 | 6.0 | 99.6 |
| 3 | GIPCL | 205.94 | 207.70 | 196.01 | 2.66 | 5.63% | 23.4% | 23 (~3.3 sess) | 0.675 | 9.1 | 100.0 |
| 4 | RPEL | 1774.60 | 1798.00 | 1687.10 | 2.43 | 6.17% | 13.8% | 16 (~2.3 sess) | 0.672 | 9.6 | 99.3 |
| 5 | CONFIPET | 82.37 | 84.40 | 78.69 | 2.22 | 6.77% | 15.6% | 19 (~2.8 sess) | 0.686 | 10.1 | 97.7 |
| 6 | TFCILTD | 145.90 | 147.65 | 137.06 | 2.09 | 7.17% | 13.6% | 29 (~4.2 sess) | 0.789 | 86.2 | 100.0 |
| 7 | JTLIND | 92.40 | 93.87 | 86.99 | 2.05 | 7.33% | 17.4% | 18 (~2.6 sess) | 0.492 | 8.6 | 100.0 |
| 8 | REDINGTON | 362.60 | 372.00 | 344.10 | 2.00 | 7.50% | 14.0% | 26 (~3.8 sess) | 0.757 | 79.1 | 98.3 |
| 9 | KENNAMET | 4637.00 | 4734.70 | 4352.00 | 1.86 | 8.08% | 33.5% | 25 (~3.6 sess) | 0.581 | 14.5 | 97.5 |

RRR ranks the **geometry**, not the odds. It says what the trade pays if it works, never how
often it works, and because it is inverse base depth, the shallowest base automatically tops
the table. See CGCL below for exactly why that is a trap this week.

**Boundary pass:** KENNAMET cleared `pct_of_60d_high` at 97.5% against a 97.0% floor. A
boundary pass is not the same evidence as a margin pass. No name here has a wick-set base low
(`base_low_is_wick` false on all nine), so the quoted stops are on real bodies-and-lows, not a
single outlier print.

## Visual pass — what the charts actually show

I looked at all nine panels. Sorted:

### Clean structural match (3)

**GIPCL** — the best chart in the batch. Flat 170–177 shelf through 12–22 Aug, then a genuinely
sustained six-session advance to 207 with no single bar carrying it (largest bar is 17% of the
move — lowest concentration here). The base rounds properly: down to 196, curving back to 206.
Both EMAs run under the base and turn up through it. At the 60-day high.

**TFCILTD** — longest base (29 bars, ~4.2 sessions), best parabola fit (R² 0.789), and by far the
most liquid name here at ₹86cr/day. A staircase advance from 115 rather than a spike, then a
base that dips to 137 and curls back to 146, pressing into the lip on the last bar. The whole
60-day window is an uptrend, so it is extended — but the base is the most legitimately formed
of the nine.

**CONFIPET** — clean multi-day rally out of a 70–74 floor, base curving down to 78.7 and back to
82.4. One caveat the numbers don't show: there is visible overhead supply at 83–84 from late
August, which sits exactly at the 84.40 entry.

### Marginal (3)

**RPEL** — the trend is real (1,290 → 1,800 in three weeks), and that is the problem. The stock
is extended, and the 16-bar "base" is 2.3 sessions of tight shelf inside an ongoing advance —
a continuation flag being scored as a rounded base. Fine as a trend-continuation idea; it is
not the pattern this screen claims to find.

**KENNAMET** — +33.5% in four sessions, then an 8.1%-deep pullback. That is a breather inside a
near-parabolic move, not a base, and 8.1% is the deepest structural risk in the set. Compounded
by the boundary pass on `pct_of_60d_high`.

**REDINGTON** — dropped 378 → 344 sharply and has recovered only part of it; the fast EMA rolled
over *inside* the base and price traded beneath it, which a healthy rounded base does not do.
Reads closer to a failed push than a base. Also the highest single-bar concentration in the
batch (47% of the rally in one bar) — it passed the gap-driven filter, but only just, and the
eye sees what the threshold let through. Good liquidity (₹79cr) is the one thing in its favour.

### Distrust, despite passing every filter (3)

**CGCL — the top-ranked name, and the one I trust least.** It ranks first purely because its base
is the shallowest (3.82%), and RRR is inverse depth. What the chart shows is three weeks of flat
drift at 228, one near-vertical bar on 24 Aug carrying 45% of the entire rally, and two sessions
of drift underneath the high. Worst fit in the set (R² 0.452). The ranking is rewarding the
precise feature — a shallow, short base after a single-bar jump — that should disqualify it.
Do not read position 1 as "best candidate".

**MOL** — not a rally-then-base at all. Three weeks of choppy decline *down* to 58.5, then a
single-day vertical spike to 66 on 01 Sep. The 12-bar base is 1.7 sessions of hanging at the
high after a V-bounce off a low, with no prior uptrend to continue. Turnover ₹6.0cr is barely
above the ₹5cr floor. This is a V, and the detector fitted a parabola to it because a V fits a
parabola well.

**JTLIND** — R² 0.492 with a vertex well left of centre (−0.246). Both say the same thing: the fit
is describing a V-dip and a ramp back up, not a curved base. The parabola is being fitted to
something that isn't round.

## Stop-inside-base check

**All 9 of 9 put a conventional 3% stop inside the base**, where ordinary base noise reaches it.
Real structural risk is entry down to base low:

| Symbol | 3% stop | Structural stop (`risk_pct_to_base_low`) | Compatible? |
|---|---|---|---|
| CGCL | 3.00% | 3.82% | Marginal — closest in the set, still inside |
| MOL | 3.00% | 5.52% | No |
| GIPCL | 3.00% | 5.63% | No |
| RPEL | 3.00% | 6.17% | No |
| CONFIPET | 3.00% | 6.77% | No |
| TFCILTD | 3.00% | 7.17% | No |
| JTLIND | 3.00% | 7.33% | No |
| REDINGTON | 3.00% | 7.50% | No |
| KENNAMET | 3.00% | 8.08% | No |

Plainly: on eight of nine, a 3% stop is 1.8×–2.7× tighter than the base itself, so it sits in
the middle of the pattern's normal range and would be taken out by the base doing what bases
do. Only CGCL is close, at 3.82%, and CGCL is a name I distrust on other grounds. Size off the
structural number or don't take the setup — a fixed 3% here is not a tight stop, it is a stop
in the wrong place.

Closing-basis alternatives (`risk_pct_to_base_low_close`) are marginally tighter — CGCL 2.70%,
GIPCL 4.90%, TFCILTD 6.91%, REDINGTON 6.51%, KENNAMET 7.15% — but none of them rescues the 3%
figure, and the low-based stop remains the conservative one since those lows are real traded
prices.

## Honesty notes

- **These are candidates matching a geometry, not recommendations.** Nothing here is a call to
  buy. The screen finds a shape and says nothing about whether it resolves upward.
- Coverage was 2,247/2,301 (97.7%). 54 EQ symbols were never screened.
- No threshold, filter parameter or ranking rule was touched on this run. If anything wants
  tuning, it is the interaction between RRR and base depth — a very shallow, very short base
  (CGCL, 14 bars, 3.82%) mechanically tops the ranking while being the weakest structure in the
  batch. Flagging it; not changing it.
- One environmental note, no impact on results: Yahoo rate-limited several fetch batches. The
  resumable gap-fill recovered 58 of 112 missing symbols in round 1 and 0 in round 2, at which
  point the remaining 54 were judged genuinely absent rather than throttled. Coverage still
  landed at 97.7%, well above the 80% floor.
