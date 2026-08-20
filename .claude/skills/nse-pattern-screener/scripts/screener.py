"""Rally-then-cup detector: steep rally leg into a shallow ROUNDED base that
forms near the rally high, price above rising fast EMAs, volume drying up.

CALIBRATION NOTE (the thing that bites):
The parabola is fit on price divided by its own mean, over x in [-1, 1].
Under that normalization the curvature coefficient `a` comes out roughly equal
to the cup's FRACTIONAL DEPTH -- a 5% cup gives a ~= 0.05. Across the whole NSE
universe the 99th percentile of `a` is about 0.043. So min_curvature belongs
near 0.015, NOT 0.15. Setting it an order of magnitude too high returns zero
matches on every input, which reads as "quiet market" rather than as a bug.

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


@dataclass
class Params:
    # the cup
    base_min: int = 12
    base_max: int = 30
    base_max_depth: float = 0.10
    min_curvature: float = 0.015   # ~= fractional cup depth; see note above
    min_r2: float = 0.45
    vertex_window: float = 0.65

    # the rally leg feeding it
    rally_max_bars: int = 45
    min_rally: float = 0.10
    min_slope_ratio: float = 1.5

    # cup must sit at the TOP
    base_top_vs_rally_high: float = 0.97
    max_dist_from_high: float = 0.04

    # trend + volume
    ema_fast: int = 20
    ema_slow: int = 50
    require_ema_stack: bool = True
    max_base_vol_ratio: float = 0.85

    lookback: int = 120


_DESIGN: dict[int, np.ndarray] = {}


def design_matrix(n: int) -> np.ndarray:
    if n not in _DESIGN:
        x = np.linspace(-1.0, 1.0, n)
        _DESIGN[n] = np.column_stack([x * x, x, np.ones(n)])
    return _DESIGN[n]


def fit_parabola(y: np.ndarray) -> tuple[float, float, float]:
    """Return (curvature, r2, vertex_x) for y fit on x in [-1, 1]."""
    A = design_matrix(len(y))
    ys = y / y.mean()
    coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
    a, b, _c = coef
    resid = ys - A @ coef
    ss_res = float(resid @ resid)
    ss_tot = float(((ys - ys.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
    vx = float(-b / (2 * a)) if abs(a) > 1e-9 else 0.0
    return float(a), r2, vx


def ema(values: np.ndarray, span: int) -> np.ndarray:
    alpha = 2.0 / (span + 1.0)
    out = np.empty_like(values)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return out


def scan_symbol(sym: str, df: pl.DataFrame, p: Params,
                reasons: Counter | None = None) -> dict | None:
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

    ef, es = ema(close, p.ema_fast), ema(close, p.ema_slow)
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

    for k in range(p.base_min, min(p.base_max, n - 10) + 1):
        bc = close[-k:]
        bh, bl = float(high[-k:].max()), float(low[-k:].min())

        depth = (bh - bl) / bh
        if depth > p.base_max_depth:
            inner["depth"] += 1
            continue

        a, r2, vx = fit_parabola(bc)
        if a < p.min_curvature:
            inner["curvature"] += 1
            continue
        if r2 < p.min_r2:
            inner["r2"] += 1
            continue
        if abs(vx) > p.vertex_window:
            inner["vertex"] += 1
            continue

        pre = close[: n - k]
        if len(pre) < 8:
            inner["no_rally_room"] += 1
            continue
        w = pre[-p.rally_max_bars:]
        li = int(w.argmin())
        rl = float(w[li])
        rh = float(high[: n - k][-p.rally_max_bars:][li:].max())
        rb = len(w) - li
        if rb < 5:
            inner["rally_too_short"] += 1
            continue

        rally_pct = (rh - rl) / rl
        if rally_pct < p.min_rally:
            inner["rally_pct"] += 1
            continue
        if bh < p.base_top_vs_rally_high * rh:
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

        score = a * r2 * (1 - dist) * (1 - vr) * (1 + rally_pct)
        cand = {
            "symbol": sym, "last_ts": str(g["ts"][-1]),
            "close": round(float(close[-1]), 2),
            "base_bars": k, "base_high": round(bh, 2), "base_low": round(bl, 2),
            "base_depth_pct": round(depth * 100, 2),
            "curvature": round(a, 4), "r2": round(r2, 3), "vertex_x": round(vx, 3),
            "rally_pct": round(rally_pct * 100, 2), "rally_bars": rb,
            "dist_from_lip_pct": round(dist * 100, 2),
            "vol_ratio": round(vr, 2), "score": round(float(score), 5),
        }
        if best is None or cand["score"] > best["score"]:
            best = cand

    if best is None and reasons is not None:
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
    return row


def run(parquet: str, p: Params, sl=0.03, t1=0.03, t2=0.15) -> list[dict]:
    df = (pl.scan_parquet(parquet)
          .select(["symbol", "ts", "open", "high", "low", "close", "volume"])
          .sort(["symbol", "ts"]).collect())
    hits = []
    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        try:
            r = scan_symbol(str(sym), grp, p)
        except Exception:
            continue
        if r:
            hits.append(attach_levels(r, sl, t1, t2))
    return sorted(hits, key=lambda r: r["score"], reverse=True)


def diagnose(parquet: str, p: Params) -> None:
    df = (pl.scan_parquet(parquet).sort(["symbol", "ts"]).collect())
    reasons, passed, samples = Counter(), 0, []

    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        r = scan_symbol(str(sym), grp, p, reasons)
        if r:
            passed += 1
        g = grp.tail(p.lookback)
        c = g["close"].to_numpy().astype(float)
        if len(c) >= 40:
            for k in (12, 16, 20, 24):
                if len(c) > k:
                    samples.append(fit_parabola(c[-k:]))

    print(f"symbols: {df['symbol'].n_unique()}   passed: {passed}\n")
    print("rejection reasons (first failing gate):")
    for k, v in reasons.most_common():
        print(f"  {k:26s} {v}")

    if samples:
        arr = np.array(samples)
        print("\nuniverse distribution (p50 / p75 / p90 / p95 / p99):")
        for name, i in [("curvature", 0), ("r2", 1), ("|vertex_x|", 2)]:
            col = np.abs(arr[:, i]) if i == 2 else arr[:, i]
            print(f"  {name:12s}", np.round(np.percentile(col, [50, 75, 90, 95, 99]), 4))
        print("\nCompare your thresholds against these. If min_curvature sits")
        print("above p99, nothing can ever match -- that is a bug, not a quiet market.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--json", default="hits.json")
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--min-curvature", type=float, default=None)
    ap.add_argument("--min-rally", type=float, default=None)
    ap.add_argument("--min-r2", type=float, default=None)
    ap.add_argument("--base-max-depth", type=float, default=None)
    ap.add_argument("--max-dist-from-high", type=float, default=None)
    ap.add_argument("--sl-pct", type=float, default=0.03)
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    p = Params()
    for cli, attr in [("min_curvature", "min_curvature"), ("min_rally", "min_rally"),
                      ("min_r2", "min_r2"), ("base_max_depth", "base_max_depth"),
                      ("max_dist_from_high", "max_dist_from_high")]:
        v = getattr(args, cli)
        if v is not None:
            setattr(p, attr, v)

    if args.diagnose:
        diagnose(args.parquet, p)
        return

    hits = run(args.parquet, p, sl=args.sl_pct)
    if not hits:
        print("no matches. Run with --diagnose before assuming the market is quiet.")
        return

    json.dump(hits, open(args.json, "w"), indent=2, default=str)
    pl.Config.set_tbl_rows(args.top)
    pl.Config.set_tbl_width_chars(250)
    pl.Config.set_tbl_cols(20)
    print(f"{len(hits)} raw hits -> {args.json}")
    print(pl.DataFrame(hits).head(args.top).select(
        ["symbol", "close", "rally_pct", "base_bars", "base_depth_pct",
         "curvature", "r2", "dist_from_lip_pct", "vol_ratio"]))
    print("\nNext: postfilter.py (context filters), then plot_hits.py and VIEW the png.")


if __name__ == "__main__":
    main()
