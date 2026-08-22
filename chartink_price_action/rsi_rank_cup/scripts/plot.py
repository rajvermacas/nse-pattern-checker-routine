import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np, json, sys, os
sys.path.insert(0,'rsi15')
from daily_series import load_all, ema, rsi_series

UP='#1a9850'; DN='#d73027'
def candles(ax, o,h,l,c, w=0.62):
    for i in range(len(o)):
        col = UP if c[i]>=o[i] else DN
        ax.vlines(i, l[i], h[i], color=col, linewidth=0.8, zorder=2)
        lo,hi = min(o[i],c[i]), max(o[i],c[i])
        ax.add_patch(Rectangle((i-w/2, lo), w, max(hi-lo, (h[i]-l[i])*0.004 or 1e-9),
                     facecolor=col, edgecolor=col, linewidth=0.5, zorder=3))

def plot(sym, g, rank, rsi, outdir='rsi15/charts'):
    os.makedirs(outdir, exist_ok=True)
    o,h,l,c,v = [g[k].values.astype(float) for k in ('open','high','low','close','volume')]
    d = g['d'].values
    e20,e50,e200 = ema(c,20), ema(c,50), ema(c,200)
    rs = rsi_series(c)

    fig = plt.figure(figsize=(17,12))
    gs = fig.add_gridspec(4,1, height_ratios=[3.1,1.0,3.1,1.0], hspace=0.28)

    # ---- full year ----
    ax = fig.add_subplot(gs[0]); n=len(c)
    candles(ax,o,h,l,c)
    ax.plot(e20,color='#4575b4',lw=1.1,label='EMA20')
    ax.plot(e50,color='#f46d43',lw=1.1,label='EMA50')
    ax.plot(e200,color='#7b3294',lw=1.2,label='EMA200')
    ax.set_xlim(-1,n); ax.legend(loc='upper left',fontsize=9,ncol=3)
    ax.set_title(f'#{rank}  {sym}   daily RSI(14)={rsi:.1f}   close={c[-1]:.2f}   '
                 f'[{d[0]} .. {d[-1]}]  {n} daily bars', fontsize=13, weight='bold')
    ax.grid(alpha=0.18); ax.set_ylabel('price')
    tk=range(0,n,15); ax.set_xticks(list(tk)); ax.set_xticklabels([d[i][2:] for i in tk],fontsize=7,rotation=45)

    axr = fig.add_subplot(gs[1], sharex=ax)
    axr.plot(rs,color='#111',lw=1.0); axr.axhline(70,color='#d73027',lw=0.7,ls='--')
    axr.axhline(60,color='#888',lw=0.7,ls=':'); axr.axhline(30,color='#1a9850',lw=0.7,ls='--')
    axr.set_ylim(10,95); axr.set_ylabel('RSI14'); axr.grid(alpha=0.18)
    plt.setp(ax.get_xticklabels(), visible=False)

    # ---- zoom: last 110 bars ----
    k = min(110, n); s = n-k
    ax2 = fig.add_subplot(gs[2])
    candles(ax2,o[s:],h[s:],l[s:],c[s:])
    ax2.plot(e20[s:],color='#4575b4',lw=1.2)
    ax2.plot(e50[s:],color='#f46d43',lw=1.2)
    if not np.isnan(e200[s:]).all(): ax2.plot(e200[s:],color='#7b3294',lw=1.3)
    hi=h[s:].max(); ax2.axhline(hi,color='#666',lw=0.9,ls='--')
    ax2.annotate(f'{k}-bar high {hi:.2f}',(0,hi),xytext=(2,4),textcoords='offset points',fontsize=9,color='#444')
    ax2.set_xlim(-1,k); ax2.grid(alpha=0.18); ax2.set_ylabel('price')
    ax2.set_title(f'{sym} — zoom, last {k} daily bars', fontsize=11)
    tk2=range(0,k,5); ax2.set_xticks(list(tk2)); ax2.set_xticklabels([d[s+i][5:] for i in tk2],fontsize=7,rotation=45)

    axv = fig.add_subplot(gs[3], sharex=ax2)
    avg = np.convolve(v, np.ones(20)/20, mode='same')
    axv.bar(range(k), v[s:], color=[UP if c[s+i]>=o[s+i] else DN for i in range(k)], width=0.62)
    axv.plot(avg[s:], color='#333', lw=1.0)
    axv.set_ylabel('vol'); axv.grid(alpha=0.18)
    plt.setp(ax2.get_xticklabels(), visible=False)

    fig.savefig(f'{outdir}/{rank:02d}_{sym}.png', dpi=105, bbox_inches='tight', facecolor='white')
    plt.close(fig)

if __name__ == '__main__':
    rank = {r['symbol']: (i+1, r['rsi14']) for i,r in enumerate(json.load(open('rsi15/ranking.json')))}
    top = [l.strip() for l in open('rsi15/top15.txt') if l.strip()]
    all_g = load_all()
    for s in top:
        r,q = rank[s]; plot(s, all_g[s], r, q); print('ok', r, s)
