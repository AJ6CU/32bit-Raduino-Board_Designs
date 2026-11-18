import sys,re
exec(open('tools/pcb.py').read().split("print('layers'")[0])
for f in get(T,'footprint'):
    ref=[p[2] for p in get(f,'property') if p[1]=='Reference']
    ref=ref[0] if ref else ''
    if ref not in sys.argv[2:]: continue
    for p in get(f,'pad'):
        print(ref,p[1],netname(p))
