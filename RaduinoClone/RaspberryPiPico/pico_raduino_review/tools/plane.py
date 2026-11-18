import sys,math
exec(open('tools/pcb.py').read().split("print('layers'")[0])
st=one(one(T,'setup'),'stackup')
if st:
  for l in get(st,'layer'):
    th=one(l,'thickness'); ty=one(l,'type'); 
    print('  stack',l[1],ty[1] if ty else '',th[1] if th else '')
segs=[]
for s in get(T,'segment'):
    a=one(s,'start');b=one(s,'end')
    segs.append(((float(a[1]),float(a[2])),(float(b[1]),float(b[2])),float(one(s,'width')[1]),one(s,'layer')[1],netname(s)))
polys={}
for z in get(T,'zone'):
    for fp in get(z,'filled_polygon'):
        L=one(fp,'layer')[1]
        xy=[(float(p[1]),float(p[2])) for p in one(fp,'pts') if p[0]=='xy']
        polys.setdefault(L,[]).append(xy)
def inside(pt,poly):
    x,y=pt; c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[i-1]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
VIAS=[(float(one(v,"at")[1]),float(one(v,"at")[2])) for v in get(T,"via")]
want=sys.argv[2].split(',')
for net in want:
    tot=0; bad=0; out=[]
    for a,b,w,L,n in segs:
        if n!=net: continue
        ref='In1.Cu' if L=='F.Cu' else 'In2.Cu'
        steps=max(2,int(math.dist(a,b)/0.25))
        for i in range(steps+1):
            p=(a[0]+(b[0]-a[0])*i/steps,a[1]+(b[1]-a[1])*i/steps)
            tot+=1
            if not any(inside(p,pg) for pg in polys.get(ref,[])) and min([math.dist(p,v) for v in VIAS]+[9]) > 0.9 and p[1] < 126.5: bad+=1; out.append((L,round(p[0],1),round(p[1],1)))
    print(f'{net:20s} points {tot}, not over its reference plane: {bad}', sorted(set(out))[:12])
    print('   widths', sorted(set((w,L) for a,b,w,L,n in segs if n==net)))
