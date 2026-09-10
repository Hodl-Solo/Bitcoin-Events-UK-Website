# Bitcoin Events UK Website

Live site: https://bitcoinevents.uk

## Updating meetup listings

`UK-Bitcoin-Meetups-Directory.md` is the single source of truth for both the meetup directory and the map.

To update the website:

1. Edit `UK-Bitcoin-Meetups-Directory.md`.
2. Update the relevant meetup row or add a new row under the correct region.
3. Use one of these statuses:
   - `Active` — shown normally in the directory and on the map
   - `Paused` — shown as paused in the directory and as a grey marker on the map
   - `Remove` — excluded from both the directory and the map
4. Keep the `Map` column in `latitude,longitude` format. If a meetup rotates venues, use a sensible town or area centre.
5. Commit the change to `main`.

GitHub Actions automatically runs `generate-meetups.py`, regenerates `meetups-source.html`, and updates the live directory data. The Leaflet/OpenStreetMap map reads those same generated meetup records. Do not edit `meetups-source.html` manually.

## Main website files

- `index.html` — live homepage
- `styles.css` — site styling
- `map.css` — Leaflet map styling
- `script.js` — search, filters, meetup rendering, expected-date logic and map rendering
- `UK-Bitcoin-Meetups-Directory.md` — editable meetup master list and map coordinates
- `generate-meetups.py` — converts the Markdown master list into website data
- `meetups-source.html` — generated website data; do not edit manually
- `.github/workflows/dynamic-meetup-counter.yml` — automatic rebuild workflow
- `BitcoinEventsUK new logo trans.png` — site logo and favicon
- `CNAME` — custom domain configuration
