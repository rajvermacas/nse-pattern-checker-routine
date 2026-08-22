"""End-to-end self-test on synthetic bars with KNOWN shapes.

The screener's failure mode is silence: a mis-set threshold returns zero hits
and looks exactly like a quiet market, and a shape gate that is too loose
returns V-bounces that look exactly like bases until someone opens the PNG.
Neither shows up in a live run until it has already wasted the run.

So: build bars whose shape we chose, push them through the real detectors, and
assert on what comes out. No network, no market, deterministic. Run this after
touching any threshold or any detector:

    python selftest_patterns.py

It exits non-zero on the first mismatch and prints what it expected.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta

import numpy as np
import polars as pl

import momentum_dip
import screener

RNG = np.random.default_rng(20260822)


def ohlc(close: np.ndarray, wick=0.004) -> dict:
    """Wrap a close path in plausible OHLC. open = previous close."""
    o = np.concatenate([[close[0]], close[:-1]])
    hi = np.maximum(o, close) * (1 + wick)
    lo = np.minimum(o, close) * (1 - wick)
    return {"open": o, "high": hi, "low": lo, "close": close}


def ramp(a: float, b: float, n: int, noise=0.002) -> np.ndarray:
    return np.linspace(a, b, n) * (1 + RNG.normal(0, noise, n))


def build(sym: str, close: np.ndarray, vol: np.ndarray, **over) -> pl.DataFrame:
    d = ohlc(close)
    d.update(over)
    t0 = datetime(2026, 6, 1, 9, 15)
    return pl.DataFrame({
        "symbol": [sym] * len(close),
        "ts": [t0 + timedelta(hours=i) for i in range(len(close))],
        "open": d["open"], "high": d["high"], "low": d["low"],
        "close": d["close"], "volume": vol,
    })


def vols(n: int, leg: slice, quiet: slice, base=200_000.0) -> np.ndarray:
    v = np.full(n, base)
    v[leg] = base * 1.8
    v[quiet] = base * 0.7
    return v


def cup_series(vee: bool) -> np.ndarray:
    """Flat -> 20% rally -> 20-bar base, rounded or V-shaped."""
    flat = ramp(95, 100, 145)
    rally = ramp(100, 120, 35)
    x = np.linspace(-1, 1, 20)
    shape = np.abs(x) if vee else x * x
    base = 120 * (1 - 0.05 * (1 - shape)) * (1 + RNG.normal(0, 0.0015, 20))
    base[-1] = 119.5
    return np.concatenate([flat, rally, base])


def dip_series(kind: str) -> np.ndarray:
    """Flat -> 25% advance -> a pullback of the requested character."""
    flat = ramp(92, 100, 100)
    adv = ramp(100, 125, 86)
    if kind == "clean":                       # orderly 6% dip, then a turn
        dip = np.array([124.0, 122.6, 121.0, 119.8, 118.6, 117.6, 118.4, 119.4])
    elif kind == "knife":                     # still falling on the last bar
        dip = np.array([123.0, 120.0, 117.0, 114.0, 111.5, 109.0, 107.0, 105.5])
    elif kind == "gap":                       # one candle did all the damage
        dip = np.array([124.6, 124.4, 117.5, 117.4, 117.6, 117.5, 117.8, 118.2])
    else:
        raise ValueError(kind)
    return np.concatenate([flat, adv, dip])


def make_universe() -> pl.DataFrame:
    frames = []

    for sym, vee in (("CUPGOOD", False), ("VBOUNCE", True)):
        c = cup_series(vee)
        frames.append(build(sym, c, vols(len(c), slice(145, 180), slice(180, None))))

    # a name in a downtrend: should never reach any gate that matters
    c = ramp(140, 100, 200)
    frames.append(build("FALLING", c, np.full(len(c), 200_000.0)))

    for sym, kind in (("DIPGOOD", "clean"), ("KNIFE", "knife"), ("GAPDIP", "gap")):
        c = dip_series(kind)
        n = len(c)
        d = ohlc(c)
        if kind == "clean":
            # last bar closes up and in the top of its own range -- the
            # stabilisation trigger the detector insists on
            d["low"][-1] = 118.3
            d["high"][-1] = 119.6
        over = {k: d[k] for k in ("open", "high", "low")}
        frames.append(build(sym, c, vols(n, slice(100, 186), slice(186, None)), **over))

    return pl.concat(frames)


def expect(name: str, got: bool, want: bool, detail: str = "") -> bool:
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {name:34s} "
          f"{'hit' if got else 'no hit':7s} (want {'hit' if want else 'no hit'}) {detail}")
    return ok


def main() -> int:
    df = make_universe()
    path = "/tmp/selftest_bars.parquet"
    df.write_parquet(path)
    print(f"synthetic universe: {df['symbol'].n_unique()} symbols, {df.height} bars\n")

    ok = True

    print("rally_cup detector:")
    rejects: list = []
    cup_hits = screener.run(path, screener.Params(), shape_rejects=rejects)
    by = {h["symbol"]: h for h in cup_hits}
    rej = {h["symbol"]: h for h in rejects}
    g = by.get("CUPGOOD")
    ok &= expect("CUPGOOD (rounded base)", "CUPGOOD" in by, True,
                 f"vee_gain {g['vee_gain']} bottom {g['bottom_frac']} "
                 f"k_pass {g['k_pass']} depth {g['base_depth_pct']}%" if g else "")
    ok &= expect("VBOUNCE (checkmark)", "VBOUNCE" in by, False,
                 f"-> shape reject on {rej['VBOUNCE']['shape_reject']}, "
                 f"vee_gain {rej['VBOUNCE']['vee_gain']}"
                 if "VBOUNCE" in rej else "(not even a shape reject)")
    ok &= expect("FALLING (downtrend)", "FALLING" in by, False)
    if "VBOUNCE" not in rej:
        print("  WARN  VBOUNCE died before the shape gates -- the shape test is")
        print("        not what rejected it, so this run does not exercise it.")
        ok = False

    print("\nmomentum_dip detector:")
    dips = momentum_dip.run(path, momentum_dip.Params())
    dby = {h["symbol"]: h for h in dips}
    d = dby.get("DIPGOOD")
    ok &= expect("DIPGOOD (orderly pullback)", "DIPGOOD" in dby, True,
                 f"adv {d['advance_pct']}% dip {d['dip_pct']}% "
                 f"retrace {d['retrace_of_advance']} trigger {d['trigger']} "
                 f"risk {d['risk_pct']}%" if d else "")
    ok &= expect("KNIFE (still falling)", "KNIFE" in dby, False)
    ok &= expect("GAPDIP (one-candle drop)", "GAPDIP" in dby, False)
    ok &= expect("CUPGOOD (no dip to buy)", "CUPGOOD" in dby, False)

    # the two screens must not be the same screen wearing a different name
    overlap = set(by) & set(dby)
    print(f"\n  {'PASS' if not overlap else 'WARN'}  patterns disjoint on this "
          f"universe{'' if not overlap else f' -- overlap: {sorted(overlap)}'}")

    print("\nOK" if ok else "\nFAILURES ABOVE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
