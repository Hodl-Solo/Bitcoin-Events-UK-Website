import json, time, websocket, bech32

BEUK_NPUB = "npub1g8ag22auywa5c5de6w9ujenpyhrrp9qq8sjzram02xldttmmwurqfd0hqk"
RELAYS = [
    "wss://atlas.nostr.land",
    "wss://bitcoiner.social",
    "wss://eden.nostr.land",
    "wss://nos.lol"
]
COUNT = 5

def npub_hex(npub):
    d = npub[5:]
    C = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    v = [C.find(c.lower()) for c in d]
    w = bech32.convertbits(v, 5, 8, pad=True)
    return bytes(w).hex()

def fetch(relay, pk, kinds, lim):
    try:
        ws = websocket.create_connection(relay, timeout=15)
        ws.send(json.dumps(["REQ","p",{"authors":[pk],"kinds":kinds,"limit":lim}]))
        posts = []
        t = time.time()
        while time.time()-t < 12:
            try:
                m = ws.recv()
                if m:
                    d = json.loads(m)
                    if d[0]=="EVENT" and d[1]=="p":
                        posts.append({'id':d[2].get('id',''),'content':d[2].get('content',''),'created_at':d[2].get('created_at',0),'kind':d[2].get('kind',1)})
                        if len(posts)>=lim: break
                    elif d[0]=="EOSE": break
            except: pass
        ws.close()
        return posts
    except Exception as e:
        print(f"    Error: {str(e)[:50]}")
        return []

pk = npub_hex(BEUK_NPUB)
print(f"Pubkey: {pk[:20]}...")

all_p = []
seen = set()
for kind in [1, 6]:
    for r in RELAYS:
        if len(all_p) >= COUNT: break
        print(f"Trying {r} for kind {kind}...")
        ps = fetch(r, pk, [kind], COUNT)
        for p in ps:
            if p['id'] not in seen:
                seen.add(p['id'])
                p['kind'] = kind
                all_p.append(p)
        print(f"  Got {len(ps)}")

for p in all_p:
    a = int(time.time())-p.get('created_at',0)
    p['created_human'] = f"{a//60}m ago" if a<3600 else f"{a//3600}h ago" if a<86400 else f"{a//86400}d ago"

all_p.sort(key=lambda x:x.get('created_at',0), reverse=True)
all_p = all_p[:COUNT]

if not all_p:
    all_p = [{'id':'demo','content':'No posts found from BEUK relays.','created_at':int(time.time()),'created_human':'Just now'}]

with open('_data/nostr-posts.json','w') as f:
    json.dump({'last_updated':int(time.time()),'posts':all_p}, f, indent=2)
print(f"Saved {len(all_p)} posts")
