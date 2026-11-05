import re,sys,html
t=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
rows=re.findall(r'<tr><td[^>]*>([^<]{1,60})</td><td[^>]*>(.*?)</td></tr>',t)
seen=set()
for k,v in rows:
    v=html.unescape(re.sub(r'<[^>]+>','',v)).strip()
    if (k,v) in seen: continue
    seen.add((k,v)); print(f"  {k}: {v}")
