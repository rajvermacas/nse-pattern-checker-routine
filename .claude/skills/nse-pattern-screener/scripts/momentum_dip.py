"""Momentum-dip detector: buy the pullback in a stock that is already strong.

Different animal from the rally-then-cup screen, and deliberately so. The cup
screen waits for a base to FINISH and buys the breakout above its lip; this one
buys INSIDE the pullback, while price is still below the recent swing high. That
is a better entry and a worse confirmation, so every gate here exists to answer
one of two questions:

    "is the trend still intact?"   and   "has the fall actually stopped?"

    swing high ─────●
                   ╱ ╲          ← dip: shallow, short, orderly, on lower volume
        advance   ╱   ╲   ●     ← last bar closing UP, off the low, in the
       (>=15%)   ╱     ╲ ╱        upper half of its range: the fall has paused
                ╱       ●       ← dip low, ABOVE the rising EMA50 = the stop
       ────────╱  EMA50 rising

The failure mode this screen must not produce is a falling knife: a stock that
is down 8% because something happened, still falling, that merely looks cheap
against last week. Three gates specifically target it --

  max_retrace       a dip deeper than half the advance is a trend change,
                    not a pause, whatever the chart's slope looks like.
  max_dip_bar_share one candle contributing most of the fall is news, and news
                    does not respect chart structure. Excluded, not ranked.
  stabilised        the last bar must close up, off the low, and not be the
                    low of the dip. Without this the screen returns whatever
                    is falling fastest, which is exactly backwards.

Even so: an intact-looking pullback resolves down often enough that the visual
pass and the stop matter more here than in the cup screen. `struct_stop` is the
dip low; if that stop is wider than the position can carry, the answer is a
smaller position or no trade, never a tighter stop.

Usage:
    python momentum_dip.py --parquet all_closed.parquet --json dip_hits.json
    python momentum_dip.py --parquet all_closed.parquet --diagnose
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass

import numpy as np
import polars as pl

import indicators as ind
import obs

LOG = obs.get_logger("dip")

PATTERN = "momentum_dip"


@dataclass
class Params:
    lookback: int = 120

    # --- is it a strong stock? -------------------------------------------
    ema_fast: int = 20
    ema_slow: int = 50
    trend_bars: int = 30          # EMA50 must be above where it was N bars ago
    # Calibrated on a live nifty500 hourly session, not guessed: the universe
    # distribution of the available advance ran p50 3.7% / p90 9.8% / p99 20%,
    # and 0.15 was the single gate emptying the screen -- 39 candidates reached
    # it, 0 passed. At 0.10 (~p90, and the same floor the cup screen uses for
    # its rally leg) it stops being the binding constraint: 0.10, 0.08 and 0.06
    # all return the same hits, so below 0.10 this gate buys nothing.
    min_advance: float = 0.10     # advance into the swing high, close-to-close
    leg_max_bars: int = 60
    min_leg_bars: int = 8
    max_below_window_high: float = 0.02   # swing high must BE the window's high

    # --- is it a dip, not a breakdown? -----------------------------------
    min_dip_bars: int = 2
    max_dip_bars: int = 15
    min_dip: float = 0.03
    max_dip: float = 0.12
    max_retrace: float = 0.50     # dip as a share of the advance it interrupts
    max_dip_bar_share: float = 0.60
    max_dip_vol_ratio: float = 1.00
    # A dip that WICKS through the rising EMA50 is the classic pullback entry;
    # one that CLOSES decisively under it is a trend change. So the gate is on
    # closes, with a slack, plus the entry bar having to be back above the line.
    # Testing the low instead (the first version of this) rejected exactly the
    # pullback-to-the-50 setups the screen exists to find.
    max_close_below_ema_slow: float = 0.02
    require_reclaim_ema_slow: bool = True

    # --- has the fall stopped, and is there still room? ------------------
    require_stabilised: bool = True
    min_close_pos: float = 0.50   # last close within its own bar's range
    max_recovered: float = 0.80   # how much of the dip may already be retraced


def _trigger(close, high, low, ef, dip_lo_idx, p) -> tuple[bool, str]:
    """Has the fall stopped? Returns (stabilised, which condition fired)."""
    n = len(close)
    if n - 1 - dip_lo_idx < 1:
        return False, "still_making_lows"     # the last bar IS the low
    rng = high[-1] - low[-1]
    pos = (close[-1] - low[-1]) / rng if rng > 1e-9 else 1.0
    if close[-1] > high[-2]:
        return True, "outside_reversal"       # closed above the prior bar's high
    if close[-1] > close[-2] and pos >= p.min_close_pos:
        return True, "up_close_off_low"
    if close[-1] > ef[-1] and low[dip_lo_idx] < ef[dip_lo_idx]:
        return True, "reclaimed_ema_fast"     # dipped under the 20 and took it back
    return False, "no_trigger"


def scan_symbol(sym: str, df: pl.DataFrame, p: Params,
                reasons: Counter | None = None) -> dict | None:
    def no(reason: str):
        if reasons is not None:
            reasons[reason] += 1
        return None

    if df.height < max(p.ema_slow, p.trend_bars) + p.max_dip_bars + 10:
        return no("too_short")

    g = df.tail(p.lookback)
    close = g["close"].to_numpy().astype(float)
    high = g["high"].to_numpy().astype(float)
    low = g["low"].to_numpy().astype(float)
    vol = g["volume"].to_numpy().astype(float)
    n = len(close)

    c_full = df["close"].to_numpy().astype(float)
    ef = ind.ema(c_full, p.ema_fast)[-p.lookback:]
    es = ind.ema(c_full, p.ema_slow)[-p.lookback:]

    # ---- 1. strong stock -------------------------------------------------
    # Note what is NOT required: close > EMA20. The whole point of a dip is
    # that price has fallen back into or under the fast average; demanding it
    # stay above would only ever return names that never dipped.
    if ef[-1] <= es[-1]:
        return no("ema_not_stacked")
    if es[-1] <= es[-p.trend_bars]:
        return no("ema_slow_flat")

    # ---- 2. locate the swing high we are dipping from --------------------
    win = p.max_dip_bars + 1
    hi_idx = n - win + int(np.argmax(high[-win:]))
    dip_bars = n - 1 - hi_idx
    if dip_bars < p.min_dip_bars:
        return no("no_dip_yet")            # the high IS the last bar or two
    swing_high = float(high[hi_idx])
    if swing_high < (1 - p.max_below_window_high) * float(high.max()):
        return no("high_not_window_high")  # dipping from a LOWER high

    dip_lo_idx = hi_idx + int(np.argmin(low[hi_idx:]))
    dip_low = float(low[dip_lo_idx])
    dip_pct = (swing_high - dip_low) / swing_high
    if dip_pct < p.min_dip:
        return no("dip_too_shallow")
    if dip_pct > p.max_dip:
        return no("dip_too_deep")

    # ---- 3. the advance the dip interrupts -------------------------------
    pre = close[:hi_idx + 1]
    seg = pre[-p.leg_max_bars:]
    li = int(seg.argmin())
    adv_low = float(seg[li])
    adv_high = float(seg[li:].max())
    leg_bars = len(seg) - li
    if leg_bars < p.min_leg_bars:
        return no("leg_too_short")
    adv_pct = (adv_high - adv_low) / adv_low
    if adv_pct < p.min_advance:
        return no("advance_too_small")

    # ---- 4. dip vs advance: pause or trend change? -----------------------
    span = swing_high - adv_low
    retrace = (swing_high - dip_low) / span if span > 1e-9 else 9.9
    if retrace > p.max_retrace:
        return no("retrace_too_deep")

    dip_closes = close[hi_idx + 1:]
    worst_close = float(dip_closes.min()) if len(dip_closes) else float(close[-1])
    worst_idx = hi_idx + 1 + int(dip_closes.argmin()) if len(dip_closes) else n - 1
    if worst_close < es[worst_idx] * (1 - p.max_close_below_ema_slow):
        return no("closed_under_ema_slow")
    if p.require_reclaim_ema_slow and close[-1] <= es[-1]:
        return no("no_ema_slow_reclaim")
    below_ema = int((dip_closes < es[hi_idx + 1:]).sum()) if len(dip_closes) else 0

    dseg = close[hi_idx:dip_lo_idx + 1]
    if len(dseg) >= 2:
        tot = dseg[0] - dseg.min()
        drop = -np.diff(dseg).min()
        dip_bar_share = float(drop / tot) if tot > 1e-9 else 9.9
    else:
        dip_bar_share = 9.9
    if dip_bar_share > p.max_dip_bar_share:
        return no("dip_gap_driven")

    av = float(vol[hi_idx - leg_bars + 1: hi_idx + 1].mean())
    dv = float(vol[hi_idx + 1:].mean())
    dip_vol_ratio = dv / av if av > 0 else 99.0
    if dip_vol_ratio > p.max_dip_vol_ratio:
        return no("dip_volume_heavy")

    # ---- 5. has the fall stopped, and is there room left? ----------------
    stabilised, trigger = _trigger(close, high, low, ef, dip_lo_idx, p)
    if p.require_stabilised and not stabilised:
        return no("not_stabilised")
    recovered = ((close[-1] - dip_low) / (swing_high - dip_low)
                 if swing_high > dip_low else 1.0)
    if recovered > p.max_recovered:
        return no("already_recovered")     # back at the high: a breakout, not a dip

    r = ind.rsi(c_full, 14)[-p.lookback:]
    rsi_now = float(r[-1]) if not np.isnan(r[-1]) else float("nan")
    rsi_dip = float(np.nanmin(r[hi_idx:])) if len(r[hi_idx:]) else float("nan")
    a = ind.atr(high, low, close, 14)
    atr_pct = float(a[-1] / close[-1] * 100) if not np.isnan(a[-1]) else float("nan")

    score = adv_pct * (1 - retrace) * (1.5 - min(dip_vol_ratio, 1.0))

    return {
        "symbol": sym, "pattern": PATTERN, "last_ts": str(g["ts"][-1]),
        "close": round(float(close[-1]), 2),
        # canonical cross-pattern keys (postfilter.py / plot_hits.py read these)
        "pattern_bars": dip_bars, "leg_bars": leg_bars,
        "struct_high": round(swing_high, 2), "struct_low": round(dip_low, 2),
        "struct_stop": round(dip_low, 2),
        # pattern specifics
        "dip_pct": round(dip_pct * 100, 2),
        "dip_bars": dip_bars,
        "retrace_of_advance": round(retrace, 2),
        "advance_pct": round(adv_pct * 100, 2), "advance_bars": leg_bars,
        "dip_bar_share": round(dip_bar_share, 2),
        "dip_vol_ratio": round(dip_vol_ratio, 2),
        "recovered_frac": round(float(recovered), 2),
        "bars_since_dip_low": n - 1 - dip_lo_idx,
        "trigger": trigger,
        "touched_ema_fast": bool(low[dip_lo_idx] <= ef[dip_lo_idx]),
        "vs_ema_slow_pct": round(float((worst_close / es[worst_idx] - 1) * 100), 2),
        "dip_closes_below_ema_slow": below_ema,
        "rsi": round(rsi_now, 1), "rsi_at_dip_low": round(rsi_dip, 1),
        "atr_pct": round(atr_pct, 2),
        "dist_from_high_pct": round((swing_high - float(close[-1])) / swing_high * 100, 2),
        "score": round(float(score), 5),
    }


def attach_levels(row: dict, sl_pct: float, target_pct: float) -> dict:
    """Entry is the current close; the stop is the dip low, not a percentage.

    `trigger_above` is the conservative alternative: wait for trade above the
    reversal bar's high instead of buying the close. Both are reported because
    they are genuinely different trades -- the close is a better price and a
    worse confirmation.
    """
    entry = row["close"]
    row["entry"] = entry
    row["trigger_above"] = row.get("trigger_above", entry)
    row["sl"] = round(entry * (1 - sl_pct), 2)
    row["t1"] = row["struct_high"]                       # reclaim the swing high
    row["t2"] = round(entry * (1 + target_pct), 2)
    row["risk_pct"] = round((entry - row["struct_low"]) / entry * 100, 2)
    # The dip low is the most-tested price in the structure -- a stop sitting
    # exactly on it is the one most likely to be taken out by a wick that does
    # not break the setup. Report a half-ATR buffer below it as the price of
    # actually surviving the noise, and the wider risk that implies.
    atr_abs = entry * row.get("atr_pct", 0.0) / 100.0
    buffered = row["struct_low"] - 0.5 * atr_abs
    row["struct_stop_buffered"] = round(buffered, 2)
    row["risk_pct_buffered"] = round((entry - buffered) / entry * 100, 2)
    # Same semantics as the cup screen's flag: the fixed-% stop sits INSIDE the
    # structure and will be taken out by noise without the setup having failed.
    row["stop_inside_base"] = row["sl"] > row["struct_low"]
    row["risk_pct_to_base_low"] = row["risk_pct"]
    row["base_depth_pct"] = row["dip_pct"]
    return row


def run(parquet: str, p: Params, sl=0.03, target=0.15) -> list[dict]:
    df = (pl.scan_parquet(parquet)
          .select(["symbol", "ts", "open", "high", "low", "close", "volume"])
          .sort(["symbol", "ts"]).collect())
    hits, n_syms, crashed = [], 0, 0
    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        n_syms += 1
        try:
            r = scan_symbol(str(sym), grp, p)
        except Exception as e:
            crashed += 1
            obs.log_exception(LOG, f"dip detector crashed on {sym}", e)
            continue
        if r:
            # trigger_above is the prior bar's high at the time of the hit
            g = grp.tail(p.lookback)
            r["trigger_above"] = round(float(g["high"].to_numpy()[-1]), 2)
            hits.append(attach_levels(r, sl, target))
    (LOG.error if crashed else LOG.info)(
        "dip: %d symbols scanned, %d hits, %d crashed", n_syms, len(hits), crashed)
    return sorted(hits, key=lambda r: r["score"], reverse=True)


def diagnose(parquet: str, p: Params) -> None:
    df = pl.scan_parquet(parquet).sort(["symbol", "ts"]).collect()
    reasons, passed = Counter(), 0
    dips, advs = [], []
    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        if scan_symbol(str(sym), grp, p, reasons):
            passed += 1
        g = grp.tail(p.lookback)
        h = g["high"].to_numpy().astype(float)
        l = g["low"].to_numpy().astype(float)
        c = g["close"].to_numpy().astype(float)
        if len(c) < 60:
            continue
        win = p.max_dip_bars + 1
        hi = len(h) - win + int(np.argmax(h[-win:]))
        sh = float(h[hi])
        dips.append((sh - float(l[hi:].min())) / sh)
        advs.append((sh - float(c[:hi + 1][-p.leg_max_bars:].min()))
                    / float(c[:hi + 1][-p.leg_max_bars:].min()))

    print(f"symbols: {df['symbol'].n_unique()}   passed: {passed}\n")
    print("rejection reasons (first failing gate):")
    for k, v in reasons.most_common():
        print(f"  {k:26s} {v}")
    if dips:
        print("\nuniverse distribution (p50 / p75 / p90 / p95 / p99):")
        print("  dip_pct     ", np.round(np.percentile(dips, [50, 75, 90, 95, 99]) * 100, 2))
        print("  advance_pct ", np.round(np.percentile(advs, [50, 75, 90, 95, 99]) * 100, 2))
        print("\nmin_dip/max_dip and min_advance are the two gates most likely to")
        print("be mis-set for a timeframe other than hourly. Compare them here.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--json", default="dip_hits.json")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--min-advance", type=float, default=None)
    ap.add_argument("--min-dip", type=float, default=None)
    ap.add_argument("--max-dip", type=float, default=None)
    ap.add_argument("--max-retrace", type=float, default=None)
    ap.add_argument("--max-dip-bars", type=int, default=None)
    ap.add_argument("--max-dip-vol-ratio", type=float, default=None)
    ap.add_argument("--max-close-below-ema-slow", type=float, default=None)
    ap.add_argument("--no-stabilised", action="store_true",
                    help="drop the reversal-bar requirement (returns falling "
                         "knives; for diagnosis only, say so if you use it)")
    ap.add_argument("--sl-pct", type=float, default=0.03)
    ap.add_argument("--target-pct", type=float, default=15.0,
                    help="profit target off the entry in PERCENT (15.0 == 15%%), "
                         "same units as postfilter.py's --target-pct")
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    p = Params()
    for attr in ("min_advance", "min_dip", "max_dip", "max_retrace",
                 "max_dip_bars", "max_dip_vol_ratio",
                 "max_close_below_ema_slow"):
        v = getattr(args, attr)
        if v is not None:
            setattr(p, attr, v)
    if args.no_stabilised:
        p.require_stabilised = False
        print("WARNING: --no-stabilised is on. Hits may still be falling.")

    if args.diagnose:
        diagnose(args.parquet, p)
        return

    hits = run(args.parquet, p, sl=args.sl_pct, target=args.target_pct / 100.0)
    json.dump(hits, open(args.json, "w"), indent=2, default=str)
    if not hits:
        print("no momentum dips. Run with --diagnose before calling it a quiet market.")
        return

    pl.Config.set_tbl_rows(args.top)
    pl.Config.set_tbl_width_chars(250)
    pl.Config.set_tbl_cols(22)
    print(f"{len(hits)} raw dip hits -> {args.json}")
    print(pl.DataFrame(hits).head(args.top).select(
        ["symbol", "close", "advance_pct", "dip_pct", "dip_bars",
         "retrace_of_advance", "dip_vol_ratio", "recovered_frac", "rsi",
         "trigger", "risk_pct"]))
    print("\nNext: postfilter.py (context filters), then plot_hits.py and VIEW the png.")
    print("A pullback that looks intact still resolves down often. The chart and")
    print("the stop matter more here than in the cup screen, not less.")


if __name__ == "__main__":
    main()
