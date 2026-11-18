import pickle,math,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
segs,vias,fps=pickle.load(open('tools/r10.pkl','rb'))
# P3 pin x positions from where clock traces end (y~128)
def end(net):
    pts=[p for s in segs if s['net']==net for p in (s['a'],s['b'])]
    return max(pts,key=lambda p:p[1])
p8,p11,p14=end('Net-(P3-Pin_8)'),end('Net-(P3-Pin_11)'),end('Net-(P3-Pin_14)')
print('P3 pins',p8,p11,p14)
clk=('Net-(P3-Pin_8)','Net-(P3-Pin_11)','Net-(P3-Pin_14)','Net-(U2-CLK0)','Net-(U2-CLK1)','Net-(U2-CLK2)','Net-(U2-XA)','Net-(U2-XB)')
zone=(62,108,86,127.5)
inzone=set()
fig,ax=plt.subplots(figsize=(14,9))
for s in segs:
    x=[s['a'][0],s['b'][0]]; y=[s['a'][1],s['b'][1]]
    if s['net'] in clk:
        ax.plot(x,y,'-',color='#999',lw=1.2,alpha=.5,dashes=(2,2)); continue
    mid=((x[0]+x[1])/2,(y[0]+y[1])/2)
    hit=any(zone[0]<=px<=zone[2] and zone[1]<=py<=zone[3] for px,py in (s['a'],s['b'],mid))
    if hit: inzone.add(s['net'])
    ax.plot(x,y,'-' if s['L']=='F.Cu' else ':',color='#e377c2' if hit else '#cccccc',lw=s['w']*5)
ax.add_patch(Rectangle((zone[0],zone[1]),zone[2]-zone[0],zone[3]-zone[1],fill=False,ec='#e377c2',lw=1.5,ls='--'))
ax.text(zone[0]+.3,zone[1]-.6,'area to clear (pink traces re-route around it)',color='#c2185b',fontsize=9)
# proposed parts
U2=(73.2,116.0)
ax.add_patch(Rectangle((U2[0]-2.5,U2[1]-2.5),5,5,fc='#ffe08a',ec='k',zorder=5)); ax.text(*U2,'U2\nSi5351',ha='center',va='center',fontsize=8,zorder=6)
ax.add_patch(Rectangle((64.5,113.5),5,3.2,fc='#ffe08a',ec='k',zorder=5)); ax.text(67,115.1,'Y1',ha='center',va='center',fontsize=8,zorder=6)
ax.plot([69.5,70.7],[115.1,115.6],'k-',lw=1.2,zorder=4); ax.plot([69.5,70.7],[115.1,116.4],'k-',lw=1.2,zorder=4)
cols={'CLK0':'#d62728','CLK1':'#1f77b4','CLK2':'#2ca02c'}
plan=[('CLK0',(75.7,117.0),p8,(79.5,121.5),'R C4'),('CLK1',(74.0,118.5),p11,(73.2,122.5),'R C6'),('CLK2',(72.4,118.5),p14,(66.9,121.5),'R C5')]
for name,start,pin,cap,lab in plan:
    path=[start,(cap[0],cap[1]-2.2),cap,(pin[0],pin[1]-2.0),pin]
    xs,ys=zip(*path); ax.plot(xs,ys,'-',color=cols[name],lw=3.2,solid_capstyle='round',zorder=4)
    ax.add_patch(Rectangle((cap[0]-0.9,cap[1]-1.6),1.8,1.4,fc='white',ec=cols[name],zorder=6))
    ax.text(cap[0]+1.2,cap[1]-0.9,lab,fontsize=7,color=cols[name],zorder=6)
# ground guard traces with stitching vias between clocks
for gx in ((70.0,76.6),):
    pass
for x0,x1 in ((70.4,69.6),(76.6,77.0)):
    ax.plot([x0,x1],[119.5,127.2],'-',color='#555',lw=1.5,zorder=3)
    for t in (0,.33,.66,1): ax.plot(x0+(x1-x0)*t,119.5+7.7*t,'o',ms=4,mfc='white',mec='#555',zorder=4)
ax.text(78.5,126.3,'GND guard + vias\n(P3 GND pins 7,9,10,12,13\nalready sit between clocks)',fontsize=7,color='#333')
# decoupling and I2C
for (x,y,l) in ((76.6,113.2,'C1'),(70.0,112.2,'C2')):
    ax.add_patch(Rectangle((x-0.9,y-0.7),1.8,1.4,fc='#d0e8ff',ec='k',zorder=6)); ax.text(x,y-1.3,l,fontsize=7,ha='center')
ax.add_patch(Rectangle((78.2,109.8),3,2.2,fc='#d0f0d0',ec='k',zorder=6)); ax.text(79.7,110.9,'LDO',fontsize=7,ha='center',va='center',zorder=7)
ax.annotate('',xy=(74,113.5),xytext=(87,95),arrowprops=dict(arrowstyle='<->',color='#8c564b',lw=2,ls='--'))
ax.text(82,103,'SDA/SCL only\n(slow; vias OK)',color='#8c564b',fontsize=8)
ax.text(61.2,96.6,'old U2 spot\n(freed)',fontsize=8,color='#777',ha='center',bbox=dict(fc='white',ec='#999',ls='--'))
ax.plot(61.15,96.43,'x',color='#777',ms=10)
for r,v,x,y,L,f in fps:
    if r in('U2','Y1','C1','C2','C4','C5','C6'): continue
    if r: ax.text(x,y,r,fontsize=8,ha='center',color='k',zorder=5,bbox=dict(fc='yellow',alpha=.5,lw=0,pad=0.5))
for n,p in (('P3-8',p8),('P3-11',p11),('P3-14',p14)): ax.text(p[0],p[1]+1.3,n,ha='center',fontsize=7)
ax.set_ylim(136,72); ax.set_xlim(37,134); ax.set_aspect('equal')
ax.set_title('Rev 10-Optic: PROPOSED Si5351 placement (sketch, not to exact footprint size)\ncoloured = new clock routes, all top copper; grey dashed = today\'s clock routes',fontsize=11)
plt.tight_layout(); plt.savefig('/tmp/claude-0/out/board_review/rev10_proposed_placement.png',dpi=110)
print('nets in zone:',sorted(inzone))
