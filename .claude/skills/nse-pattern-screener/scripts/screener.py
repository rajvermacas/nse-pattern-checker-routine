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

TWO MODES
---------
1. GATED (default, unchanged): scan_symbol()/run() apply the boolean gate chain
   and return None on the first failure. Every existing caller keeps working.

2. GRADED (--preset): score_symbol()/run_flexible() convert the SAME tests into
   0-1 scores with a soft ramp -- full credit past the ideal, partial credit
   through a tolerance band, zero beyond -- then rank by a composite and label
   a tier. The point is RECALL: put 20-40 names in front of the human eye and
   let the chart do the rejecting, instead of a binary verdict returning two.

   --preset strict      tolerance band = 0  -> the ramp degenerates to the old
                        step function and the shortlist is byte-identical to
                        the gated pipeline (detector + context filters).
   --preset balanced    1x bands
   --preset exploratory 2x bands, one criterion allowed to fail outright

WHAT STAYS HARD (and why loosening it was refused)
--------------------------------------------------
pct_of_60d_high -- the ZEEL / HINDCOPPER trap. A stock that fell 20% and
bounced shows a rally and a base near the WINDOW high while sitting far below
the real one. The detector's 120-bar window CANNOT see this, and neither can a
reviewer looking at a 120-bar chart, so no amount of eyeballing corrects for
it. It is never scored, never ramped: failing names are removed from the
shortlist into a separate `hard_excluded` list with their numbers attached.

V-shape -- a V fits a parabola BETTER than a real cup (SKILL.md step 6). Two
defences, one structural and one advisory:
  * STRUCTURAL: `vertex_window` is the documented numeric defence against
    V-bounces (references/parameters.md). It still gets a tolerance band so
    near-misses are visible, but a name whose only miss is `vertex` is capped
    at tier C -- loosening the vertex window can therefore never promote a
    V-bounce into A or B. Tier A is by construction "passes every gate at its
    ideal", so no loosening of anything reaches A.
  * ADVISORY: a `shape` score (leg symmetry, with a flat-shelf penalty) feeds
    the composite ranking with the largest single weight. It is a RANKING
    signal only. It does not gate, because it was measured against the
    labelled batch and does not reliably separate V from cup -- see the caveat
    on shape_quality(). The eye is still the filter.

Usage:
    python screener.py --parquet all_closed.parquet --json hits.json
    python screener.py --parquet all_closed.parquet --diagnose
    python screener.py --parquet all_closed.parquet --preset balanced \
                       --json flex.json --bars-per-day 7
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass

import numpy as np
import polars as pl

import obs

LOG = obs.get_logger("detect")


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

    # Context ideals. GRADED MODE ONLY -- these mirror postfilter.py's cuts so
    # that bar_share and turnover can be SCORED instead of silently deleting a
    # name. scan_symbol()/run() ignore them entirely, so the gated pipeline is
    # unchanged and postfilter.py remains the authority there.
    max_bar_share: float = 0.50
    min_turnover_cr: float = 5.0


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


# =====================================================================
#  GRADED MODE
# =====================================================================
# Every gate above becomes a 0-1 score. Ideal == the gated threshold, so
# score 1.0 is exactly "would have passed the old gate" and preset=strict
# (band 0) reproduces the gated pipeline exactly.


@dataclass
class Criterion:
    """One test, as a soft ramp instead of a boolean.

    One-sided by default. Set ideal_max/band_max for a SWEET SPOT criterion --
    full credit inside [ideal, ideal_max], ramping off on both sides. Used by
    depth_fit, where "bigger is better" is actively wrong: a monotone-in-depth
    reward is what drags the k-sweep onto the longest window and floats random
    walks up the ranking.
    """
    name: str
    ideal: float           # the gated threshold; >= ideal (or <=) scores 1.0
    band: float            # tolerance width at 1x; score hits 0.0 at ideal-+band
    higher_is_better: bool
    weight: float          # share of the composite
    fmt: str = "{:.3f}"
    ideal_max: float | None = None
    band_max: float = 0.0

    def score(self, value: float, tol: float) -> float:
        b = self.band * tol
        if self.ideal_max is not None:
            lo = 1.0 if value >= self.ideal else (
                0.0 if b <= 0 else max(0.0, (value - (self.ideal - b)) / b))
            bm = self.band_max * tol
            hi = 1.0 if value <= self.ideal_max else (
                0.0 if bm <= 0 else max(0.0, ((self.ideal_max + bm) - value) / bm))
            return min(lo, hi)
        if self.higher_is_better:
            if value >= self.ideal:
                return 1.0
            if b <= 0:
                return 0.0
            return max(0.0, (value - (self.ideal - b)) / b)
        if value <= self.ideal:
            return 1.0
        if b <= 0:
            return 0.0
        return max(0.0, ((self.ideal + b) - value) / b)


def build_criteria(p: "Params") -> dict[str, Criterion]:
    """Ideals are read off Params so --min-curvature etc. still move them.

    Weights are NOT uniform, for two measured reasons:

    * `r2` is nearly worthless as shape evidence. The parabolic model NESTS the
      linear term, so a pure straight line at any slope scores r2 = 1.000. R2
      measures absence of noise, not roundedness -- so it is weighted as a
      cleanliness term (0.5) and the shape evidence comes from depth_fit,
      vertex/centring and shape instead.
    * raw `a` is only the cup's fractional depth when the vertex is CENTRED.
      The verified relation is depth ~= a * (1 + |vx|)^2, so with |vx| <= 0.65
      admitted, raw `a` understates depth by up to 2.72x, and sweeping k moves
      `a` 6x on a fixed 7% cup. The raw-`a` gate is kept (strict must
      reproduce) but weighted down to 0.6; the vertex-corrected depth_fit
      carries the shape weight instead.
    """
    C = Criterion
    return {c.name: c for c in [
        # --- the cup ---
        C("curvature",  p.min_curvature,        0.007, True,  0.6, "{:.4f}"),
        C("r2",         p.min_r2,               0.12,  True,  0.5),
        C("vertex",     p.vertex_window,        0.55,  False, 1.2),
        C("base_depth", p.base_max_depth,       0.05,  False, 1.0),
        # --- the rally leg ---
        C("rally",      p.min_rally,            0.04,  True,  0.8),
        C("slope_ratio", p.min_slope_ratio,     0.80,  True,  0.5, "{:.2f}"),
        # --- cup must sit at the TOP ---
        C("base_top",   p.base_top_vs_rally_high, 0.04, True, 1.0),
        C("dist_from_lip", p.max_dist_from_high, 0.03,  False, 0.8),
        # --- trend + volume ---
        C("ema_stack",  1.0,                    0.030, True,  1.2),
        C("vol_dryup",  p.max_base_vol_ratio,   0.35,  False, 0.8),
        # --- context, folded in from postfilter.py so it can be SCORED ---
        C("bar_share",  p.max_bar_share,        0.30,  False, 1.0, "{:.2f}"),
        C("turnover",   p.min_turnover_cr,      3.50,  True,  0.6, "{:.2f}"),
        # --- advisory: rank only. Never gate, never counted as a miss. ---
        # vertex-corrected fractional depth, as a SWEET SPOT: below min_curvature
        # it is not a cup, above ~6% it is a correction (and base_max_depth is
        # the hard ceiling at 10%). Deliberately non-monotone in depth.
        C("depth_fit",  p.min_curvature, 0.007, True, 1.2, "{:.3f}",
          ideal_max=0.060, band_max=p.base_max_depth - 0.060),
        # how centred the turn is. |vx| near 0 is a real cup; the gate only asks
        # <= 0.65, which gives no ranking gradient, so this supplies one and
        # penalises extreme vertices explicitly.
        C("centring",   0.25,                   0.75,  False, 1.0, "{:.2f}"),
        C("shape",      1.0,                    1.00,  True,  1.5, "{:.2f}"),
    ]}


# Which group a criterion belongs to. The split matters:
#   DETECTOR -- exactly scan_symbol()'s gate chain, so DETECTOR_CRIT all scoring
#               1.0 == "would have been a raw hit". Reproduces hits.json.
#   CONTEXT  -- postfilter.py's scored cuts. Reproduces hits_clean.json.
#   ADVISORY -- shape. Never gates, never counted as a miss; it only subtracts
#               from the composite and caps the tier at C when it is 0.
DETECTOR_CRIT = ("curvature", "r2", "vertex", "base_depth", "rally",
                 "slope_ratio", "base_top", "dist_from_lip", "ema_stack",
                 "vol_dryup")
CONTEXT_CRIT = ("bar_share", "turnover")
ADVISORY_CRIT = ("depth_fit", "centring", "shape")
GATE_CRIT = DETECTOR_CRIT + CONTEXT_CRIT

# Criteria that may never take the preset's "one free failure". A score of 0
# on these does not mean "a loose cup" -- it means the OPPOSITE SHAPE, so
# admitting them is not extra recall, it is pure noise:
#   curvature  score 0 at a <= ~0  ->  an inverted parabola. A dome, not a cup.
#   vol_dryup  score 0 at vr > 1.5 ->  base volume EXPANDING vs the rally, which
#                                      is the opposite of a dry-up (SIGMAADV
#                                      measured 15.8x and was floating into the
#                                      exploratory top ten on its free zero).
# bar_share deliberately stays free-zero-able: a one-candle leg is a real if
# different setup (gap-and-base), so it is admitted with a GAP_DRIVEN flag
# rather than deleted.
NO_FREE_ZERO = ("curvature", "vol_dryup")


PRESETS: dict[str, dict] = {
    # tol      = multiplier on every band. 0 -> the ramp is a step function.
    # max_zero = how many criteria may score exactly 0.0 and still be admitted.
    # min_composite = floor on the weighted score.
    # Bands and floors are tuned so balanced and exploratory both land in the
    # 20-40 range on a 107-name universe. That is the design target: the
    # numeric stage is high-RECALL and the human eye is the precision stage,
    # so a shortlist that returns single digits has failed, and one that
    # returns 75 is unreviewable.
    "strict":      {"tol": 0.0, "max_zero": 0, "min_composite": 0.00},
    "balanced":    {"tol": 1.0, "max_zero": 0, "min_composite": 0.60},
    "exploratory": {"tol": 2.0, "max_zero": 1, "min_composite": 0.82},
}


def shape_quality(bc: np.ndarray) -> tuple[float, float, float]:
    """Advisory shape descriptor. READ THE CAVEAT.

    Two measurements over the base closes:
      leg_sym    -- min/max of the two legs' per-bar slopes about the low. A
                    5-bars-down / 2-bars-up snapback (the TMB shape) scores low.
      floor_frac -- share of bars in the bottom third of the base range. A V
                    touches the floor once; a saucer dwells; a flat SHELF sits
                    there the whole time. So both extremes are penalised --
                    real cups in this batch measure 0.23-0.40.

    CAVEAT, measured not assumed: this does NOT reliably separate a V-bounce
    from a cup. Fitting an explicit two-segment V model against the parabola
    and comparing residuals was tried on the labelled batch and came out
    BACKWARDS -- the kink-searched V fit PAYTM (a confirmed cup) better than it
    fit BLISSGVS (a confirmed V-dip). SKILL.md is right that no threshold
    separates these; only looking does. leg_sym merely correlates: the five
    visually-confirmed names in the reference batch all sit >= 0.66 while most
    of the visually-rejected ones sit lower. That is good enough to RANK on and
    nowhere near good enough to GATE on, which is why this never gates.
    """
    k = len(bc)
    lo, hi = float(bc.min()), float(bc.max())
    rng = hi - lo
    if rng <= 1e-12 or k < 4:
        return 0.0, 0.0, 0.0
    floor_frac = float((bc <= lo + rng / 3.0).sum()) / k
    i = int(bc.argmin())
    lbars, rbars = max(i, 1), max(k - 1 - i, 1)
    lslope = (bc[0] - lo) / lbars
    rslope = (bc[-1] - lo) / rbars
    leg_sym = (0.0 if max(lslope, rslope) <= 1e-12
               else float(min(lslope, rslope) / max(lslope, rslope)))
    sym_q = min(1.0, leg_sym / 0.70)
    # flat-shelf penalty: nothing below 0.55, dead by 0.85
    shelf_q = 1.0 if floor_frac <= 0.55 else max(0.0, (0.85 - floor_frac) / 0.30)
    return sym_q * shelf_q, floor_frac, leg_sym


def _ema_stack_score(close, ef, es, base_min: int) -> float:
    """Graded version of `close > ema20 > ema50 and ema20 rising`.

    Expressed as ratios so one band (3% at 1x) covers all three sub-tests.
    """
    s = [close[-1] / ef[-1], ef[-1] / es[-1]]
    j = min(base_min, len(ef) - 1)
    s.append(ef[-1] / ef[-j] if ef[-j] > 0 else 0.0)
    return float(min(s))


def score_symbol(sym: str, df: pl.DataFrame, p: "Params", crit: dict,
                 tol: float, bars_per_day: int = 7,
                 high_window: int | None = None) -> dict | None:
    """Graded twin of scan_symbol(). Returns the best-scoring base window.

    Never returns None for "failed a threshold" -- only for "not enough bars to
    form the question". Admission is the caller's decision, made on the scores.
    """
    if df.height < p.base_min + 20:
        return None

    g = df.tail(p.lookback)
    close = g["close"].to_numpy().astype(float)
    high = g["high"].to_numpy().astype(float)
    low = g["low"].to_numpy().astype(float)
    vol = g["volume"].to_numpy().astype(float)
    n = len(close)

    ef, es = ema(close, p.ema_fast), ema(close, p.ema_slow)
    ema_v = _ema_stack_score(close, ef, es, p.base_min)

    # HARD, not scored: the 60-day high is outside the detector window, so a
    # reviewer looking at the chart cannot correct for it. Measured on the FULL
    # frame (or the last `high_window` bars), not the 120-bar lookback.
    fh = df["high"].to_numpy().astype(float)
    if high_window:
        fh = fh[-high_window:]
    full_high = float(fh.max()) if len(fh) else float(high.max())

    fc = df["close"].to_numpy().astype(float)[-120:]
    fv = df["volume"].to_numpy().astype(float)[-120:]
    turnover = float(np.median(fc * fv) / 1e7 * bars_per_day)

    best = None
    for k in range(p.base_min, min(p.base_max, n - 10) + 1):
        bc = close[-k:]
        bh, bl = float(high[-k:].max()), float(low[-k:].min())
        depth = (bh - bl) / bh
        a, r2, vx = fit_parabola(bc)

        pre = close[: n - k]
        if len(pre) < 8:
            continue
        w = pre[-p.rally_max_bars:]
        li = int(w.argmin())
        rl = float(w[li])
        rh = float(high[: n - k][-p.rally_max_bars:][li:].max())
        rb = len(w) - li
        if rb < 5 or rl <= 0:
            continue

        rally_pct = (rh - rl) / rl
        rs = (rh - rl) / rb / rl
        bs = abs(bc[-1] - bc[0]) / k / bc[0]
        slope_ratio = 99.0 if bs <= 1e-9 else rs / bs
        dist = (bh - close[-1]) / bh
        rv = float(vol[n - k - rb: n - k].mean())
        bv = float(vol[-k:].mean())
        vr = bv / rv if rv > 0 else 99.0

        # replicate postfilter.py's bar_share exactly (closes over the leg)
        seg = fc[len(fc) - k - rb: len(fc) - k] if len(fc) >= k + rb else np.array([])
        if len(seg) > 2:
            tot = seg[-1] - seg[0]
            bar_share = float(np.diff(seg).max() / tot) if tot > 0 else 9.9
        else:
            bar_share = 9.9

        shape_q, floor_frac, leg_sym = shape_quality(bc)

        vals = {
            "curvature": a, "r2": r2, "vertex": abs(vx), "base_depth": depth,
            "rally": rally_pct, "slope_ratio": slope_ratio,
            "base_top": bh / rh if rh > 0 else 0.0, "dist_from_lip": dist,
            "ema_stack": ema_v, "vol_dryup": vr, "bar_share": bar_share,
            "turnover": turnover, "shape": shape_q,
            # depth ~= a*(1+|vx|)^2. Raw `a` is the cup depth ONLY for a
            # centred vertex; off-centre it understates by up to 2.72x at the
            # admitted |vx| <= 0.65, and it drifts ~6x as k sweeps 12->28 on a
            # fixed 7% cup. This is the stable quantity, so this is what ranks.
            "depth_fit": a * (1.0 + abs(vx)) ** 2,
            "centring": abs(vx),
        }
        scores = {nm: crit[nm].score(v, tol) for nm, v in vals.items()
                  if nm not in ADVISORY_CRIT}
        # shape is a quality measure, not a gate: it is always graded at 1x so
        # that --preset strict (band 0, everything else a step) still ranks and
        # still flags Vs, instead of collapsing it to a 13th boolean.
        for nm in ADVISORY_CRIT:
            scores[nm] = crit[nm].score(vals[nm], 1.0)

        def _wavg(names):
            w = sum(crit[nm].weight for nm in names)
            return sum(scores[nm] * crit[nm].weight for nm in names) / w
        det_comp, ctx_comp = _wavg(DETECTOR_CRIT), _wavg(CONTEXT_CRIT)
        composite = _wavg(list(scores))
        legacy = a * r2 * (1 - dist) * (1 - vr) * (1 + rally_pct)

        # Window choice mirrors the documented pipeline: the DETECTOR picks the
        # base window, postfilter judges whatever it picked. So the key leads
        # with the detector gates -- context is deliberately NOT in it, or the
        # graded scan would quietly pick a friendlier window than the gated one
        # and --preset strict would stop reproducing.
        #
        # The TIE-BREAK is preset-dependent, on purpose:
        #   tol == 0  -> the legacy score, which is what scan_symbol() uses, so
        #                the chosen window is identical and strict reproduces
        #                today's output *including* today's known bias: legacy
        #                is monotone increasing in `a`, so it lands on the
        #                longest/deepest qualifying k ~24% of the time versus
        #                ~5% expected, while postfilter then ranks
        #                shallowest-first. The two disagree. That is today's
        #                behaviour and strict's job is to reproduce it.
        #   tol > 0   -> the composite, i.e. THE SAME QUANTITY THE SHORTLIST IS
        #                RANKED BY. depth_fit is a sweet spot rather than
        #                monotone, so the long-k / random-walk bias is gone.
        key = (round(det_comp, 9), legacy if tol <= 0 else composite)
        if best is None or key > best["_key"]:
            best = {"_k": k, "_vals": vals, "_scores": scores, "_key": key,
                    "_composite": composite, "_det": det_comp, "_ctx": ctx_comp,
                    "_bh": bh, "_bl": bl, "_rb": rb,
                    "_depth": depth, "_a": a, "_r2": r2, "_vx": vx,
                    "_rally": rally_pct, "_dist": dist, "_vr": vr,
                    "_floor": floor_frac, "_sym": leg_sym}

    if best is None:
        return None

    vals, scores = best["_vals"], best["_scores"]
    # Cost list: which criteria took points off, worst first. This is the
    # column a human triages on -- "bar_share 0.57 vs 0.50" is the useful bit.
    costs = []
    for nm, s in scores.items():
        adv = nm in ADVISORY_CRIT
        # shape never reaches 1.0 on a real chart, so listing it as a "cost"
        # on every single row would drown the column. Show it only when it is
        # actually saying something.
        if s >= (0.75 if adv else 0.999):
            continue
        c = crit[nm]
        lbl = (f"{nm} {c.fmt.format(vals[nm])} (weak shape)" if adv
               else f"{nm} {c.fmt.format(vals[nm])} vs {c.fmt.format(c.ideal)}")
        costs.append({
            "criterion": nm, "value": float(vals[nm]), "ideal": c.ideal,
            "score": round(s, 3), "advisory": adv, "label": lbl,
            "points_lost": round((1 - s) * c.weight, 3)})
    costs.sort(key=lambda d: -d["points_lost"])

    n_zero = sum(1 for nm in GATE_CRIT if scores[nm] <= 0.0)
    hard_zero = any(scores[nm] <= 0.0 for nm in NO_FREE_ZERO)
    n_miss = sum(1 for nm in GATE_CRIT if scores[nm] < 0.999)
    detector_pass = all(scores[nm] >= 0.999 for nm in DETECTOR_CRIT)

    # Tier is strict-gate accounting, so nothing can be promoted by loosening.
    if n_miss == 0:
        tier = "A"
    elif n_miss == 1 and n_zero == 0:
        tier = "B"
    else:
        tier = "C"
    flags = []
    # THE V DEFENCE. vertex_window is the documented numeric defence against
    # V-bounces, so a widened vertex band is exactly the loosening that would
    # smuggle one in. Give it a band (the near-miss stays visible) but refuse
    # to let a vertex miss buy tier B.
    if tier == "B" and scores["vertex"] < 0.999:
        tier = "C"
        flags.append("VERTEX_LOOSENED")
    if scores["shape"] < 0.40:
        # loud, and it caps the tier -- but it is a RANKING signal, so the cap
        # only ever demotes. See shape_quality()'s caveat.
        flags.append("SHAPE_WEAK")
        tier = "C" if tier == "C" else tier
    if scores["bar_share"] <= 0.0:
        flags.append("GAP_DRIVEN")
    if scores["turnover"] <= 0.0:
        flags.append("ILLIQUID")

    k = best["_k"]
    pct_high = best["_bh"] / full_high * 100 if full_high > 0 else 0.0
    row = {
        "symbol": sym, "tier": tier, "composite": round(best["_composite"], 4),
        "detector_pass": detector_pass,
        "last_ts": str(g["ts"][-1]), "close": round(float(close[-1]), 2),
        "base_bars": k, "base_high": round(best["_bh"], 2),
        "base_low": round(best["_bl"], 2),
        "base_depth_pct": round(best["_depth"] * 100, 2),
        "curvature": round(best["_a"], 4), "r2": round(best["_r2"], 3),
        "vertex_x": round(best["_vx"], 3),
        "rally_pct": round(best["_rally"] * 100, 2), "rally_bars": best["_rb"],
        "dist_from_lip_pct": round(best["_dist"] * 100, 2),
        "vol_ratio": round(best["_vr"], 2),
        "bar_share": round(vals["bar_share"], 2),
        "turnover_cr": round(vals["turnover"], 2),
        "pct_of_60d_high": round(pct_high, 1),
        "shape_score": round(vals["shape"], 3),
        "depth_from_fit_pct": round(vals["depth_fit"] * 100, 2),
        "floor_frac": round(best["_floor"], 2), "leg_sym": round(best["_sym"], 2),
        "scores": {nm: round(s, 3) for nm, s in scores.items()},
        "costs": costs, "cost_summary": "; ".join(c["label"] for c in costs[:3]) or "-",
        "n_missed": n_miss, "n_zero": n_zero, "hard_zero": hard_zero,
        "flags": flags,
        "score": round(float(best["_a"] * best["_r2"] * (1 - best["_dist"])
                             * (1 - best["_vr"]) * (1 + best["_rally"])), 5),
    }
    return row


def run_flexible(parquet: str, p: "Params", preset: str = "balanced",
                 sl=0.03, t1=0.03, t2=0.15, bars_per_day: int = 7,
                 high_window: int | None = None,
                 min_pct_60d_high: float = 97.0,
                 tol: float | None = None,
                 max_zero: int | None = None,
                 min_composite: float | None = None) -> dict:
    """Graded scan. Returns {"candidates": [...], "hard_excluded": [...], ...}.

    Ranked by composite descending: the reviewer works down the list and stops
    when quality drops off, rather than opening 40 charts in arbitrary order.
    """
    cfg = dict(PRESETS[preset])
    if tol is not None:
        cfg["tol"] = tol
    if max_zero is not None:
        cfg["max_zero"] = max_zero
    if min_composite is not None:
        cfg["min_composite"] = min_composite

    crit = build_criteria(p)
    df = (pl.scan_parquet(parquet)
          .select(["symbol", "ts", "open", "high", "low", "close", "volume"])
          .sort(["symbol", "ts"]).collect())

    kept, excluded, detector_hits = [], [], []
    n_syms = crashed = skipped = 0
    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        n_syms += 1
        try:
            r = score_symbol(str(sym), grp, p, crit, cfg["tol"],
                             bars_per_day, high_window)
        except Exception as e:
            crashed += 1
            obs.log_exception(LOG, f"graded detector crashed on {sym}", e)
            continue
        if r is None:
            skipped += 1
            continue
        attach_levels(r, sl, t1, t2)
        if r["detector_pass"]:
            detector_hits.append(r["symbol"])
        admissible = (r["n_zero"] <= cfg["max_zero"]
                      and not r["hard_zero"]
                      and r["composite"] >= cfg["min_composite"])
        # HARD exclusion -- see module docstring. Listed with its numbers so
        # the count is auditable, but never in the shortlist. Only names that
        # would otherwise have been shortlisted are listed, so this stays a
        # readable "here is what the trap ate" rather than a universe dump.
        if r["pct_of_60d_high"] < min_pct_60d_high:
            if admissible:
                r["excluded_reason"] = (
                    f"downtrend-bounce trap: base high is "
                    f"{r['pct_of_60d_high']}% of the full-history high "
                    f"(floor {min_pct_60d_high}%)")
                excluded.append(r)
            continue
        if not admissible:
            continue
        kept.append(r)

    kept.sort(key=lambda r: -r["composite"])
    excluded.sort(key=lambda r: -r["composite"])
    (LOG.error if crashed else LOG.info)(
        "graded[%s]: %d scanned, %d shortlisted, %d hard-excluded, "
        "%d too-short, %d crashed", preset, n_syms, len(kept), len(excluded),
        skipped, crashed)
    return {
        "preset": preset, "tolerance": cfg["tol"],
        "max_zero": cfg["max_zero"], "min_composite": cfg["min_composite"],
        "scanned": n_syms,
        "tiers": {t: sum(1 for r in kept if r["tier"] == t) for t in "ABC"},
        # every symbol whose 10 DETECTOR gates all scored 1.0 -- i.e. exactly
        # what the old run()/hits.json would have contained. Kept for the
        # strict-reproduction audit even when context scoring drops the name.
        "detector_pass_symbols": sorted(detector_hits),
        "candidates": kept, "hard_excluded": excluded,
    }


def print_flexible(res: dict, top: int = 60) -> None:
    t = res["tiers"]
    print(f"\npreset={res['preset']}  tol={res['tolerance']}x  "
          f"scanned={res['scanned']}  shortlist={len(res['candidates'])}  "
          f"(A={t['A']} B={t['B']} C={t['C']})  "
          f"hard-excluded={len(res['hard_excluded'])}")
    print(f"{'#':>3} {'T':1} {'score':>5} {'symbol':<12} {'close':>9} "
          f"{'lip':>9} {'dep%':>5} {'rrr':>4}  what cost it points")
    print("-" * 118)
    for i, r in enumerate(res["candidates"][:top], 1):
        rrr = 15.0 / r["base_depth_pct"] if r["base_depth_pct"] else 0
        fl = (" [" + ",".join(r["flags"]) + "]") if r["flags"] else ""
        print(f"{i:>3} {r['tier']:1} {r['composite']:>5.3f} {r['symbol']:<12} "
              f"{r['close']:>9.2f} {r['base_high']:>9.2f} "
              f"{r['base_depth_pct']:>5.2f} {rrr:>4.1f}  {r['cost_summary']}{fl}")
    if res["hard_excluded"]:
        print(f"\nHARD-EXCLUDED ({len(res['hard_excluded'])}) -- downtrend bounce into "
              f"overhead supply; invisible on a 120-bar chart, so not scored:")
        for r in res["hard_excluded"]:
            print(f"    {r['symbol']:<12} base high at {r['pct_of_60d_high']}% "
                  f"of the full-history high  (would have been tier {r['tier']})")
    print("\nTiers are strict-gate accounting: A = passes every gate at its ideal,")
    print("B = misses exactly one inside tolerance, C = everything else admitted.")
    print("Ranked best-first. This is a shortlist for the EYE -- plot_hits.py and")
    print("VIEW the charts. Candidates, not recommendations.")


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
    n_syms = crashed = 0
    for (sym,), grp in df.group_by(["symbol"], maintain_order=True):
        n_syms += 1
        try:
            r = scan_symbol(str(sym), grp, p)
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

    # ---- graded mode (additive; omit --preset and nothing below applies) ----
    ap.add_argument("--preset", choices=sorted(PRESETS), default=None,
                    help="graded mode: strict|balanced|exploratory. strict "
                         "reproduces the gated pipeline exactly.")
    ap.add_argument("--base-min", type=int, default=None)
    ap.add_argument("--base-max", type=int, default=None)
    ap.add_argument("--rally-max-bars", type=int, default=None)
    ap.add_argument("--lookback", type=int, default=None)
    ap.add_argument("--bars-per-day", type=int, default=7,
                    help="7 NSE hourly, 25 for 15m, 1 for daily (turnover scale)")
    ap.add_argument("--high-window-bars", type=int, default=None,
                    help="bars used for the at-high test; default = whole file")
    ap.add_argument("--min-pct-60d-high", type=float, default=97.0,
                    help="HARD exclusion floor; the one thing not softened")
    ap.add_argument("--max-bar-share", type=float, default=None)
    ap.add_argument("--min-turnover-cr", type=float, default=None)
    ap.add_argument("--tol", type=float, default=None,
                    help="override the preset's tolerance multiplier")
    ap.add_argument("--max-zero", type=int, default=None,
                    help="how many criteria may score 0 and still be admitted")
    ap.add_argument("--min-composite", type=float, default=None)
    args = ap.parse_args()

    p = Params()
    for attr in ["min_curvature", "min_rally", "min_r2", "base_max_depth",
                 "max_dist_from_high", "base_min", "base_max", "rally_max_bars",
                 "lookback", "max_bar_share", "min_turnover_cr"]:
        v = getattr(args, attr, None)
        if v is not None:
            setattr(p, attr, v)

    if args.preset:
        res = run_flexible(args.parquet, p, preset=args.preset, sl=args.sl_pct,
                           bars_per_day=args.bars_per_day,
                           high_window=args.high_window_bars,
                           min_pct_60d_high=args.min_pct_60d_high,
                           tol=args.tol, max_zero=args.max_zero,
                           min_composite=args.min_composite)
        json.dump(res, open(args.json, "w"), indent=2, default=str)
        print_flexible(res, top=max(args.top, 60))
        print(f"\n-> {args.json}")
        return

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
