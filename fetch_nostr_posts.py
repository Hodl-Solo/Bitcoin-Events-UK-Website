import json, time, websocket, bech32

# BEUK account
BEUK_NPUB = "npub1g8ag22auywa5c5de6w9ujenpyhrrp9qq8sjzram02xldttmmwurqfd0hqk"
# Simon's personal npub (from USER.md)
SIMON_NPUB = "npub1f69t2s7uzljr626ctm0k3mufx5vlv4a2jqwac0w0gxwghp4w5zpq0jva3d"

RELAYS = [
    "wss://relay.ditto.pub",
    "wss://relay.primal.net", 
    "wss://nos.lol",
    "wss://relay.damus.io",
    "wss://wot.gab.com",
    "wss://nostr.wine"
]
COUNT = 3

def npub_hex(npub):
    d = npub[5:]
    C = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    v = [C.find(c.lower()) for c in d]
    w = bech32.convertbits(v, 5, 8, pad=True)
    return bytes(w).hex()

def fetch(relay, pk, lim):
    print(f"  Connecting to {relay}...")
    try:
        ws = websocket.create_connection(relay, timeout=12)
        ws.send(json.dumps(["REQ","posts",{"authors":[pk],"kinds":[1],"limit":lim}]))
        posts = []
        t = time.time()
        while time.time()-t < 10:
            try:
                m = ws.recv()
                if m:
                    d = json.loads(m)
                    if d[0]=="EVENT" and d[1]=="posts":
                        posts.append({'id':d[2].get('id',''),'content':d[2].get('content',''),'created_at':d[2].get('created_at',0)})
                        print(f"    Got post!")
                        if len(posts)>=lim: break
                    elif d[0]=="EOSE":
                        print(f"    EOSE")
                        break
            except: pass
        ws.close()
        return posts
    except Exception as e:
        print(f"    Error: {e}")
        return []

print("=== Testing BEUK account ===")
pk_beuk = npub_hex(BEUK_NPUB)
print(f"BEUK Pubkey: {pk_beuk}")
for r in RELAYS:
    ps = fetch(r, pk_beuk, COUNT)
    if ps:
        print(f"  Found {len(ps)} posts!")
        break

print("\n=== Testing Simon's personal account ===")
pk_simon = npub_hex(SIMON_NPUB)
print(f"Simon's Pubkey: {pk_simon}")
for r in RELAYS:
    ps = fetch(r, pk_simon, COUNT)
    if ps:
        print(f"  Found {len(ps)} posts!")
        break

print("\n=== All posts (combined) ===")
all_p = []
seen = set()
for pk, name in [(pk_beuk, "BEUK"), (pk_simon, "Simon")]:
    for r in RELAYS:
        if len(all_p) >= COUNT: break
        ps = fetch(r, pk, COUNT)
        for p in ps:
            if p['id'] not in seen:
                seen.add(p['id'])
                all_p.append(p)

for p in all_p:
    a = int(time.time())-p.get('created_at',0)
    p['created_human'] = f"{a//60}m ago" if a<3600 else f"{a//3600}h ago" if a<86400 else f"{a//86400}d ago"

all_p.sort(key=lambda x:x.get('created_at',0), reverse=True)
all_p = all_p[:COUNT]

if not all_p:
    all_p = [{'id':'demo','content':'No posts found from relays. BEUK account may not have posted yet.','created_at':int(time.time()),'created_human':'Just now'}]

with open('_data/nostr-posts.json','w') as f:
    json.dump({'last_updated':int(time.time()),'posts':all_p}, f, indent=2)
print(f"Saved {len(all_p)} posts")
