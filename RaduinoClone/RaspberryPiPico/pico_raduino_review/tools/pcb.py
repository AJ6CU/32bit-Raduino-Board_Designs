import re, sys, math, collections
src=open(sys.argv[1]).read()
def sexp(s):
    tok=re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+',s); st=[[]]
    for t in tok:
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t.strip('"'))
    return st[0][0]
T=sexp(src)
def get(n,k): return [c for c in n if isinstance(c,list) and c and c[0]==k]
def one(n,k):
    g=get(n,k); return g[0] if g else None
nets={}
for n in get(T,'net'): nets[n[1]]=n[2] if len(n)>2 else n[1]
def netname(x):
    v=one(x,'net');
    if not v: return ''
    return nets.get(v[1],v[1]) if len(v)>1 else ''
print('layers', [l[1] for l in get(one(T,'layers'),None) or []] if False else '')
for l in one(T,'layers')[1:]: print('  ',l[:3])
segs=[]
for s in get(T,'segment'):
    a=one(s,'start');b=one(s,'end')
    segs.append(dict(a=(float(a[1]),float(a[2])),b=(float(b[1]),float(b[2])),w=float(one(s,'width')[1]),L=one(s,'layer')[1],net=netname(s)))
vias=[(float(one(v,'at')[1]),float(one(v,'at')[2]),netname(v)) for v in get(T,'via')]
print('segments',len(segs),'vias',len(vias))
fps=[]
for f in get(T,'footprint'):
    at=one(f,'at'); ref=''; val=''
    for p in get(f,'property'):
        if p[1]=='Reference': ref=p[2]
        if p[1]=='Value': val=p[2]
    for t in get(f,'fp_text'):
        if t[1]=='reference': ref=t[2]
        if t[1]=='value': val=t[2]
    fps.append((ref,val,float(at[1]),float(at[2]),one(f,'layer')[1], f[1]))
for f in sorted(fps): print('FP',f)
print('ZONES')
for z in get(T,'zone'):
    L=one(z,'layer') or one(z,'layers'); 
    pts=one(one(z,'polygon'),'pts')
    xy=[(float(p[1]),float(p[2])) for p in pts if p[0]=='xy']
    xs=[p[0] for p in xy]; ys=[p[1] for p in xy]
    fills=get(z,'filled_polygon')
    print(' ',netname(z),L[1:],'bbox',min(xs),min(ys),max(xs),max(ys),'fills',len(fills))
# per net length
nl=collections.defaultdict(float); nlay=collections.defaultdict(set)
for s in segs:
    nl[s['net']]+=math.dist(s['a'],s['b']); nlay[s['net']].add(s['L'])
print('NETS')
for k,v in sorted(nl.items(),key=lambda x:-x[1]): print(f'  {k:30s} {v:7.1f}mm {sorted(nlay[k])} vias={sum(1 for x in vias if x[2]==k)}')
ec=one(T,'general')
import pickle; pickle.dump((segs,vias,fps),open('/tmp/claude-0/raduino/tools/'+sys.argv[2]+'.pkl','wb'))
