"""Render candlestick panels for every hit so they can be visually verified.

This step is not decoration. A V-shaped reversal fits a parabola BEAUTIFULLY --
often better than a genuine rounded base. Curvature cannot tell "rounded" from
"sharp bounce"; no threshold reliably separates them. Looking does.

After running this, open the PNG with the `view` tool and read the panels
BEFORE writing the report.

These are matplotlib renderings of yfinance data, not screenshots from any
charting platform. EMA seeding and session handling differ from TradingView and
Kite, so treat them as shape verification, not price truth.

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

BG, UP, DOWN, EMA_F, EMA_S, MARK = "#131722", "#26a69a", "#ef5350", "#e6d84a", "#9ad14b", "#ff9800"


def ema(values: np.ndarray, span: int) -> np.ndarray:
    alpha = 2.0 / (span + 1.0)
    out = np.empty_like(values)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", required=True)
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="hits.png")
    ap.add_argument("--bars", type=int, default=110)
    # Two columns, not three. A 3x3 grid puts each panel at roughly 620x440px,
    # which is enough to see that a shape curves but NOT enough to see how the
    # fast EMA behaves through the base -- whether it rolls over and keeps
    # falling, or dips and turns back up. That distinction is most of the
    # judgement this step exists to make, and at 3-up it is invisible: on the
    # 2026-08-25 run MANIPALHOS and SGMART were both filed as marginal off the
    # 3x3 grid and both moved to the top tier once re-rendered 2-up, unchanged.
    # The taller image costs nothing; misreading the panels costs the whole step.
    ap.add_argument("--cols", type=int, default=2)
    ap.add_argument("--ema-fast", type=int, default=20)
    ap.add_argument("--ema-slow", type=int, default=50)
    ap.add_argument("--title", default="NSE hourly — rally + rounded base near highs")
    args = ap.parse_args()

    hits = json.load(open(args.hits))
    if not hits:
        print("nothing to plot")
        return

    df = pl.read_parquet(args.parquet).sort(["symbol", "ts"])
    cols = min(args.cols, len(hits))
    rows = math.ceil(len(hits) / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5.4 * cols, 3.8 * rows),
                             facecolor=BG, squeeze=False)
    flat = axes.ravel()

    for ax, h in zip(flat, hits):
        g = df.filter(pl.col("symbol") == h["symbol"]).tail(args.bars)
        o = g["open"].to_numpy(); c = g["close"].to_numpy()
        hi = g["high"].to_numpy(); lo = g["low"].to_numpy()
        x = np.arange(len(c))
        up = c >= o
        colors = np.where(up, UP, DOWN)

        ax.vlines(x, lo, hi, color=colors, lw=0.7)
        ax.bar(x, c - o, bottom=o, color=colors, width=0.65, linewidth=0)
        ax.plot(x, ema(c, args.ema_fast), color=EMA_F, lw=1.1)
        ax.plot(x, ema(c, args.ema_slow), color=EMA_S, lw=1.1)

        k = h.get("base_bars", 0)
        if k:
            ax.axvspan(len(c) - k - 0.5, len(c) - 0.5, color=MARK, alpha=0.13)
        if "base_high" in h:
            ax.axhline(h["base_high"], color=MARK, ls="--", lw=1)

        ax.set_title(
            f"{h['symbol']}  rally {h.get('rally_pct','?')}%  base {k}b  "
            f"depth {h.get('base_depth_pct','?')}%  R2 {h.get('r2','?')}",
            color="w", fontsize=10)
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
    # tight_layout() does not reserve space for a suptitle, and the taller the
    # figure the tighter it packs the top row -- at 2 columns and 5 rows the
    # header lands on top of the first row's panel titles. Reserve a fixed
    # half-inch strip for it and place the title inside that strip, both scaled
    # out of figure-fraction coordinates so this holds for 1 row or 8.
    fig_h = 3.8 * rows
    fig.suptitle(f"{args.title}  ({suffix})", color="w",
                 y=1 - 0.18 / fig_h, va="top")
    plt.tight_layout(rect=(0, 0, 1, 1 - 0.55 / fig_h))
    plt.savefig(args.out, dpi=115, facecolor=BG)
    print(f"wrote {args.out}")
    print("Now VIEW this file. Check each panel: is the rally sustained or one candle?")
    print("Does the base ROUND, or is it a V / wedge / flat shelf?")
    print("Do the fast EMAs run under the base and rise through it?")


if __name__ == "__main__":
    main()
