# NSE hourly pattern screen — 2026-08-20

**Rally-then-rounded-base near highs, hourly bars.**

📈 **Chart panels (required viewing):** https://claude.ai/code/artifact/8681d304-9518-4698-b3f8-43ea4e4f4919

> These are **candidates matching a geometry, not recommendations**. Entry, sizing,
> and whether to trade at all are your calls. No threshold was loosened to produce
> this list.

---

## 1. Coverage and data

| | |
|---|---|
| Universe | **nifty200 — 200 symbols** |
| Symbols with usable data | **200 / 200 (100%)** |
| Interval / history | 1h / 60d |
| Universe's newest closed bar | 2026-08-20 **15:15** IST |
| Bar the candidates are priced at | 2026-08-20 **14:15** IST |
| Run timestamp | 2026-08-20 23:25 IST (market closed) |

**The universe was overridden to `nifty200`, which is narrower than the skill's
default.** The skill defaults to the full EQ list (~2,293 symbols); this run
covered 200, about 9% of that. Do not read "3 raw hits" as comparable to a
full-universe scan — the funnel below is a Nifty 200 funnel.

**Two different "last bar" timestamps, and the difference matters.** The
universe's newest closed bar is 15:15, but **only 123 of 200 symbols carry that
15-minute stub**. The remaining 77 — including *both* surviving candidates — end
at 14:15. Every price, lip distance, and volume ratio quoted below for JUBLFOOD
and PAYTM is therefore a **14:15 close**: the final hour of the session is not in
these numbers. Confirm current levels on your own platform before acting.

Coverage itself was clean this run: 100%, no missing symbols.

---

## 2. Funnel

| Stage | Surviving | What it removed |
|---|---|---|
| Universe (nifty200) | 200 | — |
| Detector (`screener.py`) | **3** | 197 on the gate stack — EMA stack/rising, curvature ≥ 0.015, R² ≥ 0.45, vertex window, rally ≥ 10%, base at top, lip ≤ 4%, volume dry-up |
| Context filters (`postfilter.py`) | **2** | −1 **OBEROIRLTY**, gap-driven (`max_bar_share` 0.51). Liquidity and the 60-day-high check removed nothing. |
| Visual pass (this report) | **1** | −1 **JUBLFOOD**, spike-and-fade rather than rally-and-base |

---

## 3. Ranked table

Ranked by `rrr_structural` (target 15% ÷ risk-to-base-low), descending.

| # | Symbol | RRR | Close | Entry (lip) | Base low | Depth % | Risk to base low % | Rally % | Rally bars | Base bars | Curv | R² | Vertex | Dist from lip % | Vol ratio | Turnover ₹cr | % of 60d high | Bar share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | JUBLFOOD | 4.53 | 507.30 | 512.60 | 495.65 | 3.31 | 3.31 | 10.02 | 17 | 21 | 0.0231 | 0.703 | 0.012 | 1.03 | 0.22 | 85.27 | 98.5 | **0.50** |
| 2 | PAYTM | 3.04 | 1603.60 | 1626.50 | 1546.30 | 4.93 | 4.93 | 15.92 | 43 | 30 | 0.0329 | 0.605 | 0.014 | 1.41 | 0.56 | 405.39 | 98.2 | 0.27 |

Rejected before plotting:

| Symbol | Close | Entry | Reason |
|---|---|---|---|
| OBEROIRLTY | 1904.70 | 1960.30 | gap-driven, `max_bar_share` 0.51 (threshold rejects > 0.50) |

**RRR ranks the geometry, not the odds.** It reduces to inverse base depth, so
the shallowest base wins by construction. It states what a trade pays if it
works and is silent on how often it works. The top-ranked name here is the one I
distrust.

---

## 4. Tiers from the visual pass

### ✅ Clean structural match — PAYTM

- **Rally sustained?** Yes, and this is what separates it. Three distinct legs
  across 43 bars (≈1,315 → 1,450, a shelf near 1,440, then 1,440 → 1,655). No
  single candle carries more than 27% of the move.
- **Does the base round?** Yes, asymmetrically. Gives up 1,626 → 1,546 over
  ~18 bars, double-touches the low around bars 95–99, then recovers to ~1,610.
  The down leg is steeper than the recovery, so it is a genuine saucer rather
  than a V — but not a textbook symmetric one.
- **EMAs?** The 50 rises underneath and is never breached. The fast 20 cut down
  into the base and price has only just reclaimed it — the stack is intact, but
  only as of the last few bars.
- **Overhead supply?** Yes. The pre-base high near 1,655 sits ~1.8% above the
  1,626.50 lip, so a breakout runs into its own recent selling almost at once.

**Caveats even on the good one:** the base sits at 30 bars, exactly the
detector's `base_max` ceiling, so a longer base would not have been found at all;
and the volume dry-up (0.56) is moderate rather than emphatic.

### ⚠️ Distrust despite passing every filter — JUBLFOOD

This name passed all nine detector gates and all three context filters, ranks
first on RRR, and I do not trust it.

- **Rally sustained?** **No — this is the disqualifying read.** The 17-bar leg is
  mostly a *decline* from ~497 down to ~473, followed by one violent candle to
  520. That is why `max_bar_share` lands on **exactly 0.50**: half the measured
  move in a single bar. The filter rejects *above* 0.50, so it passed on a
  rounding boundary, not by margin.
- **And that candle was rejected by the market.** Its 520 print is a long upper
  wick that closed far lower, and it now sits *above* the 512.60 lip — meaning
  the overhead supply a breakout must clear was manufactured by the very bar the
  detector scored as the rally.
- **Base shape:** a tidy but very shallow shelf (3.31%) — closer to a flat base
  than a cup, though the vertex is dead-centre (0.012) and R² is the batch's best
  at 0.703.
- **What is genuinely good:** volume dry-up of 0.22 is the strongest in the
  batch, and the EMAs do run under the base and rise through it.

**Verdict: spike-and-fade into a flat shelf, not rally-and-base.** This is the
ASTRAL failure mode the `max_bar_share` filter was written to catch, and it slipped
through on the boundary.

### Marginal

None — with only two survivors, each fell clearly into one of the tiers above.

### A note on the filter boundary — flagged, not touched

JUBLFOOD passed at `max_bar_share` 0.50 and OBEROIRLTY was cut at 0.51. Same
failure mode, opposite sides of a rounding boundary, and my visual read says the
one that passed deserved the same cut as the one that didn't. **I think that
threshold's edge is doing more work than it can reliably bear and is worth
re-examining. Per the guardrail I have not changed it, and this run's numbers are
the unmodified screener's.**

---

## 5. Stop-inside-base check

Every surviving name has `stop_inside_base = true`. A 3% stop off the lip lands
inside any base deeper than 3%, sits mid-cup, and gets taken out by ordinary chop
*without the pattern having failed at all*.

| Symbol | Entry (lip) | 3% stop | Base low | `risk_pct_to_base_low` | Compatible? | Position size vs a 3% assumption |
|---|---|---|---|---|---|---|
| PAYTM | 1,626.50 | 1,577.70 | 1,546.30 | **4.93%** | **No** — the stop sits ₹31.40 inside the base | **0.61×** |
| JUBLFOOD | 512.60 | 497.22 | 495.65 | **3.31%** | **No** — the stop sits ₹1.57 inside the base | **0.91×** |

- **PAYTM:** honouring the structure means accepting **4.93%** risk instead of 3%.
  That is roughly 0.61× the position size and it changes the whole reward/risk
  arithmetic — the 3.04 RRR already reflects the structural risk, but a 3% stop
  assumption would silently inflate it to ~5.0.
- **JUBLFOOD:** the rare near-miss. At 3.31% vs a 3% stop the two are
  incompatible by only ₹1.57, so the fixed stop is *almost* honest here — but
  still inside the base, and still the wrong stop.

---

## 6. Regime

Bases near highs resolve upward far more often in a trending index than a choppy
one. The same screener on the same universe has a very different hit rate in the
two. The presence of a pattern today is a different question from whether it is
worth trading today, and only a backtest split by index trend state answers the
second. This run does not attempt that.

---

## 7. What this run does not tell you

- It scanned **200 symbols, not the ~2,293 EQ universe** — the routine's
  `UNIVERSE` override is set to `nifty200`.
- The two candidates are priced at **14:15**, not the 15:30 close.
- Charts are matplotlib renderings of yfinance data. EMA seeding and session
  handling differ from TradingView and Kite; treat them as shape verification and
  confirm prices on your own platform.
- One environmental fix was applied to make the run complete at all: NSE's
  archives host began returning HTTP 403 to the universe fetch's bare
  `User-Agent`. Browser-standard `Accept` / `Accept-Language` / `Referer` headers
  were added to `fetch_universe.py`. **No detector threshold, filter parameter,
  or ranking logic was touched.**
