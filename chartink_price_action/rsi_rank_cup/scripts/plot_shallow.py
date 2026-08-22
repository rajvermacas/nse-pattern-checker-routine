import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np, json, sys, os
sys.path.insert(0,'rsi15')
from daily_series import load_all, ema, rsi_series
UP='#1a9850'; DN='#d73027'
def candles(ax,o,h,l,c,w=0.62):
    for i in range(len(o)):
        col=UP if c[i]>=o[i] else DN
        ax.vlines(i,l[i],h[i],color=col,lw=0.9,zorder=2)
        lo,hi=min(o[i],c[i]),max(o[i],c[i])
        ax.add_patch(Rectangle((i-w/2,lo),w,max(hi-lo,(h[i]-l[i])*0.004 or 1e-9),
                     facecolor=col,edgecolor=col,lw=0.5,zorder=3))

hits=json.load(open('rsi15/shallow_actionable.json'))
g_all=load_all(); os.makedirs('rsi15/shallow_charts',exist_ok=True)
for pos,H in enumerate(hits,1):
    sym=H['symbol']; g=g_all[sym]
    o,h,l,c,v=[g[k].values.astype(float) for k in ('open','high','low','close','volume')]
    d=g['d'].values; n=len(c)
    e20,e50=ema(c,20),ema(c,50); e200=ema(c,200); rs=rsi_series(c)
    i_rim=int(np.where(d==H['rim_date'])[0][0])
    rim=H['rim']; low=rim*(1-H['depth_pct']/100)

    fig=plt.figure(figsize=(16,10))
    gs=fig.add_gridspec(3,1,height_ratios=[3.4,1.0,1.0],hspace=0.26)
    k=min(150,n); s=n-k
    ax=fig.add_subplot(gs[0]); candles(ax,o[s:],h[s:],l[s:],c[s:])
    ax.plot(e20[s:],color='#4575b4',lw=1.2,label='EMA20')
    ax.plot(e50[s:],color='#f46d43',lw=1.2,label='EMA50')
    ax.plot(e200[s:],color='#7b3294',lw=1.3,label='EMA200')
    rr=i_rim-s
    ax.axvspan(max(0,rr-int(H['base_bars'])*3),rr,color='#1a9850',alpha=0.07,zorder=0)
    ax.axvspan(rr,min(k-1,rr+int(H['base_bars'])),color='#4575b4',alpha=0.13,zorder=0)
    ax.axhline(rim,color='#7b3294',lw=1.4,ls='--',zorder=4)
    ax.axhline(low,color='#d73027',lw=1.4,ls='--',zorder=4)
    ax.text(k*1.004,rim,f'rim {rim:.2f}',fontsize=10,color='#7b3294',va='center',weight='bold')
    ax.text(k*1.004,low,f'base low {low:.2f}',fontsize=10,color='#d73027',va='center',weight='bold')
    ax.scatter([rr],[rim],s=110,marker='^',color='#111',zorder=6)
    ax.scatter([k-1],[c[-1]],s=140,marker='o',facecolor='none',edgecolor='#111',lw=2,zorder=6)
    ax.set_xlim(-1,k); ax.legend(loc='upper left',fontsize=9,ncol=3); ax.grid(alpha=0.16)
    ax.set_title(f"{pos}. {sym}   RSI {H['rsi']}   close {c[-1]:.2f}\n"
                 f"rally +{H['rally_pct']}%  ->  base {H['depth_pct']}% deep, {H['base_bars']} bars from {H['rim_date']}  ->  "
                 f"{H['state']} ({H['vs_rim_pct']:+.1f}% vs rim)",fontsize=12,weight='bold')
    tk=range(0,k,7); ax.set_xticks(list(tk)); ax.set_xticklabels([d[s+i][5:] for i in tk],fontsize=7,rotation=45)

    axr=fig.add_subplot(gs[1],sharex=ax); axr.plot(rs[s:],color='#111',lw=1.0)
    axr.axhline(70,color='#d73027',lw=.7,ls='--'); axr.axhline(60,color='#888',lw=.7,ls=':')
    axr.axvspan(rr,min(k-1,rr+int(H['base_bars'])),color='#4575b4',alpha=0.13)
    axr.set_ylim(10,95); axr.set_ylabel('RSI14'); axr.grid(alpha=0.16)
    plt.setp(ax.get_xticklabels(),visible=False)
    axv=fig.add_subplot(gs[2],sharex=ax)
    avg=np.convolve(v,np.ones(20)/20,mode='same')
    axv.bar(range(k),v[s:],color=[UP if c[s+i]>=o[s+i] else DN for i in range(k)],width=0.62)
    axv.plot(avg[s:],color='#333',lw=1.0)
    axv.axvspan(rr,min(k-1,rr+int(H['base_bars'])),color='#4575b4',alpha=0.13)
    axv.set_ylabel('vol'); axv.grid(alpha=0.16); plt.setp(axr.get_xticklabels(),visible=False)
    fig.savefig(f'rsi15/shallow_charts/{pos:02d}_{sym}.png',dpi=100,bbox_inches='tight',facecolor='white')
    plt.close(fig)
print('rendered',len(hits))
