"""Does SELECTION rescue a tight stop?

The headline MAE is over all screen entries. The fair defence of a hand-picked
tight-coil setup is that it should draw down less than the average entry. If it
does not, a 2.5% stop is indefensible regardless of how clean the chart looks.

Also: express stops in ATR multiples rather than percent, which is the only way
to compare a 0.5%-ATR stock with a 5%-ATR one.
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

B = os.path.dirname(os.path.abspath(__file__))
trades = json.load(open(os.path.join(B, 'trades.json')))
SET = ['flat_base_breakout', 'tight_flag', 'pullback_ema50', 'coil_near_high']

def mae_profile(rows, name):
    v = np.array([t['mae_20d'] for t in rows if t.get('mae_20d') is not None])
    if len(v) < 30: return
    s25 = 100 * (v <= -2.5).mean(); s5 = 100 * (v <= -5.0).mean()
    print(f'{name:24s} n={len(v):>5d}  MAE p25={np.percentile(v,25):+6.2f}% '
          f'p50={np.percentile(v,50):+6.2f}%  hit-2.5%={s25:5.1f}%  hit-5%={s5:5.1f}%')

print('=== 20-day MAE by selection (does picking better setups reduce drawdown?) ===')
mae_profile(trades, 'ALL screen entries')
for s in SET:
    mae_profile([t for t in trades if t.get(f'su_{s}')], s)

low = [t for t in trades if t.get('atr_pct') is not None and t['atr_pct'] < 0.8]
tight_low = [t for t in low if t.get('su_tight_flag') or t.get('su_coil_near_high')]
mae_profile(low, 'hourly ATR < 0.8%')
mae_profile(tight_low, 'ATR<0.8% AND tight/coil')

print('\n=== STOP EXPRESSED IN HOURLY-ATR MULTIPLES ===')
print('What multiple of hourly ATR does a stop need, to survive N% of trades?\n')
rows = [t for t in trades if t.get('atr_pct') and t.get('mae_20d') is not None and t['atr_pct'] > 0]
mult = np.array([abs(t['mae_20d']) / t['atr_pct'] for t in rows])
print(f"{'survive':>9} {'needs stop at':>16}")
for pct in (50, 60, 70, 80, 90):
    print(f'{pct:8d}% {np.percentile(mult, pct):13.1f}x ATR')

print('\n=== Same, for the tight/coil subset only ===')
r2 = [t for t in rows if t.get('su_tight_flag') or t.get('su_coil_near_high')]
if len(r2) > 50:
    m2 = np.array([abs(t['mae_20d']) / t['atr_pct'] for t in r2])
    for pct in (50, 60, 70, 80, 90):
        print(f'{pct:8d}% {np.percentile(m2, pct):13.1f}x ATR   (n={len(r2)})')

print('\n=== 5-DAY horizon (closer to an hourly-timeframe trade) ===')
r5 = [t for t in trades if t.get('atr_pct') and t.get('mae_5d') is not None and t['atr_pct'] > 0]
m5 = np.array([abs(t['mae_5d']) / t['atr_pct'] for t in r5])
for pct in (50, 60, 70, 80, 90):
    print(f'{pct:8d}% {np.percentile(m5, pct):13.1f}x ATR')
v5 = np.array([t['mae_5d'] for t in r5])
print(f'\n5d MAE: p50={np.percentile(v5,50):+.2f}%  p25={np.percentile(v5,25):+.2f}%  '
      f'share hitting -2.5% = {100*(v5<=-2.5).mean():.1f}%')
