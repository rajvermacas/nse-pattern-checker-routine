"""Shared math for every detector in this skill.

Two rules this module exists to enforce:

1. **One EMA implementation, seeded the same way everywhere.** screener.py,
   momentum_dip.py and plot_hits.py each used to carry their own copy, and each
   seeded `out[0] = values[0]` on whatever slice it happened to hold. The
   detector fed it 120 bars, the plotter fed it 110, so the EMA a gate tested
   was not the EMA drawn on the chart used to verify that gate. Here the EMA is
   always computed on the FULL symbol history and sliced afterwards, with an SMA
   seed, so the warm-up bias is gone and the number and the picture agree.

2. **Shape metrics that can tell a saucer from a checkmark.** The parabola fit
   alone cannot: a V-bounce fits it better than a real cup does (SKILL.md step
   6). The three metrics below are cheap, scale-free, and each attacks that
   confusion from a different direction -- see `shape_metrics`.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- moving stats

_DESIGN: dict[int, np.ndarray] = {}


def design_matrix(n: int) -> np.ndarray:
    """Least-squares design for y = ax^2 + bx + c with x normalised to [-1, 1]."""
    if n not in _DESIGN:
        x = np.linspace(-1.0, 1.0, n)
        _DESIGN[n] = np.column_stack([x * x, x, np.ones(n)])
    return _DESIGN[n]


def ema(values: np.ndarray, span: int) -> np.ndarray:
    """EMA seeded with the SMA of the first `span` bars.

    Seeding with a single value (the old behaviour) leaves the series biased for
    roughly `span` bars. That never mattered at the right edge of a 420-bar
    history, but it did matter on short-history symbols and on the plotter's
    110-bar slice, where EMA50 was still unwinding its seed across the whole
    panel. Pass the full history; slice the result, not the input.
    """
    v = np.asarray(values, dtype=float)
    n = len(v)
    out = np.empty(n, dtype=float)
    if n == 0:
        return out
    s = min(span, n)
    # warm-up: expanding mean, so early bars are an average rather than a guess
    out[:s] = np.cumsum(v[:s]) / np.arange(1, s + 1)
    alpha = 2.0 / (span + 1.0)
    prev = out[s - 1]
    for i in range(s, n):
        prev = alpha * v[i] + (1.0 - alpha) * prev
        out[i] = prev
    return out


def rsi(values: np.ndarray, period: int = 14) -> np.ndarray:
    """Wilder RSI. out[0] is NaN; the first `period` values are the SMA seed."""
    v = np.asarray(values, dtype=float)
    n = len(v)
    out = np.full(n, np.nan)
    if n < period + 1:
        return out
    d = np.diff(v)
    gain, loss = np.clip(d, 0, None), -np.clip(d, None, 0)
    ag, al = gain[:period].mean(), loss[:period].mean()
    for i in range(period, n):
        if i > period:
            ag = (ag * (period - 1) + gain[i - 1]) / period
            al = (al * (period - 1) + loss[i - 1]) / period
        out[i] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    return out


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray,
        period: int = 14) -> np.ndarray:
    """Wilder ATR, aligned to `close`. Used for volatility-aware stops."""
    h, l, c = (np.asarray(x, dtype=float) for x in (high, low, close))
    n = len(c)
    out = np.full(n, np.nan)
    if n < 2:
        return out
    tr = np.maximum(h[1:] - l[1:],
                    np.maximum(np.abs(h[1:] - c[:-1]), np.abs(l[1:] - c[:-1])))
    if n <= period:
        return out
    a = tr[:period].mean()
    out[period] = a
    for i in range(period + 1, n):
        a = (a * (period - 1) + tr[i - 1]) / period
        out[i] = a
    return out


# ------------------------------------------------------------------ curve fits

def fit_parabola(y: np.ndarray) -> tuple[float, float, float, float]:
    """(curvature, r2, vertex_x, rmse) for y fit on x in [-1, 1].

    y is divided by its own mean first, so `curvature` comes out approximately
    equal to the cup's FRACTIONAL DEPTH (a 5% cup gives ~0.05) and `rmse` is a
    fraction of price, directly comparable across symbols.
    """
    y = np.asarray(y, dtype=float)
    A = design_matrix(len(y))
    m = y.mean()
    ys = y / m if m else y
    coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
    a, b, _c = coef
    resid = ys - A @ coef
    ss_res = float(resid @ resid)
    ss_tot = float(((ys - ys.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
    vx = float(-b / (2 * a)) if abs(a) > 1e-9 else 0.0
    return float(a), r2, vx, float(np.sqrt(ss_res / len(ys)))


def _vee_best(ys: np.ndarray) -> tuple[float, np.ndarray] | None:
    """(sum of squared residuals, fitted curve) for the best two-line V."""
    n = len(ys)
    if n < 6:
        return None
    x = np.linspace(-1.0, 1.0, n)
    k0 = int(np.argmin(ys))
    best = None
    for k in {max(2, k0 - 1), k0, min(n - 3, k0 + 1)}:
        if k < 2 or k > n - 3:
            continue
        ss, curve = 0.0, np.empty(n)
        for sl, xs, yseg in ((slice(0, k + 1), x[:k + 1], ys[:k + 1]),
                             (slice(k, n), x[k:], ys[k:])):
            A = np.column_stack([xs, np.ones(len(xs))])
            coef, *_ = np.linalg.lstsq(A, yseg, rcond=None)
            fit = A @ coef
            curve[sl] = fit
            r = yseg - fit
            ss += float(r @ r)
        if best is None or ss < best[0]:
            best = (ss, curve)
    return best


def fit_vee(y: np.ndarray) -> tuple[float, float]:
    """(r2, rmse) of the best two-segment straight-line 'V' through y.

    The knot is placed at the minimum, then walked one bar either side and the
    best of the three kept -- a real checkmark rarely turns exactly on its
    lowest close. Same normalisation as `fit_parabola`, so the two rmses are
    directly comparable, which is the whole point: it lets us ask "is this
    better described as two straight lines than as a curve?" rather than
    "does a curve fit it at all?", which everything passes.
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    m = y.mean()
    ys = y / m if m else y
    ss_tot = float(((ys - ys.mean()) ** 2).sum())
    best = _vee_best(ys)
    if best is None:
        return 0.0, float("inf")
    ss = best[0]
    r2 = 1.0 - ss / ss_tot if ss_tot > 1e-12 else 0.0
    return r2, float(np.sqrt(ss / n))


def fitted_curves(y: np.ndarray) -> tuple[np.ndarray, np.ndarray | None]:
    """Both fitted models back in PRICE units, for drawing on a chart.

    The plot is where the saucer-vs-checkmark call actually gets made, so it
    should show the two competing models, not just the data. Where the dashed
    V hugs the candles more tightly than the smooth parabola, the eye is
    looking at a bounce.
    """
    y = np.asarray(y, dtype=float)
    m = y.mean() or 1.0
    ys = y / m
    A = design_matrix(len(y))
    coef, *_ = np.linalg.lstsq(A, ys, rcond=None)
    par = (A @ coef) * m
    best = _vee_best(ys)
    return par, (best[1] * m if best is not None else None)


def shape_metrics(y: np.ndarray) -> dict:
    """Saucer-vs-checkmark metrics for a candidate base.

    - `vee_gain`  how much better the two-line V model fits than the parabola,
                  as a fraction of the parabola's error. Positive means the
                  shape is better described as two straight legs -> a bounce,
                  not a base. A genuine saucer sits comfortably negative.
    - `bottom_frac` share of closes in the lower third of the base's range. For
                  an ideal parabola this is ~0.58 (the curve loiters at the
                  bottom); for a straight-legged V it is ~0.33 by construction.
                  This is the one metric that survives noise well.
    - `limb_ratio` the shallower limb's slope over the steeper limb's. Reported,
                  not gated: real cups with a handle are legitimately lopsided,
                  but a 0.1 here plus a marginal chart is a fast reject by eye.
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    a, r2, vx, rmse_p = fit_parabola(y)
    r2_v, rmse_v = fit_vee(y)
    vee_gain = (rmse_p - rmse_v) / rmse_p if rmse_p > 1e-12 else 0.0

    lo, hi = float(y.min()), float(y.max())
    rng = hi - lo
    bottom_frac = float((y <= lo + rng / 3.0).mean()) if rng > 1e-12 else 1.0

    k = int(np.argmin(y))
    if 1 <= k <= n - 2:
        sl = abs((y[k] - y[0]) / k)
        sr = abs((y[-1] - y[k]) / (n - 1 - k))
        limb_ratio = float(min(sl, sr) / max(sl, sr)) if max(sl, sr) > 1e-12 else 0.0
    else:
        limb_ratio = 0.0

    return {"curvature": a, "r2": r2, "vertex_x": vx,
            "r2_vee": r2_v, "vee_gain": float(vee_gain),
            "bottom_frac": bottom_frac, "limb_ratio": limb_ratio}


def max_drawdown(values: np.ndarray) -> float:
    """Deepest peak-to-trough fall inside `values`, as a fraction of the peak."""
    v = np.asarray(values, dtype=float)
    if len(v) < 2:
        return 0.0
    peak = np.maximum.accumulate(v)
    return float((1.0 - v / peak).max())
