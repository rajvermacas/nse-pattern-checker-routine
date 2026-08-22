import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np, json, sys
sys.path.insert(0,'rsi15')
from daily_series import load_all, ema
UP='#1a9850'; DN='#d73027'
g_all=load_all()
top=[l.strip() for l in open('rsi15/top15.txt') if l.strip()]
rank={r['symbol']:(i+1,r['rsi14']) for i,r in enumerate(json.load(open('rsi15/ranking.json')))}
fig,axes=plt.subplots(5,3,figsize=(21,24))
for ax,s in zip(axes.ravel(),top):
    g=g_all[s]; o,h,l,c=[g[k].values[-130:].astype(float) for k in ('open','high','low','close')]
    e20=ema(g['close'].values,20)[-130:]; e50=ema(g['close'].values,50)[-130:]
    for i in range(len(o)):
        col=UP if c[i]>=o[i] else DN
        ax.vlines(i,l[i],h[i],color=col,lw=0.7)
        lo,hi=min(o[i],c[i]),max(o[i],c[i])
        ax.add_patch(Rectangle((i-0.32,lo),0.64,max(hi-lo,(h[i]-l[i])*0.004 or 1e-9),facecolor=col,edgecolor=col,lw=0.4))
    ax.plot(e20,color='#4575b4',lw=1.0); ax.plot(e50,color='#f46d43',lw=1.0)
    ax.axhline(h.max(),color='#666',ls='--',lw=0.8)
    r,q=rank[s]; ax.set_title(f'#{r} {s}  RSI {q:.1f}',fontsize=12,weight='bold')
    ax.set_xlim(-1,len(o)); ax.grid(alpha=0.15); ax.set_xticks([])
fig.suptitle('Top 15 of 107 by daily RSI(14) — last 130 daily bars (as of 2026-08-21)',fontsize=17,weight='bold',y=0.995)
fig.tight_layout(rect=[0,0,1,0.985])
fig.savefig('rsi15/contact_sheet.png',dpi=88,facecolor='white',bbox_inches='tight')
print('saved')
