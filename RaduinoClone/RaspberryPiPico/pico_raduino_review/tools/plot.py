import pickle,sys,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
segs,vias,fps=pickle.load(open(sys.argv[1],'rb'))
hi={'Net-(P3-Pin_8)':'#d62728','Net-(U2-CLK0)':'#d62728','Net-(P3-Pin_11)':'#1f77b4','Net-(U2-CLK1)':'#1f77b4','Net-(P3-Pin_14)':'#2ca02c','Net-(U2-CLK2)':'#2ca02c','PTT':'#ff7f0e','Net-(P3-Pin_15)':'#9467bd','SDA':'#8c564b','SCL':'#8c564b'}
fig,ax=plt.subplots(figsize=(14,9))
for s in segs:
    c=hi.get(s['net'],'#bbbbbb'); ls='-' if s['L']=='F.Cu' else ':'
    lw=s['w']*8 if s['net'] in hi else s['w']*5
    ax.plot([s['a'][0],s['b'][0]],[s['a'][1],s['b'][1]],ls,color=c,lw=lw,solid_capstyle='round',zorder=3 if s['net'] in hi else 1)
for x,y,n in vias: ax.plot(x,y,'o',ms=4,color=hi.get(n,'#666'),mfc='white',zorder=4)
for r,v,x,y,L,f in fps:
    if r: ax.text(x,y,r,fontsize=8,ha='center',color='k',zorder=5,bbox=dict(fc='yellow',alpha=.5,lw=0,pad=0.5))
ax.set_ylim(136,72); ax.set_xlim(37,134); ax.set_aspect('equal')
from matplotlib.lines import Line2D
L=[Line2D([0],[0],color=c,lw=3) for c in ['#d62728','#1f77b4','#2ca02c','#ff7f0e','#9467bd','#8c564b']]
ax.legend(L,['CLK0','CLK1','CLK2','PTT','12 V in (P3-15)','I2C'],loc='upper left',fontsize=9)
ax.set_title(sys.argv[3]+'   (solid = top copper, dotted = bottom copper)')
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=110)
