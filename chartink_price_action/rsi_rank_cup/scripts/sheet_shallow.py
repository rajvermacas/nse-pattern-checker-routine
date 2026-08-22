import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np, json, sys
sys.path.insert(0,'rsi15')
from daily_series import load_all, ema
UP='#1a9850'; DN='#d73027'
hits=json.load(open('rsi15/shallow_actionable.json')); g_all=load_all()
fig,axes=plt.subplots(6,4,figsize=(24,26))
for ax in axes.ravel(): ax.axis('off')
for ax,H in zip(axes.ravel(),hits):
    ax.axis('on'); sym=H['symbol']; g=g_all[sym]
    K=90; o,h,l,c=[g[k].values[-K:].astype(float) for k in ('open','high','low','close')]
    d=g['d'].values; n=len(g); s=n-K
    e20=ema(g['close'].values,20)[-K:]
    for i in range(K):
        col=UP if c[i]>=o[i] else DN
        ax.vlines(i,l[i],h[i],color=col,lw=0.75)
        lo,hi=min(o[i],c[i]),max(o[i],c[i])
        ax.add_patch(Rectangle((i-0.33,lo),0.66,max(hi-lo,(h[i]-l[i])*0.004 or 1e-9),facecolor=col,edgecolor=col,lw=0.4))
    ax.plot(e20,color='#4575b4',lw=1.0)
    rim=H['rim']; low=rim*(1-H['depth_pct']/100)
    ax.axhline(rim,color='#7b3294',ls='--',lw=1.1); ax.axhline(low,color='#d73027',ls='--',lw=1.1)
    ir=int(np.where(d==H['rim_date'])[0][0])-s
    if 0<=ir<K: ax.axvspan(ir,min(K-1,ir+int(H['base_bars'])),color='#4575b4',alpha=0.15)
    tag='IN BASE' if not H['resolved'] else f"{H['vs_rim_pct']:+.1f}%"
    ax.set_title(f"{sym}   {H['depth_pct']}% / {H['base_bars']}b   {tag}",fontsize=11,weight='bold')
    ax.set_xlim(-1,K); ax.set_xticks([]); ax.grid(alpha=0.15)
fig.suptitle('Sub-7% bases, still live — 22 of 107 (last 90 daily bars; purple = rim, red = base low, blue span = base)',
             fontsize=17,weight='bold',y=0.996)
fig.tight_layout(rect=[0,0,1,0.988])
fig.savefig('rsi15/shallow_sheet.png',dpi=82,facecolor='white',bbox_inches='tight')
print('saved')
