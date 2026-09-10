# Bitcoin Events UK Website

Live site: https://bitcoinevents.uk

## Updating meetup listings

`UK-Bitcoin-Meetups-Directory.md` is the single source of truth for meetup data.

To update the website:

1. Edit `UK-Bitcoin-Meetups-Directory.md`.
2. Update the relevant meetup row or add a new row under the correct region.
3. Use one of these statuses:
   - `Active` — shown normally on the website
   - `Paused` — shown but marked as paused
   - `Remove` — excluded from the website
4. Commit the change to `main`.

GitHub Actions automatically runs `generate-meetups.py`, regenerates `meetups-source.html`, and updates the live directory data. Do not edit `meetups-source.html` manually.

## Main website files

- `index.html` — live homepage
- `styles.css` — site styling
- `script.js` — search, filters, meetup rendering and expected-date logic
- `UK-Bitcoin-Meetups-Directory.md` — editable meetup master list
- `generate-meetups.py` — converts the Markdown master list into website data
- `meetups-source.html` — generated website data; do not edit manually
- `.github/workflows/dynamic-meetup-counter.yml` — automatic rebuild workflow
- `BitcoinEventsUK new logo trans.png` — site logo and favicon
- `CNAME` — custom domain configuration
