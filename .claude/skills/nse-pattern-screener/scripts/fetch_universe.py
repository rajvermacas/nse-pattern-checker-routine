"""Fetch the NSE symbol universe from NSE's own archives.

Series meanings:
    EQ - rolling settlement, intraday allowed. The tradable universe.
    BE - trade-to-trade, delivery only. No intraday.
    BZ - surveillance / suspended.

Usage:
    python fetch_universe.py --series EQ --out universe.txt
    python fetch_universe.py --index nifty500 --out universe.txt
"""

from __future__ import annotations

import argparse
import io
import sys

import pandas as pd
import requests

# NSE's edge gates on the Chrome major version in the UA, not just on the
# presence of browser-ish headers. Measured 2026-08-20 against EQUITY_L.csv,
# unprimed, one request each:
#     Chrome/124 -> 403      Chrome/131 -> 200
#     Chrome/126 -> 403      Chrome/139 -> 200
#     curl/8.5.0 -> timeout  Firefox/130, Safari/17, Edge/131 -> 200
# So a UA that merely looks like a browser is not enough; it has to look like a
# CURRENT one. This will rot again as the floor moves -- when the universe
# stage starts 403ing, bump this before suspecting the network or a block.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")

# NSE's edge rejects requests that carry only a User-Agent with a bare 403.
# Sending the rest of what a browser sends -- Accept, Accept-Language, and a
# Referer from the site itself -- is what the archives host actually checks.
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/csv,application/csv,text/plain,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}

# Two priming stops. The bare home page 403s on some evenings and only sets one
# cookie when it does answer 200 -- not enough to unblock the archives host. The
# securities-available-for-trading page reliably yields the fuller cookie set
# (bm_sv/bm_sz/ak_bmsc) that nsearchives.nseindia.com actually checks. Prime
# both, in order, and let the first-page failure be non-fatal.
PRIME_URLS = [
    "https://www.nseindia.com/",
    "https://www.nseindia.com/market-data/securities-available-for-trading",
]

EQUITY_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
INDEX_URLS = {
    "nifty50": "https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv",
    "nifty100": "https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv",
    "nifty200": "https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv",
    "nifty500": "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
    "midcap150": "https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
    "smallcap250": "https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
}


def _get(url: str) -> pd.DataFrame:
    # One session so the cookie NSE sets on the home page rides along to the
    # archives host. The edge's 403 is not purely header-based -- on a cold
    # client it also wants the cookie a browser would already hold, so a first
    # pass can fail where a primed second pass succeeds. Prime once, then retry
    # once. Never retry more than that: a persistent 403 is a real block, and
    # hammering it walks straight into rate limiting.
    s = requests.Session()
    s.headers.update(HEADERS)
    last: requests.Response | None = None
    for attempt in (1, 2):
        try:
            if attempt == 2:
                # Prime: walk both stops so Set-Cookie lands in the jar, then
                # reissue the archives request with the fuller cookie set
                # attached. Prime pages are HTML, so we send Accept:text/html
                # for them (the session's default Accept:text/csv causes NSE to
                # reject the prime, which then never sets cookies -- the whole
                # trip is wasted). Priming is best-effort per-URL: one may 403
                # while the other succeeds; the retry still tries.
                html_hdrs = {"Accept":
                             "text/html,application/xhtml+xml,"
                             "application/xml;q=0.9,*/*;q=0.8"}
                for p in PRIME_URLS:
                    try:
                        s.get(p, headers=html_hdrs, timeout=30)
                    except requests.RequestException:
                        continue
            r = s.get(url, timeout=30)
            last = r
            if r.status_code == 200:
                df = pd.read_csv(io.StringIO(r.text))
                df.columns = [c.strip() for c in df.columns]
                return df
        except requests.RequestException as exc:
            # A transport error (TLS/proxy/DNS) is worth one primed retry too,
            # but keep the message so a terminal failure is diagnosable.
            if attempt == 2:
                sys.exit(f"universe fetch: {url} failed transport: {exc}")

    # Both passes returned a non-200. Surface the actual status and a snippet
    # of the body instead of a bare HTTPError -- the difference between "NSE
    # blocked us (403)" and "wrong path (404)" is the whole diagnosis, and the
    # old raise_for_status() buried it behind a generic stage-fail message.
    code = last.status_code if last is not None else "no-response"
    body = (last.text[:200].replace("\n", " ") if last is not None else "")
    sys.exit(f"universe fetch: {url} returned HTTP {code} after a primed "
             f"retry. First 200 bytes: {body!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="EQ",
                    help="comma list: EQ, BE, BZ, or ALL")
    ap.add_argument("--index", default=None, help=f"one of {list(INDEX_URLS)}")
    ap.add_argument("--out", default="universe.txt")
    args = ap.parse_args()

    if args.index:
        key = args.index.lower().replace(" ", "").replace("-", "")
        if key not in INDEX_URLS:
            sys.exit(f"unknown index {args.index}; choose from {list(INDEX_URLS)}")
        df = _get(INDEX_URLS[key])
        syms = sorted(df["Symbol"].astype(str).str.strip().unique())
        label = args.index
    else:
        df = _get(EQUITY_URL)
        df["SERIES"] = df["SERIES"].astype(str).str.strip()
        counts = df["SERIES"].value_counts().to_dict()
        print("series breakdown:", counts)
        if args.series.upper() == "ALL":
            keep = df
        else:
            wanted = [s.strip().upper() for s in args.series.split(",")]
            keep = df[df["SERIES"].isin(wanted)]
        syms = sorted(keep["SYMBOL"].astype(str).str.strip().unique())
        label = args.series

    with open(args.out, "w") as f:
        f.write("\n".join(syms))
    print(f"{len(syms)} symbols ({label}) -> {args.out}")


if __name__ == "__main__":
    main()
