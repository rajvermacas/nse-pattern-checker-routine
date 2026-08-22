"""Point-in-time reconstruction of the Chartink screen + forward-return backtest.

The screen is pure arithmetic on OHLCV, so historical membership can be rebuilt
from bars instead of relying on Chartink for history. Validated against the live
2026-08-21 run: 99/107 reproduced, misses all at the RSI 60 boundary.

Conditions (from the screener's own atlas_query):
    daily RSI(14) > 60 AND weekly RSI(14) > 60 AND monthly RSI(14) > 60
    AND market cap > 5000 cr
    AND 30-min EMA(20) >= 0.97 * 30-min close        <- NOT reconstructible
    AND 1-hour  EMA(20) >= 0.97 * 1-hour close

The 30-min leg is dropped: Yahoo serves only 60 days of 30-minute bars. It is a
near-duplicate of the 1-hour leg (both say "within 3% of the 20-EMA"), so the
approximation is mild, but it does make this screen slightly LOOSER than the real
one and that belongs in any reading of the results.
"""
import os, json, datetime
import numpy as np

B = os.path.dirname(os.path.abspath(__file__))
BARS = os.path.join(B, 'bars')
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
CR = 1e7  # 1 crore

# ---------------------------------------------------------------- indicators
def wilder_rsi(c, n=14):
    """RSI(14), Wilder smoothing, seeded on the first n deltas. Returns a full
    array aligned to c, NaN until it is defined."""
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) < n + 2:
        return out
    d = np.diff(c)
    g = np.where(d > 0, d, 0.0)
    l = np.where(d < 0, -d, 0.0)
    ag, al = g[:n].mean(), l[:n].mean()
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n, len(d)):
        ag = (ag * (n - 1) + g[i]) / n
        al = (al * (n - 1) + l[i]) / n
        out[i + 1] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out

def ema(a, n):
    a = np.asarray(a, float)
    k = 2 / (n + 1)
    o = np.empty_like(a)
    o[0] = a[0]
    for i in range(1, len(a)):
        o[i] = a[i] * k + o[i - 1] * (1 - k)
    return o

def atr(h, l, c, n=14):
    h, l, c = map(lambda x: np.asarray(x, float), (h, l, c))
    tr = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    tr = np.concatenate([[h[0] - l[0]], tr])
    o = np.empty(len(tr)); o[0] = tr[:n].mean()
    for i in range(1, len(tr)):
        o[i] = (o[i - 1] * (n - 1) + tr[i]) / n
    return o

# ---------------------------------------------------------------- resampling
def running_period_rsi(dates, closes, key, n=14):
    """RSI(n) of a resampled (weekly/monthly) series, evaluated as of EVERY daily
    bar, treating the in-progress period as its final point -- which is what a
    live screener sees mid-week or mid-month.

    Incremental, O(1) per bar. Wilder state (ag/al) is committed only when a
    period actually closes; the running value forks one provisional step off
    that committed state using the current partial period's close.
    """
    keys = [key(d) for d in dates]
    out = np.full(len(closes), np.nan)
    seed_deltas = []          # deltas between closed-period closes, for seeding
    ag = al = None
    prev_closed = None        # close of the most recent COMPLETED period
    for i in range(len(closes)):
        if i > 0 and keys[i] != keys[i - 1]:
            # period ending at i-1 just completed
            c_closed = closes[i - 1]
            if prev_closed is not None:
                d = c_closed - prev_closed
                if ag is None:
                    seed_deltas.append(d)
                    if len(seed_deltas) == n:
                        g = [x for x in seed_deltas if x > 0]
                        l = [-x for x in seed_deltas if x < 0]
                        ag = sum(g) / n
                        al = sum(l) / n
                else:
                    ag = (ag * (n - 1) + max(d, 0.0)) / n
                    al = (al * (n - 1) + max(-d, 0.0)) / n
            prev_closed = c_closed
        if ag is not None and prev_closed is not None:
            d = closes[i] - prev_closed
            pag = (ag * (n - 1) + max(d, 0.0)) / n
            pal = (al * (n - 1) + max(-d, 0.0)) / n
            out[i] = 100.0 if pal == 0 else 100 - 100 / (1 + pag / pal)
    return out

def iso_week(d):  return (d.isocalendar()[0], d.isocalendar()[1])
def cal_month(d): return (d.year, d.month)

# ---------------------------------------------------------------- loading
def load(sym):
    z = np.load(os.path.join(BARS, f'{sym}.npz'))
    ht = z['ht']
    hdates = np.array([datetime.datetime.fromtimestamp(int(t), IST).date() for t in ht])
    dt = z['dt']
    ddates = np.array([datetime.datetime.fromtimestamp(int(t), IST).date() for t in dt])
    dc = z['dc'].astype(float); dh = z['dh'].astype(float)
    dl = z['dl'].astype(float); dv = z['dv'].astype(float)

    # Yahoo's daily series frequently lags the hourly by a session. Left alone
    # this evaluates the screen a day early and silently costs both recall and
    # precision (measured: 87.8% / 92.3% before this fix). Rebuild any trailing
    # sessions the daily series is missing from the hourly bars, which are
    # already there.
    if len(ddates):
        last_d = ddates[-1]
        extra = {}
        for i, d in enumerate(hdates):
            if d > last_d:
                extra.setdefault(d, []).append(i)
        for d in sorted(extra):
            idx = extra[d]
            dh = np.append(dh, max(z['hh'][k] for k in idx))
            dl = np.append(dl, min(z['hl'][k] for k in idx))
            dc = np.append(dc, z['hc'][idx[-1]])
            dv = np.append(dv, sum(int(z['hv'][k]) for k in idx))
            ddates = np.append(ddates, d)

    return dict(
        hdates=hdates, ht=ht, ho=z['ho'].astype(float), hh=z['hh'].astype(float),
        hl=z['hl'].astype(float), hc=z['hc'].astype(float), hv=z['hv'].astype(float),
        ddates=ddates, dc=dc, dh=dh, dl=dl, dv=dv)

# ---------------------------------------------------------------- screen
def screen_mask(S, shares, mcap_min_cr=5000.0, always_eligible=False):
    """Boolean per DAILY bar: did this symbol satisfy the screen at that close?"""
    dd, dc = S['ddates'], S['dc']
    n = len(dc)
    if n < 400:
        return None
    r_d = wilder_rsi(dc, 14)
    r_w = running_period_rsi(dd, dc, iso_week, 14)
    r_m = running_period_rsi(dd, dc, cal_month, 14)

    # 1-hour EMA20 condition, evaluated at the LAST hourly bar of each day
    hc, hd = S['hc'], S['hdates']
    e20 = ema(hc, 20)
    last_h = {}
    for i, d in enumerate(hd):
        last_h[d] = i
    h_ok = np.zeros(n, dtype=bool)
    h_have = np.zeros(n, dtype=bool)
    for i, d in enumerate(dd):
        j = last_h.get(d)
        if j is not None:
            h_have[i] = True
            h_ok[i] = e20[j] >= 0.97 * hc[j]

    if always_eligible or not shares:
        mcap_ok = np.ones(n, dtype=bool)
    else:
        mcap_ok = (dc * shares / CR) > mcap_min_cr

    ok = (r_d > 60) & (r_w > 60) & (r_m > 60) & mcap_ok & h_ok & h_have
    return np.nan_to_num(ok, nan=False).astype(bool)

# ---------------------------------------------------------------- setups
def setups_at(S, j):
    """Mechanical setup classification on hourly bars, using data up to and
    including bar j. Returns a dict of bool flags. Volume statistics EXCLUDE
    zero-volume bars: 81.6% of 09:15 bars report 0, which otherwise depresses
    every average and inflates every 'Nx average volume' multiple."""
    out = {}
    if j < 220:
        return out
    c = S['hc'][:j + 1]; h = S['hh'][:j + 1]; l = S['hl'][:j + 1]; v = S['hv'][:j + 1]
    e20 = ema(c, 20); e50 = ema(c, 50); e200 = ema(c, 200)
    px = c[-1]
    def vmed(a):
        a = a[a > 0]
        return float(np.median(a)) if len(a) else 0.0
    v_recent, v_base = vmed(v[-20:]), vmed(v[-100:-20])
    stack = e20[-1] > e50[-1] > e200[-1]

    prior_hi = float(h[-63:-3].max()); prior_lo = float(l[-63:-3].min())
    width = (prior_hi - prior_lo) / prior_hi if prior_hi else 1.0
    out['flat_base_breakout'] = bool(stack and width <= 0.10 and px > prior_hi
                                     and v_recent > 0 and v_base > 0 and v_recent >= 1.3 * v_base)

    r15h, r15l = float(h[-15:].max()), float(l[-15:].min())
    tight = (r15h - r15l) / r15h if r15h else 1.0
    out['tight_flag'] = bool(stack and tight <= 0.05 and px > e20[-1]
                             and v_base > 0 and v_recent <= 0.85 * v_base)

    near50 = abs(float(l[-5:].min()) - e50[-1]) / e50[-1] if e50[-1] else 1.0
    out['pullback_ema50'] = bool(stack and near50 <= 0.015 and px > e50[-1])

    hi60 = float(h[-60:].max())
    r30h, r30l = float(h[-30:].max()), float(l[-30:].min())
    out['coil_near_high'] = bool(stack and px >= 0.98 * hi60
                                 and ((r30h - r30l) / r30h if r30h else 1) <= 0.07)
    out['any_setup'] = any(out.values())
    return out

# ---------------------------------------------------------------- trades
HORIZONS = {'1d': 7, '3d': 21, '5d': 35, '10d': 70, '20d': 140}

def build_trades(sym, S, mask, want_setups=True):
    """One trade per FRESH screen entry: in-screen today, not yesterday.
    Entry at the OPEN of the first hourly bar strictly after the signal day."""
    dd = S['ddates']; hd = S['hdates']
    trades = []
    A = atr(S['hh'], S['hl'], S['hc'], 14)
    # first hourly index on each date
    first_h = {}
    for i in range(len(hd) - 1, -1, -1):
        first_h[hd[i]] = i
    dates_sorted = sorted(first_h)
    for i in range(1, len(mask)):
        if not (mask[i] and not mask[i - 1]):
            continue
        sig_day = dd[i]
        nxt = None
        for d in dates_sorted:
            if d > sig_day:
                nxt = d; break
        if nxt is None:
            continue
        j = first_h[nxt]
        if j < 220 or j + 1 >= len(S['hc']):
            continue
        entry = float(S['ho'][j])
        if entry <= 0:
            continue
        rec = dict(symbol=sym, signal_date=str(sig_day), entry_date=str(nxt),
                   entry=entry, entry_idx=int(j),
                   atr_pct=float(A[j - 1] / entry * 100) if entry else None)
        for name, nb in HORIZONS.items():
            k = min(j + nb, len(S['hc']) - 1)
            if k <= j:
                rec[f'ret_{name}'] = None; continue
            rec[f'ret_{name}'] = float(S['hc'][k] / entry - 1) * 100
            seg_l = S['hl'][j:k + 1]; seg_h = S['hh'][j:k + 1]
            rec[f'mae_{name}'] = float(seg_l.min() / entry - 1) * 100
            rec[f'mfe_{name}'] = float(seg_h.max() / entry - 1) * 100
        if want_setups:
            rec.update({f'su_{k}': v for k, v in setups_at(S, j - 1).items()})
        trades.append(rec)
    return trades
