"""Render candlestick panels for every hit so they can be visually verified.

This step is not decoration. A V-shaped reversal fits a parabola BEAUTIFULLY --
often better than a genuine rounded base. Curvature cannot tell "rounded" from
"sharp bounce"; no threshold reliably separates them. Looking does.

To make the looking faster, a cup panel draws BOTH competing models over the
base: the solid curve is the parabola, the dashed one is the best two-straight-
line V. Where the dashed line hugs the candles more tightly than the curve, you
are looking at a bounce -- that judgement used to be pure eyeballing.

Dip panels instead draw the swing high (the level being retraced), the dip low
(the structural stop) and the entry, because the question there is different:
not "is this shape round" but "is this fall over, and how far is the stop".

After running this, open the PNG with the `view` tool and read the panels
BEFORE writing the report.

These are matplotlib renderings of yfinance data, not screenshots from any
charting platform. EMA seeding and session handling differ from TradingView and
Kite, so treat them as shape verification, not price truth. The EMAs here come
from the same function the detector used, computed on the same full history,
so the line you see IS the line the gate tested.

Usage:
    python plot_hits.py --hits hits_clean.json --parquet all_closed.parquet --out hits.png
"""

from __future__ import annotations

import argparse
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

import indicators as ind

BG, UP, DOWN = "#131722", "#26a69a", "#ef5350"
EMA_F, EMA_S, MARK = "#e6d84a", "#9ad14b", "#ff9800"
FIT, VFIT, STOP = "#4fc3f7", "#ff7043", "#ef5350"

TITLES = {
    "rally_cup": "NSE hourly - rally + rounded base near highs",
    "momentum_dip": "NSE hourly - dips in strong momentum names",
}


def panel_cup(ax, h, c, hi, lo, n):
    k = int(h.get("pattern_bars", h.get("base_bars", 0)) or 0)
    if k:
        ax.axvspan(n - k - 0.5, n - 0.5, color=MARK, alpha=0.13)
        base = c[-k:]
        par, vee = ind.fitted_curves(base)
        xs = np.arange(n - k, n)
        ax.plot(xs, par, color=FIT, lw=1.6, zorder=5)
        if vee is not None:
            ax.plot(xs, vee, color=VFIT, lw=1.2, ls="--", alpha=0.9, zorder=5)
    lip = h.get("struct_high", h.get("base_high"))
    if lip:
        ax.axhline(lip, color=MARK, ls="--", lw=1)
    if h.get("struct_low"):
        ax.axhline(h["struct_low"], color=STOP, ls=":", lw=1)
    return (f"{h['symbol']}  rally {h.get('rally_pct','?')}%  base {k}b  "
            f"depth {h.get('base_depth_pct','?')}%\n"
            f"R2 {h.get('r2','?')}  vee {h.get('vee_gain','?')}  "
            f"btm {h.get('bottom_frac','?')}  k {h.get('k_pass','?')}")


def panel_dip(ax, h, c, hi, lo, n):
    k = int(h.get("pattern_bars", 0) or 0)
    rb = int(h.get("leg_bars", 0) or 0)
    if k:
        ax.axvspan(n - k - 0.5, n - 0.5, color=STOP, alpha=0.12)
    if rb:
        ax.axvspan(n - k - rb - 0.5, n - k - 0.5, color=UP, alpha=0.07)
    if h.get("struct_high"):
        ax.axhline(h["struct_high"], color=MARK, ls="--", lw=1)
    if h.get("struct_low"):
        ax.axhline(h["struct_low"], color=STOP, ls="-", lw=1.2)
    if h.get("entry"):
        ax.axhline(h["entry"], color=FIT, ls=":", lw=1.2)
    return (f"{h['symbol']}  adv {h.get('advance_pct','?')}%  "
            f"dip {h.get('dip_pct','?')}% / {k}b\n"
            f"retr {h.get('retrace_of_advance','?')}  "
            f"vol {h.get('dip_vol_ratio','?')}  rsi {h.get('rsi','?')}  "
            f"{h.get('trigger','?')}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", required=True)
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="hits.png")
    ap.add_argument("--bars", type=int, default=110)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--ema-fast", type=int, default=20)
    ap.add_argument("--ema-slow", type=int, default=50)
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    hits = json.load(open(args.hits))
    if not hits:
        print("nothing to plot")
        return

    pattern = hits[0].get("pattern", "rally_cup")
    title = args.title or TITLES.get(pattern, TITLES["rally_cup"])

    df = pl.read_parquet(args.parquet).sort(["symbol", "ts"])
    cols = min(args.cols, len(hits))
    rows = math.ceil(len(hits) / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5.4 * cols, 4.0 * rows),
                             facecolor=BG, squeeze=False)
    flat = axes.ravel()

    for ax, h in zip(flat, hits):
        g = df.filter(pl.col("symbol") == h["symbol"])
        # EMAs on the FULL history, sliced to the panel -- same call the
        # detector makes. Computing them on the 110-bar slice made the plotted
        # EMA50 a different line from the one the gate tested.
        c_full = g["close"].to_numpy().astype(float)
        ef = ind.ema(c_full, args.ema_fast)[-args.bars:]
        es = ind.ema(c_full, args.ema_slow)[-args.bars:]
        g = g.tail(args.bars)
        o = g["open"].to_numpy(); c = g["close"].to_numpy()
        hi = g["high"].to_numpy(); lo = g["low"].to_numpy()
        n = len(c)
        x = np.arange(n)
        up = c >= o
        colors = np.where(up, UP, DOWN)

        ax.vlines(x, lo, hi, color=colors, lw=0.7)
        ax.bar(x, c - o, bottom=o, color=colors, width=0.65, linewidth=0)
        ax.plot(x, ef, color=EMA_F, lw=1.1)
        ax.plot(x, es, color=EMA_S, lw=1.1)

        draw = panel_dip if pattern == "momentum_dip" else panel_cup
        ax.set_title(draw(ax, h, c, hi, lo, n), color="w", fontsize=9)
        ax.set_facecolor(BG)
        ax.tick_params(colors="#777", labelsize=7)
        for s in ax.spines.values():
            s.set_color("#333")
        ax.grid(alpha=0.12, color="#555")

    for ax in flat[len(hits):]:
        ax.set_visible(False)

    # last_ts varies per symbol -- Yahoo may not yet have published the newest
    # bar for every ticker at fetch time. hits[0] would stamp whatever the
    # top-ranked hit happened to have, which today read 14:15 while
    # run_meta.json said 15:15. Use the newest close in the batch, and note
    # when not every symbol has caught up.
    stamps = [h.get("last_ts", "") for h in hits if h.get("last_ts")]
    if stamps:
        newest = max(stamps)
        stale = sum(1 for s in stamps if s != newest)
        note = f" ({stale} of {len(stamps)} one bar behind)" if stale else ""
        suffix = f"newest closed bar: {newest}{note}"
    else:
        suffix = "no timestamps in hits"
    legend = ("blue = parabola fit, dashed orange = best two-line V fit"
              if pattern != "momentum_dip"
              else "orange dash = swing high, red = dip low (stop), blue dot = entry")
    plt.suptitle(f"{title}  ({suffix})\n{legend}", color="w", fontsize=11)
    plt.tight_layout(rect=(0, 0, 1, 0.97))
    plt.savefig(args.out, dpi=115, facecolor=BG)
    print(f"wrote {args.out}")
    if pattern == "momentum_dip":
        print("Now VIEW this file. Per panel: is the advance real, or one gap?")
        print("Is the dip orderly, or a cliff? Does the last bar actually turn up,")
        print("and is the dip low a stop you could survive?")
    else:
        print("Now VIEW this file. Check each panel: is the rally sustained or one candle?")
        print("Does the base ROUND, or is it a V / wedge / flat shelf?")
        print("Do the fast EMAs run under the base and rise through it?")
        print("Where the dashed V hugs the candles closer than the curve, distrust it.")


if __name__ == "__main__":
    main()
