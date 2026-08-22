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

Pattern-agnostic. Both detectors emit the same four canonical keys and this
script reads only those, so a new pattern needs no second copy of the context
filters -- which is the point, since the context filters are what actually
decide whether a shortlist is usable:

  pattern_bars  bars in the base / the dip      (the structure itself)
  leg_bars      bars in the rally / the advance (the move that preceded it)
  struct_high   the lip / the swing high        (what the geometry is measured against)
  risk_pct      entry -> struct_low, in percent (the only stop the structure supports)

Usage:
    python postfilter.py --hits hits.json --parquet all_closed.parquet --out hits_clean.json
"""

from __future__ import annotations

import argparse
import csv
import json

import numpy as np
import polars as pl


def _k(h: dict) -> int:
    return int(h.get("pattern_bars", h.get("base_bars", 0)))


def _rb(h: dict) -> int:
    return int(h.get("leg_bars", h.get("rally_bars", 0)))


def _struct_high(h: dict) -> float:
    return float(h.get("struct_high", h.get("base_high", 0.0)))


def _risk_pct(h: dict) -> float:
    # base_depth_pct is the legacy fallback: for the cup, entry IS the lip, so
    # risk-to-base-low and base depth are the same number by construction.
    return float(h.get("risk_pct", h.get("risk_pct_to_base_low",
                                         h.get("base_depth_pct", 0.0))))


def enrich(hits: list[dict], parquet: str, bars_per_day: int,
           target_pct: float) -> list[dict]:
    df = pl.read_parquet(parquet).sort(["symbol", "ts"])
    # Universe-wide newest closed bar. Any hit whose own last_ts predates this
    # is priced on stale data even though the universe as a whole is fresh --
    # the caller needs to know so quoted levels are not paraded as current.
    universe_last = df["ts"].max()
    # Distinct hourly bars per symbol, so "bars_behind_universe" is measured in
    # actual bars rather than clock time (a 15:15 stub is only 15 minutes past
    # the 15:00 close but is still one bar).
    bars_ordered = sorted(df["ts"].unique().to_list())
    bar_index = {ts: i for i, ts in enumerate(bars_ordered)}
    last_bar_pos = bar_index[universe_last]
    out = []
    for h in hits:
        g = df.filter(pl.col("symbol") == h["symbol"])
        c = g["close"].to_numpy().astype(float)
        v = g["volume"].to_numpy().astype(float)
        hi = g["high"].to_numpy().astype(float)
        sym_last = g["ts"].max()
        h["bars_behind_universe"] = last_bar_pos - bar_index.get(sym_last, last_bar_pos)

        # median hourly turnover -> approx daily Rs crore
        turn = np.median(c[-120:] * v[-120:]) / 1e7 * bars_per_day
        h["turnover_cr"] = round(float(turn), 2)

        h["pct_of_60d_high"] = round(float(_struct_high(h) / hi.max() * 100), 1)

        k, rb = _k(h), _rb(h)
        seg = c[len(c) - k - rb: len(c) - k]
        if len(seg) > 2:
            tot = seg[-1] - seg[0]
            h["max_bar_share"] = round(float(np.diff(seg).max() / tot), 2) if tot > 0 else 9.9
        else:
            h["max_bar_share"] = 9.9

        # Structural reward-to-risk: target measured off the entry, risk
        # measured to the structural low -- the only stop the pattern supports.
        # Both numerator and denominator are percentages; the ratio is unitless
        # and ties the geometry to position sizing. This is the ranking key.
        # For the cup, entry is the lip, so this is still target / base depth.
        risk = _risk_pct(h)
        h["rrr_structural"] = round(target_pct / risk, 2) if risk > 1e-9 else 0.0
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
    ap.add_argument("--target-pct", type=float, default=15.0,
                    help="profit target off the entry in PERCENT (15.0 == 15%%), "
                         "used as the RRR numerator")
    args = ap.parse_args()

    raw = json.load(open(args.hits))
    if not raw:
        json.dump([], open(args.out, "w"))
        print(f"0 raw -> 0 clean -> {args.out}")
        return

    hits = enrich(raw, args.parquet, args.bars_per_day, args.target_pct)
    pattern = hits[0].get("pattern", "rally_cup")

    def why(h: dict) -> list[str]:
        r = []
        if h["turnover_cr"] < args.min_turnover:
            r.append(f"illiquid {h['turnover_cr']}cr")
        if h["pct_of_60d_high"] < args.min_pct_60d_high:
            r.append(f"not-at-high {h['pct_of_60d_high']}%")
        if h["max_bar_share"] > args.max_bar_share:
            r.append(f"gap-driven {h['max_bar_share']}")
        return r

    # Edge-proximity flag: how close each PASSING hit sat to the filter that
    # would have cut it. JUBLFOOD passed max_bar_share at exactly 0.50 against
    # a >0.50 reject rule -- a rounding-boundary pass indistinguishable from a
    # margin pass in the JSON. This surfaces the margin per hit so the visual
    # pass and the report can weight it. Does NOT change what passes.
    def edges(h: dict) -> list[str]:
        eps = 0.02  # "within one bucket" -- deliberate, not a tuning knob
        r = []
        if abs(h["max_bar_share"] - args.max_bar_share) <= eps:
            r.append(f"max_bar_share {h['max_bar_share']} vs cut {args.max_bar_share}")
        if abs(h["turnover_cr"] - args.min_turnover) <= args.min_turnover * 0.1:
            r.append(f"turnover {h['turnover_cr']}cr vs floor {args.min_turnover}")
        if abs(h["pct_of_60d_high"] - args.min_pct_60d_high) <= 0.5:
            r.append(f"pct_of_60d_high {h['pct_of_60d_high']}% vs floor {args.min_pct_60d_high}")
        return r

    clean = [h for h in hits if not why(h)]
    for h in clean:
        h["edge_flags"] = edges(h)
    rejected = [(h, why(h)) for h in hits if why(h)]
    clean.sort(key=lambda r: -r["rrr_structural"])

    json.dump(clean, open(args.out, "w"), indent=2, default=str)

    print(f"[{pattern}] {len(hits)} raw -> {len(clean)} clean -> {args.out}")
    if clean:
        pl.Config.set_tbl_rows(60)
        pl.Config.set_tbl_width_chars(250)
        pl.Config.set_tbl_cols(24)
        d = pl.DataFrame(clean)
        risk_col = "risk_pct" if "risk_pct" in d.columns else "risk_pct_to_base_low"
        print("ranked by structural RRR (target / risk-to-structural-low), best first:\n")
        print(d.select([c for c in ["symbol", "rrr_structural", "entry",
                                    "struct_low", "base_depth_pct", risk_col,
                                    "stop_inside_base", "t1", "t2", "turnover_cr"]
                        if c in d.columns]))
        print()
        if pattern == "momentum_dip":
            shape_cols = ["symbol", "close", "advance_pct", "dip_pct", "dip_bars",
                          "retrace_of_advance", "dip_vol_ratio", "recovered_frac",
                          "rsi", "trigger", "pct_of_60d_high", "max_bar_share"]
        else:
            shape_cols = ["symbol", "close", "rally_pct", "base_bars", "curvature",
                          "r2", "vee_gain", "bottom_frac", "k_pass",
                          "dist_from_lip_pct", "vol_ratio", "pct_of_60d_high",
                          "max_bar_share"]
        print(d.select([c for c in shape_cols if c in d.columns]))

        n_bad = sum(1 for h in clean if h.get("stop_inside_base"))
        if n_bad:
            print(f"\n{n_bad}/{len(clean)} have the fixed-% stop INSIDE the structure.")
            print("Report risk_pct as the real structural risk.")

        suspect = [h for h in clean if h.get("vol_suspect")]
        if suspect:
            print(f"\n{len(suspect)}/{len(clean)} have a suspect volume dry-up "
                  f"(ratio under 0.10 or zero-volume bars) -- more likely a "
                  f"yfinance artifact than real exhaustion:")
            for h in suspect:
                print(f"  {h['symbol']:14s} vol_ratio {h.get('vol_ratio')}")

        n_stale = sum(1 for h in clean if h.get("bars_behind_universe", 0) > 0)
        if n_stale:
            print(f"\n{n_stale}/{len(clean)} priced BEHIND the universe's last bar:")
            for h in clean:
                b = h.get("bars_behind_universe", 0)
                if b > 0:
                    print(f"  {h['symbol']:14s} {b} bar(s) behind (last_ts {h['last_ts']})")
            print("Quote these hits at their last_ts, not the universe last_closed_bar.")

        edge_hits = [h for h in clean if h.get("edge_flags")]
        if edge_hits:
            print(f"\n{len(edge_hits)}/{len(clean)} passed within an edge of a filter:")
            for h in edge_hits:
                print(f"  {h['symbol']:14s} {'; '.join(h['edge_flags'])}")
            print("A boundary pass is not the same evidence as a margin pass.")
        if pattern == "momentum_dip":
            print("\nCROSS-PATTERN WARNING: these RRRs are NOT comparable with the")
            print("rally_cup screen's. The dip's stop is the dip low, typically 1-3%")
            print("away, which mechanically produces RRRs of 5-15 against the cup's")
            print("2-5. A tighter stop is also a likelier stop: this entry sits")
            print("inside an unfinished move, where the cup screen waits for one to")
            print("finish. Quote risk_pct_buffered (half an ATR below the dip low)")
            print("as the risk a real position would have to carry.")

        print("\nRRR ranks the GEOMETRY, not the odds. It says what the trade pays")
        print("if it works, never how often it works. Do not present it as a")
        print("probability of success or as a recommendation to buy the top name.")

    if rejected:
        print("\nrejected:")
        for h, r in sorted(rejected, key=lambda x: -x[0]["rrr_structural"]):
            print(f"  {h['symbol']:14s} {', '.join(r)}")

    if args.csv:
        common = ["symbol", "pattern", "close", "entry", "sl",
                  "t1", "t2", "struct_high", "struct_low", "base_depth_pct",
                  "risk_pct", "risk_pct_to_base_low", "stop_inside_base",
                  "rrr_structural", "turnover_cr", "pct_of_60d_high",
                  "max_bar_share", "score", "last_ts", "bars_behind_universe",
                  "edge_flags"]
        cup = ["rally_pct", "rally_bars", "rally_dd_pct", "base_bars",
               "curvature", "r2", "vertex_x", "vee_gain", "bottom_frac",
               "limb_ratio", "round_ratio", "k_pass", "k_span",
               "dist_from_lip_pct", "vol_ratio", "vol_suspect", "overhead_frac"]
        dip = ["trigger_above", "advance_pct", "advance_bars", "dip_pct", "dip_bars",
               "struct_stop_buffered", "risk_pct_buffered",
               "retrace_of_advance", "dip_bar_share", "dip_vol_ratio",
               "recovered_frac", "bars_since_dip_low", "trigger",
               "touched_ema_fast", "vs_ema_slow_pct", "dip_closes_below_ema_slow", "rsi", "rsi_at_dip_low",
               "atr_pct", "dist_from_high_pct"]
        # One column set per pattern: a shared header would be half-empty in
        # every row and unreadable in a spreadsheet.
        cols = common + (dip if pattern == "momentum_dip" else cup)
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in clean:
                row = dict(r)
                # edge_flags is a list -- flatten to a semicolon-joined string
                # so the CSV stays one-row-per-hit and readable in a spreadsheet
                row["edge_flags"] = "; ".join(r.get("edge_flags", []))
                w.writerow(row)
        print(f"\ncsv -> {args.csv}")

    print("\nNext: plot_hits.py, then VIEW the png before reporting anything.")


if __name__ == "__main__":
    main()
