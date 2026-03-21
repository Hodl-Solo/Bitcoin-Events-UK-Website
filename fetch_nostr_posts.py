import json, time, websocket, bech32

NPUB = "npub1g8ag22auywa5c5de6w9ujenpyhrrp9qq8sjzram02xldttmmwurqfd0hqk"
RELAYS = ["wss://relay.ditto.pub", "wss://relay.primal.net", "wss://nos.lol", "wss://relay.damus.io"]
COUNT = 3

def npub_hex(npub):
    d = npub[5:]
    C = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    v = [C.find(c.lower()) for c in d]
    w = bech32.convertbits(v, 5, 8, pad=True)
    return bytes(w).hex()

pk = npub_hex(NPUB)
print(f"Pubkey: {pk}")
print(f"Testing npub conversion...")
test_npub = "npub1qny3tkwh0sdjk5gzv689xjd2xqjt0p3rj9gzu5l6r7ce8gyt5gxq3vgzhu"
test_hex = npub_hex(test_npub)
print(f"Test npub hex (known): {test_hex}")
if not pk:
    print("ERROR: bad npub")
    exit(1)

def fetch(relay, pk, lim):
    print(f"Connecting to {relay}...")
    try:
        ws = websocket.create_connection(relay, timeout=15)
        # First, let's get our own profile to verify connection
        ws.send(json.dumps(["REQ","test",{"authors":[pk],"kinds":[0],"limit":1}]))
        time.sleep(2)
        
        # Clear and send actual request
        ws.send(json.dumps(["CLOSE","test"]))
        time.sleep(0.5)
        ws.send(json.dumps(["REQ","posts",{"authors":[pk],"kinds":[1],"limit":lim}]))
        
        posts = []
        t = time.time()
        received_eose = False
        while time.time()-t < 12:
            try:
                m = ws.recv()
                if m:
                    d = json.loads(m)
                    print(f"  Received: {d[0] if d else 'unknown'}")
                    if d[0]=="EVENT" and d[1]=="posts":
                        content = d[2].get('content','')[:50]
                        posts.append({'id':d[2].get('id',''),'content':d[2].get('content',''),'created_at':d[2].get('created_at',0)})
                        print(f"  Got post: {content}...")
                        if len(posts)>=lim: break
                    elif d[0]=="EOSE":
                        received_eose = True
                        print(f"  EOSE received")
                        break
            except Exception as e:
                print(f"  recv error: {e}")
                pass
        ws.close()
        print(f"  Total posts: {len(posts)}")
        return posts
    except Exception as e:
        print(f"  Connection error: {e}")
        return []

print(f"\nFetching posts for pubkey: {pk}")
all_p = []
seen = set()
for r in RELAYS:
    if len(all_p)>=COUNT: break
    print(f"\nTrying relay: {r}")
    ps = fetch(r, pk, COUNT)
    for p in ps:
        if p['id'] not in seen:
            seen.add(p['id'])
            all_p.append(p)
    print(f"Accumulated: {len(all_p)} posts")

for p in all_p:
    a = int(time.time())-p.get('created_at',0)
    p['created_human'] = f"{a//60}m ago" if a<3600 else f"{a//3600}h ago" if a<86400 else f"{a//86400}d ago"

all_p.sort(key=lambda x:x.get('created_at',0), reverse=True)
all_p = all_p[:COUNT]
if not all_p:
    print("\nWARNING: No posts found from any relay!")
    all_p = [{'id':'demo','content':'No posts fetched. Check relay connectivity.','created_at':int(time.time()),'created_human':'Just now'}]

with open('_data/nostr-posts.json','w') as f:
    json.dump({'last_updated':int(time.time()),'posts':all_p}, f, indent=2)
print(f"\nSaved {len(all_p)} posts")
