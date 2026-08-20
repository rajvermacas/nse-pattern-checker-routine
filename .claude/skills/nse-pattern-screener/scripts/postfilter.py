"""Context filters. The detector sees a 120-bar window; these supply what it
cannot see. Each one was earned from a real false positive:

  liquidity      -- thin names give beautiful geometry and unfillable entries,
                    and make the volume dry-up ratio meaningless.
  pct_of_60d_high-- a stock that fell 20% and bounced shows a "rally" and a base
                    near the WINDOW high while sitting far below the real one.
                    That is a downtrend bounce into overhead supply.
  max_bar_share  -- the rally is measured low-to-high, so a single gap-up candle
                    registers as a multi-bar rally. Gap-and-base is a different
                    setup with different odds than rally-and-base.

Usage:
    python postfilter.py --hits hits.json --parquet all_closed.parquet --out hits_clean.json
"""

from __future__ import annotations

import argparse
import csv
import json

import numpy as np
import polars as pl


def enrich(hits: list[dict], parquet: str, bars_per_day: int,
           target_pct: float) -> list[dict]:
    df = pl.read_parquet(parquet).sort(["symbol", "ts"])
    out = []
    for h in hits:
        g = df.filter(pl.col("symbol") == h["symbol"])
        c = g["close"].to_numpy().astype(float)
        v = g["volume"].to_numpy().astype(float)
        hi = g["high"].to_numpy().astype(float)

        # median hourly turnover -> approx daily Rs crore
        turn = np.median(c[-120:] * v[-120:]) / 1e7 * bars_per_day
        h["turnover_cr"] = round(float(turn), 2)

        h["pct_of_60d_high"] = round(float(h["base_high"] / hi.max() * 100), 1)

        k, rb = h["base_bars"], h["rally_bars"]
        seg = c[len(c) - k - rb: len(c) - k]
        if len(seg) > 2:
            tot = seg[-1] - seg[0]
            h["max_bar_share"] = round(float(np.diff(seg).max() / tot), 2) if tot > 0 else 9.9
        else:
            h["max_bar_share"] = 9.9

        # Structural reward-to-risk: target measured off the lip, risk measured
        # to the base low -- the only stop the pattern's structure supports.
        # Reduces to target_pct / base_depth_pct. This is the ranking criterion:
        # it is the one number that ties the geometry to position sizing.
        h["rrr_structural"] = round(target_pct * 100 / h["base_depth_pct"], 2)
        out.append(h)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", required=True)
    ap.add_argument("--parquet", required=True)
    ap.add_argument("--out", default="hits_clean.json")
    ap.add_argument("--csv", default=None)
    ap.add_argument("--min-turnover", type=float, default=5.0, help="Rs crore/day")
    ap.add_argument("--min-pct-60d-high", type=float, default=97.0)
    ap.add_argument("--max-bar-share", type=float, default=0.5)
    ap.add_argument("--bars-per-day", type=int, default=7, help="7 for NSE hourly")
    ap.add_argument("--target-pct", type=float, default=0.15,
                    help="profit target off the lip, used as the RRR numerator")
    args = ap.parse_args()

    hits = enrich(json.load(open(args.hits)), args.parquet, args.bars_per_day,
                  args.target_pct)

    def why(h: dict) -> list[str]:
        r = []
        if h["turnover_cr"] < args.min_turnover:
            r.append(f"illiquid {h['turnover_cr']}cr")
        if h["pct_of_60d_high"] < args.min_pct_60d_high:
            r.append(f"not-at-high {h['pct_of_60d_high']}%")
        if h["max_bar_share"] > args.max_bar_share:
            r.append(f"gap-driven {h['max_bar_share']}")
        return r

    clean = [h for h in hits if not why(h)]
    rejected = [(h, why(h)) for h in hits if why(h)]
    clean.sort(key=lambda r: -r["rrr_structural"])

    json.dump(clean, open(args.out, "w"), indent=2, default=str)

    print(f"{len(hits)} raw -> {len(clean)} clean -> {args.out}")
    if clean:
        pl.Config.set_tbl_rows(60)
        pl.Config.set_tbl_width_chars(250)
        pl.Config.set_tbl_cols(22)
        d = pl.DataFrame(clean)
        print("ranked by structural RRR (target / risk-to-base-low), best first:\n")
        print(d.select(["symbol", "rrr_structural", "entry", "base_low",
                        "base_depth_pct", "risk_pct_to_base_low",
                        "stop_inside_base", "t2", "turnover_cr"]))
        print()
        print(d.select(["symbol", "close", "rally_pct", "base_bars",
                        "curvature", "r2", "dist_from_lip_pct", "vol_ratio",
                        "pct_of_60d_high", "max_bar_share"]))
        n_bad = sum(1 for h in clean if h["stop_inside_base"])
        if n_bad:
            print(f"\n{n_bad}/{len(clean)} have the fixed-% stop INSIDE the base.")
            print("Report risk_pct_to_base_low as the real structural risk.")
        print("\nRRR ranks the GEOMETRY, not the odds. It says what the trade pays")
        print("if it works, never how often it works. Do not present it as a")
        print("probability of success or as a recommendation to buy the top name.")

    if rejected:
        print("\nrejected:")
        for h, r in sorted(rejected, key=lambda x: -x[0]["rrr_structural"]):
            print(f"  {h['symbol']:14s} {', '.join(r)}")

    if args.csv:
        cols = ["symbol", "close", "rally_pct", "rally_bars", "base_bars",
                "base_depth_pct", "curvature", "r2", "vertex_x", "dist_from_lip_pct",
                "vol_ratio", "turnover_cr", "pct_of_60d_high", "max_bar_share",
                "entry", "sl", "t1", "t2", "base_low", "risk_pct_to_base_low",
                "stop_inside_base", "rrr_structural", "score", "last_ts"]
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in clean:
                w.writerow(r)
        print(f"\ncsv -> {args.csv}")

    print("\nNext: plot_hits.py, then VIEW the png before reporting anything.")


if __name__ == "__main__":
    main()
