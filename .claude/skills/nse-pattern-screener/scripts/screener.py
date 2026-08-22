"""Rally-then-cup detector: steep rally leg into a shallow ROUNDED base that
forms near the rally high, price above rising fast EMAs, volume drying up.

CALIBRATION NOTE (the thing that bites):
The parabola is fit on price divided by its own mean, over x in [-1, 1].
Under that normalization the curvature coefficient `a` comes out roughly equal
to the cup's FRACTIONAL DEPTH -- a 5% cup gives a ~= 0.05. Across the whole NSE
universe the 99th percentile of `a` is about 0.043. So min_curvature belongs
near 0.015, NOT 0.15. Setting it an order of magnitude too high returns zero
matches on every input, which reads as "quiet market" rather than as a bug.

SHAPE GATES (added after the V-bounce problem kept surviving every number):
curvature and R^2 cannot tell a saucer from a checkmark -- a V-bounce fits a
parabola BETTER than a real cup. Two metrics can, and they are gated here:

  vee_gain     how much better a two-straight-line V fits than the parabola.
               Negative for saucers, positive for checkmarks. On synthetic
               bases at realistic hourly noise, `> 0.05` rejects ~80% of
               symmetric V-bounces and ~68% of asymmetric ones for ~10% of
               genuine cups.
  bottom_frac  share of closes in the lower third of the base. ~0.58 for a
               parabola (it loiters at the bottom), ~0.33 for straight legs.

They do NOT replace the visual pass -- they move the batch from "mostly
V-bounces" to "mostly bases", which is the difference between the eye doing
triage and the eye doing confirmation. Everything they cut is written to
--shape-rejects so a mis-tuned gate can never silently empty the funnel.

Run --diagnose whenever a scan returns zero hits.

Usage:
    python screener.py --parquet all_closed.parquet --json hits.json
    python screener.py --parquet all_closed.parquet --diagnose
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

LOG = obs.get_logger("detect")

PATTERN = "rally_cup"


@dataclass
class Params:
    # the cup
    base_min: int = 12
    base_max: int = 30
    base_max_depth: float = 0.10
    min_curvature: float = 0.015   # ~= fractional cup depth; see note above
    min_r2: float = 0.45
    vertex_window: float = 0.65

    # cup SHAPE -- saucer vs checkmark. See module docstring.
    max_vee_gain: float = 0.05
    min_bottom_frac: float = 0.30

    # how many of the 19 candidate window lengths must agree. One window in
    # nineteen fitting is a multiple-comparisons artifact, not a base.
    min_k_stability: int = 2

    # the rally leg feeding it
    rally_max_bars: int = 45
    min_rally: float = 0.10
    min_slope_ratio: float = 1.5
    # deepest give-back inside the leg, as a fraction of the leg itself. A leg
    # that surrenders half its gain mid-way is two moves, not one rally.
    max_rally_dd_share: float = 0.5

    # cup must sit at the TOP
    base_top_vs_rally_high: float = 0.97
    max_dist_from_high: float = 0.04

    # trend + volume
    ema_fast: int = 20
    ema_slow: int = 50
    require_ema_stack: bool = True
    max_base_vol_ratio: float = 0.85
    # below this the "dry-up" is almost certainly a yfinance artifact rather
    # than real selling exhaustion. Flagged, not rejected -- and clamped out of
    # the score so a data hole cannot rank first.
    suspect_vol_ratio: float = 0.10

    lookback: int = 120


def _emas(df: pl.DataFrame, p: Params) -> tuple[np.ndarray, np.ndarray]:
    """EMAs computed on the FULL history, then sliced to the lookback window.

    Computing them on the 120-bar slice (the old behaviour) meant EMA50 spent
    the first third of the window unwinding its seed, so the "close > EMA20 >
    EMA50" gate was partly testing the seed. plot_hits.py now calls the same
    function on the same full history, so the chart shows the line the gate saw.
    """
    c = df["close"].to_numpy().astype(float)
    return (ind.ema(c, p.ema_fast)[-p.lookback:],
            ind.ema(c, p.ema_slow)[-p.lookback:])


def scan_symbol(sym: str, df: pl.DataFrame, p: Params,
                reasons: Counter | None = None,
                shape_rejects: list | None = None) -> dict | None:
    if df.height < p.base_min + 20:
        if reasons is not None:
            reasons["too_short"] += 1
        return None

    g = df.tail(p.lookback)
    close = g["close"].to_numpy().astype(float)
    high = g["high"].to_numpy().astype(float)
    low = g["low"].to_numpy().astype(float)
    vol = g["volume"].to_numpy().astype(float)
    n = len(close)

    ef, es = _emas(df, p)
    if p.require_ema_stack:
        if not (close[-1] > ef[-1] > es[-1]):
            if reasons is not None:
                reasons["ema_stack"] += 1
            return None
        if ef[-1] <= ef[-p.base_min]:
            if reasons is not None:
                reasons["ema_rising"] += 1
            return None

    best, inner = None, Counter()
    k_pass: list[int] = []
    shape_only: dict | None = None   # best candidate that failed ONLY on shape

    for k in range(p.base_min, min(p.base_max, n - 10) + 1):
        bc = close[-k:]
        bh, bl = float(high[-k:].max()), float(low[-k:].min())

        depth = (bh - bl) / bh
        if depth > p.base_max_depth:
            inner["depth"] += 1
            continue

        sh = ind.shape_metrics(bc)
        a, r2, vx = sh["curvature"], sh["r2"], sh["vertex_x"]
        if a < p.min_curvature:
            inner["curvature"] += 1
            continue
        if r2 < p.min_r2:
            inner["r2"] += 1
            continue
        if abs(vx) > p.vertex_window:
            inner["vertex"] += 1
            continue

        # ---- the rally leg -------------------------------------------------
        # Measured close-to-close on both ends. The old code took the low from
        # closes and the high from `high`, which mixed two price series and
        # inflated every rally by a wick. Closes are the conservative choice:
        # they measure the part of the move that actually held into a close.
        pre_close = close[: n - k]
        if len(pre_close) < 8:
            inner["no_rally_room"] += 1
            continue
        w = pre_close[-p.rally_max_bars:]
        li = int(w.argmin())
        rl = float(w[li])
        leg = w[li:]
        rh = float(leg.max())
        rb = len(w) - li
        if rb < 5:
            inner["rally_too_short"] += 1
            continue

        rally_pct = (rh - rl) / rl
        if rally_pct < p.min_rally:
            inner["rally_pct"] += 1
            continue

        # A leg that gives back half its gain in the middle is two moves.
        rally_dd = ind.max_drawdown(leg)
        if rally_pct > 0 and rally_dd > p.max_rally_dd_share * rally_pct:
            inner["rally_drawdown"] += 1
            continue

        # base at the top of the leg, closes vs closes
        if float(bc.max()) < p.base_top_vs_rally_high * rh:
            inner["base_not_at_top"] += 1
            continue

        rs = (rh - rl) / rb / rl
        bs = abs(bc[-1] - bc[0]) / k / bc[0]
        if bs > 1e-9 and rs / bs < p.min_slope_ratio:
            inner["slope_ratio"] += 1
            continue

        dist = (bh - close[-1]) / bh
        if dist > p.max_dist_from_high:
            inner["dist_from_lip"] += 1
            continue

        rv = float(vol[n - k - rb: n - k].mean())
        bv = float(vol[-k:].mean())
        vr = bv / rv if rv > 0 else 99.0
        if vr > p.max_base_vol_ratio:
            inner["volume"] += 1
            continue

        # ---- shape: saucer or checkmark? -----------------------------------
        # Everything above this line is the legacy gate set. Anything that dies
        # below it is recorded, so a mis-calibrated shape threshold shows up as
        # "the shape gates ate the funnel" instead of "quiet market".
        vol_suspect = bool(vr < p.suspect_vol_ratio or (vol[-k:] <= 0).any())
        # clamp so a zero-volume data hole cannot buy the top rank
        vr_scored = max(vr, p.suspect_vol_ratio)
        overhead = float((close[:n - k] > bh).mean())

        cand = {
            "symbol": sym, "pattern": PATTERN, "last_ts": str(g["ts"][-1]),
            "close": round(float(close[-1]), 2),
            "base_bars": k, "base_high": round(bh, 2), "base_low": round(bl, 2),
            "base_depth_pct": round(depth * 100, 2),
            "curvature": round(a, 4), "r2": round(r2, 3), "vertex_x": round(vx, 3),
            "vee_gain": round(sh["vee_gain"], 3),
            "bottom_frac": round(sh["bottom_frac"], 2),
            "limb_ratio": round(sh["limb_ratio"], 2),
            "round_ratio": round(a / depth, 2) if depth > 1e-9 else 0.0,
            "rally_pct": round(rally_pct * 100, 2), "rally_bars": rb,
            "rally_dd_pct": round(rally_dd * 100, 2),
            "dist_from_lip_pct": round(dist * 100, 2),
            "vol_ratio": round(vr, 2), "vol_suspect": vol_suspect,
            "overhead_frac": round(overhead, 3),
            "score": 0.0,
        }
        cand["score"] = round(float(
            a * r2 * (1 - dist) * (1 - vr_scored) * (1 + rally_pct)), 5)

        if sh["vee_gain"] > p.max_vee_gain:
            inner["shape_vee"] += 1
            if shape_only is None or cand["score"] > shape_only["score"]:
                shape_only = dict(cand, shape_reject="vee_gain")
            continue
        if sh["bottom_frac"] < p.min_bottom_frac:
            inner["shape_bottom"] += 1
            if shape_only is None or cand["score"] > shape_only["score"]:
                shape_only = dict(cand, shape_reject="bottom_frac")
            continue

        k_pass.append(k)
        if best is None or cand["score"] > best["score"]:
            best = cand

    if best is not None:
        # Stability across window lengths: how many of the candidate windows
        # agreed, and over what span. One window in nineteen fitting is noise.
        best["k_pass"] = len(k_pass)
        best["k_span"] = f"{min(k_pass)}-{max(k_pass)}"
        if len(k_pass) < p.min_k_stability:
            inner["k_stability"] += 1
            if reasons is not None:
                reasons["k_stability"] += 1
            return None

    if best is None:
        if shape_rejects is not None and shape_only is not None:
            shape_rejects.append(shape_only)
        if reasons is not None:
            reasons["inner:" + (inner.most_common(1)[0][0] if inner else "none")] += 1
    return best


def attach_levels(row: dict, sl_pct: float, t1_pct: float, t2_pct: float) -> dict:
    entry = row["base_high"]
    row["entry"] = round(entry, 2)
    row["sl"] = round(entry * (1 - sl_pct), 2)
    row["t1"] = round(entry * (1 + t1_pct), 2)
    row["t2"] = round(entry * (1 + t2_pct), 2)
    # True == the fixed-% stop sits INSIDE the cup and will be hit by normal
    # chop without the pattern having failed. Surface this every time.
    row["stop_inside_base"] = row["sl"] > row["base_low"]
    row["risk_pct_to_base_low"] = round((entry - row["base_low"]) / entry * 100, 2)
    # Canonical cross-pattern keys. postfilter.py and plot_hits.py read these
    # so a second pattern does not need a second copy of either script.
    row["pattern_bars"] = row["base_bars"]
    row["leg_bars"] = row["rally_bars"]
    row["struct_high"] = row["base_high"]
    row["struct_low"] = row["base_low"]
    row["struct_stop"] = row["base_low"]
    row["risk_pct"] = row["risk_pct_to_base_low"]
    return row


def run(parquet: str, p: Params, sl=0.03, t1=0.03, t2=0.15,
        shape_rejects: list | None = None) -> list[dict]:
    df = (pl.scan_parquet(parquet)
          .select(["symbol", "ts", "open", "high", "low", "close", "volume"])
          .sort(["symbol", "ts"]).collect())
    hits = []
    n_syms = crashed = 0
    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        n_syms += 1
        try:
            r = scan_symbol(str(sym), grp, p, shape_rejects=shape_rejects)
        except Exception as e:
            # A crash here previously read as "no pattern found" -- a detector
            # bug and a quiet stock looked identical. Log it, count it, keep going.
            crashed += 1
            obs.log_exception(LOG, f"detector crashed on {sym}", e)
            continue
        if r:
            hits.append(attach_levels(r, sl, t1, t2))
    # ERROR (not just info) if the detector threw on any symbol: a nonzero count
    # means the scan silently under-covered and the threshold audit is suspect.
    (LOG.error if crashed else LOG.info)(
        "detect: %d symbols scanned, %d hits, %d crashed", n_syms, len(hits), crashed)
    return sorted(hits, key=lambda r: r["score"], reverse=True)


def diagnose(parquet: str, p: Params) -> None:
    df = (pl.scan_parquet(parquet).sort(["symbol", "ts"]).collect())
    reasons, passed, samples = Counter(), 0, []
    shape_rejects: list = []

    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        r = scan_symbol(str(sym), grp, p, reasons, shape_rejects)
        if r:
            passed += 1
        g = grp.tail(p.lookback)
        c = g["close"].to_numpy().astype(float)
        if len(c) >= 40:
            for k in (12, 16, 20, 24):
                if len(c) > k:
                    m = ind.shape_metrics(c[-k:])
                    samples.append((m["curvature"], m["r2"], m["vertex_x"],
                                    m["vee_gain"], m["bottom_frac"]))

    print(f"symbols: {df['symbol'].n_unique()}   passed: {passed}\n")
    print("rejection reasons (first failing gate):")
    for k, v in reasons.most_common():
        print(f"  {k:26s} {v}")

    if shape_rejects:
        print(f"\n{len(shape_rejects)} symbols cleared every legacy gate and died")
        print("only on the shape test (saucer vs checkmark):")
        for h in sorted(shape_rejects, key=lambda r: -r["score"])[:15]:
            print(f"  {h['symbol']:14s} {h['shape_reject']:12s} "
                  f"vee_gain {h['vee_gain']:+.2f}  bottom_frac {h['bottom_frac']:.2f}")
        print("If this list is long AND the survivors are zero, suspect the")
        print("shape thresholds before concluding the market is quiet.")

    if samples:
        arr = np.array(samples)
        print("\nuniverse distribution (p50 / p75 / p90 / p95 / p99):")
        for name, i in [("curvature", 0), ("r2", 1), ("|vertex_x|", 2),
                        ("vee_gain", 3), ("bottom_frac", 4)]:
            col = np.abs(arr[:, i]) if i == 2 else arr[:, i]
            print(f"  {name:12s}", np.round(np.percentile(col, [50, 75, 90, 95, 99]), 4))
        print("\nCompare your thresholds against these. If min_curvature sits")
        print("above p99, nothing can ever match -- that is a bug, not a quiet market.")
        print("vee_gain is a REJECT-ABOVE gate and bottom_frac a REJECT-BELOW one,")
        print("so read those two rows against max_vee_gain / min_bottom_frac.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--json", default="hits.json")
    ap.add_argument("--shape-rejects", default=None,
                    help="write hits that failed ONLY the saucer-vs-V test here")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--min-curvature", type=float, default=None)
    ap.add_argument("--min-rally", type=float, default=None)
    ap.add_argument("--min-r2", type=float, default=None)
    ap.add_argument("--base-max-depth", type=float, default=None)
    ap.add_argument("--max-dist-from-high", type=float, default=None)
    ap.add_argument("--max-vee-gain", type=float, default=None)
    ap.add_argument("--min-bottom-frac", type=float, default=None)
    ap.add_argument("--min-k-stability", type=int, default=None)
    ap.add_argument("--max-rally-dd-share", type=float, default=None)
    ap.add_argument("--sl-pct", type=float, default=0.03)
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    p = Params()
    for attr in ("min_curvature", "min_rally", "min_r2", "base_max_depth",
                 "max_dist_from_high", "max_vee_gain", "min_bottom_frac",
                 "min_k_stability", "max_rally_dd_share"):
        v = getattr(args, attr)
        if v is not None:
            setattr(p, attr, v)

    if args.diagnose:
        diagnose(args.parquet, p)
        return

    shape_rejects: list = []
    hits = run(args.parquet, p, sl=args.sl_pct, shape_rejects=shape_rejects)

    if args.shape_rejects:
        json.dump(sorted(shape_rejects, key=lambda r: -r["score"]),
                  open(args.shape_rejects, "w"), indent=2, default=str)
    if shape_rejects:
        print(f"{len(shape_rejects)} symbols passed every legacy gate but failed "
              f"the saucer-vs-V shape test"
              + (f" -> {args.shape_rejects}" if args.shape_rejects else ""))

    if not hits:
        print("no matches. Run with --diagnose before assuming the market is quiet.")
        json.dump([], open(args.json, "w"))
        return

    json.dump(hits, open(args.json, "w"), indent=2, default=str)
    pl.Config.set_tbl_rows(args.top)
    pl.Config.set_tbl_width_chars(250)
    pl.Config.set_tbl_cols(20)
    print(f"{len(hits)} raw hits -> {args.json}")
    print(pl.DataFrame(hits).head(args.top).select(
        ["symbol", "close", "rally_pct", "base_bars", "base_depth_pct",
         "curvature", "r2", "vee_gain", "bottom_frac", "k_pass",
         "dist_from_lip_pct", "vol_ratio"]))
    print("\nNext: postfilter.py (context filters), then plot_hits.py and VIEW the png.")


if __name__ == "__main__":
    main()
