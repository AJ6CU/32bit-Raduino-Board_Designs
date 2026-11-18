import pickle,math,sys,collections
segs,vias,fps=pickle.load(open(sys.argv[1],'rb'))
clk=set(sys.argv[2].split(','))
def proj(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; L2=dx*dx+dy*dy
    return ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L2 if L2 else 0
def dist_pt_line(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    return abs((p[0]-a[0])*dy-(p[1]-a[1])*dx)/L
res=collections.defaultdict(lambda:[0,99,set()])
for s in segs:
    if s['net'] not in clk: continue
    a,b=s['a'],s['b']; L=math.dist(a,b)
    if L<0.2: continue
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for t in segs:
        if t['net']==s['net']: continue
        c,d=t['a'],t['b']; L2=math.dist(c,d)
        if L2<0.2: continue
        ang2=math.atan2(d[1]-c[1],d[0]-c[0])
        da=abs((ang-ang2+math.pi/2)%math.pi-math.pi/2)
        if da>math.radians(12): continue
        t0,t1=sorted((proj(c,a,b),proj(d,a,b)))
        ov=(min(1,t1)-max(0,t0))*L
        if ov<1: continue
        gap=(dist_pt_line(c,a,b)+dist_pt_line(d,a,b))/2-(s['w']+t['w'])/2
        same = s['L']==t['L']
        lim=3.0 if same else 1.0
        if gap>lim: continue
        k=(s['net'],t['net'],s['L'] if same else s['L']+'/'+t['L'])
        r=res[k]; r[0]+=ov; r[1]=min(r[1],gap)
for (a,b,L),(ov,g,_) in sorted(res.items(),key=lambda x:-x[1][0]):
    print(f'{a:18s} || {b:22s} {L:12s} overlap {ov:5.1f} mm  min edge gap {g:5.2f} mm')
