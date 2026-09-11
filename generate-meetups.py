#!/usr/bin/env python3
"""Generate the Bitcoin Events UK meetup data source from the Markdown master list."""

import html
import re
import sys
from pathlib import Path

REGION_ORDER = [
    'London', 'South', 'Midlands', 'North', 'Scotland', 'Wales',
    'Northern Ireland', 'Ireland', 'Special Events',
]

MEETUP_FILE_CANDIDATES = [
    'UK-Bitcoin-Meetups-Directory.md',
    '../bill-mission-control/UK-Bitcoin-Meetups-Directory.md',
    '../UK-Bitcoin-Meetups-Directory.md',
]

OUTPUT_PATH = Path('meetups-source.html')

LOGO_BY_NAME = {
    'Battersea Bitcoiners': 'assets/meetup-logos/battersea-bitcoiners.webp',
    'Berkshire Bitcoiners': 'assets/meetup-logos/berkshire-bitcoiners.jpg',
    'Bitcoin Beach Bournemouth': 'assets/meetup-logos/bitcoin-beach-bournemouth.webp',
    'Chilterns Bitcoin Hub': 'assets/meetup-logos/chilterns-bitcoin-hub.webp',
    'City & Financial Bitcoiners': 'assets/meetup-logos/city-financial-bitcoiners.webp',
    'Cyphermunk House': 'assets/meetup-logos/cyphermunk-house.webp',
    'Leamington Spa Bitcoin': 'assets/meetup-logos/leamington-spa-bitcoin.jpg',
    'Northamptonshire Bitcoin Network': 'assets/meetup-logos/northamptonshire-bitcoin-network.webp',
    'Bitcoin Surrey': 'assets/meetup-logos/surrey-bitcoin.jpg',
    'Sutton Coldfield Bitcoin': 'assets/meetup-logos/sutton-coldfield-bitcoin.webp',
    'Sheffield Bitcoin': 'assets/meetup-logos/sheffield-bitcoin.webp',
    'Bitcoin Wales': 'assets/meetup-logos/wales-bitcoin.webp',
    'Bitcoin Power - Ayrshire': 'assets/meetup-logos/bitcoin-power-ayrshire.webp',
    'Bitcoin Derby': 'assets/meetup-logos/bitcoin-derby.webp',
    'Dundee Bitcoin': 'assets/meetup-logos/dundee-bitcoin.webp',
    'Glasgow Bitcoin': 'assets/meetup-logos/glasgow-bitcoin.webp',
    'Kent Bitcoin': 'assets/meetup-logos/kent-bitcoin.webp',
    'Lake District BTC': 'assets/meetup-logos/lake-district-btc.webp',
    'Limerick Bitcoin': 'assets/meetup-logos/limerick-bitcoin.webp',
    'Liverpool Bitcoin': 'assets/meetup-logos/liverpool-bitcoin.webp',
    'Newcastle Bitcoin Coffee': 'assets/meetup-logos/newcastle-bitcoin-coffee.webp',
    'Preston Bitcoin': 'assets/meetup-logos/preston-bitcoin.webp',
    'Real Bedford FC': 'assets/meetup-logos/real-bedford-fc.webp',
    'Women of Bitcoin UK': 'assets/meetup-logos/women-of-bitcoin-uk.webp',
    'Brighton Bitcoin': 'assets/meetup-logos/brighton-bitcoin.jpg',
    'Bitcoin Essex': 'assets/meetup-logos/essex-bitcoin.png',
    'Lincolnshire Bitcoin': 'assets/meetup-logos/lincolnshire-bitcoin.jpg',
    'Bitcoin Nottingham': 'assets/meetup-logos/nottingham-bitcoin.jpg',
    'Wiltshire Bitcoin': 'assets/meetup-logos/wiltshire-bitcoin.jpg',
    'Leeds Bitcoin Network': 'assets/meetup-logos/leeds-bitcoin.jpg',
    'North West Bitcoin Hub': 'assets/meetup-logos/north-west-ireland-bitcoin.jpg',
    'Belfast Bitcoin Meetup': 'assets/meetup-logos/northern-ireland-bitcoin.jpg',
    'Bitcoin Walk London': 'assets/meetup-logos/bitcoinwalk.png',
    'Bitcoin Walk Edinburgh': 'assets/meetup-logos/bitcoinwalk.png',
    '2140Art': 'assets/meetup-logos/2140art.png',
    '2140.wtf': 'assets/meetup-logos/2140wtf.png',
    'Aberdeen Bitcoin': 'assets/meetup-logos/aberdeen-bitcoin.jpg',
    'Bitcoin Edinburgh': 'assets/meetup-logos/bitcoin-edinburgh.jpg',
    'Bitcoinology': 'assets/meetup-logos/bitcoinology.jpg',
    'Bitcoin Bristol Beer Social': 'assets/meetup-logos/bristol-bitcoin.png',
    'Brum Bitcoin & Beer': 'assets/meetup-logos/brum-bitcoin-beer.jpg',
    'BTC Gloucestershire': 'assets/meetup-logos/btc-gloucestershire.jpg',
    'Cambridge Bitcoin': 'assets/meetup-logos/cambridge-bitcoin.jpg',
    'Cambs Bitcoin': 'assets/meetup-logos/cambs-bitcoin.jpg',
    'Faith and Bitcoin': 'assets/meetup-logos/faith-and-bitcoin.jpg',
    'Glasgow Bitcoin Group': 'assets/meetup-logos/glasgow-bitcoin-group.jpg',
    'Manchester Bitcoin': 'assets/meetup-logos/manchester-bitcoin.png',
    'Oxford Bitcoin (OxBit)': 'assets/meetup-logos/oxford-bitcoin.jpg',
    'Portsmouth Bitcoin': 'assets/meetup-logos/portsmouth-bitcoin.jpg',
    'Shropshire Bitcoiners': 'assets/meetup-logos/shropshire-bitcoiners.jpg',
    'Southampton Satoshi Society': 'assets/meetup-logos/southampton-satoshi.jpg',
    'Cardiff Bitcoin': 'assets/meetup-logos/cardiff-bitcoin.jpg',
}


def find_meetup_file() -> Path:
    for candidate in MEETUP_FILE_CANDIDATES:
        p = Path(candidate)
        if p.exists():
            return p
    raise FileNotFoundError('Could not locate UK-Bitcoin-Meetups-Directory.md')


def parse_map_coordinates(value: str):
    match = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$', value or '')
    if not match:
        return None, None
    lat, lon = match.groups()
    try:
        lat_num, lon_num = float(lat), float(lon)
    except ValueError:
        return None, None
    if not (-90 <= lat_num <= 90 and -180 <= lon_num <= 180):
        return None, None
    return lat, lon


def parse_table_markdown(text: str):
    sections = re.split(r'^##\s+', text, flags=re.MULTILINE)[1:]
    regions = {}

    for section in sections:
        lines = section.strip().split('\n')
        region = lines[0].strip()
        if region not in REGION_ORDER:
            continue

        meetups = []
        for row in lines[1:]:
            if not row.startswith('|') or re.match(r'^\|\s*-+', row):
                continue

            cols = [col.strip() for col in row.split('|')[1:-1]]
            if len(cols) < 4 or cols[0].lower() == 'name':
                continue

            name, schedule, venue, status = cols[:4]
            links_cell = cols[4] if len(cols) > 4 else ''
            map_cell = cols[5] if len(cols) > 5 else ''
            logo_cell = cols[6] if len(cols) > 6 else ''
            status_value = status.strip().lower()

            if status_value in {'delete', 'remove'}:
                continue
            if status_value not in {'active', 'paused'}:
                status = 'Active'

            description = schedule.strip()
            venue = venue.strip()
            if venue and venue != '-' and venue not in description:
                description = f'{description} · {venue}' if description and description != '-' else venue

            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', links_cell)
            plain_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', '', links_cell).strip(' ·')
            lat, lon = parse_map_coordinates(map_cell)
            meetup_name = name.strip()
            logo = logo_cell.strip() or LOGO_BY_NAME.get(meetup_name, '')

            meetups.append({
                'name': meetup_name,
                'description': description,
                'status': status.strip().title(),
                'links': links,
                'plain_text': plain_text,
                'lat': lat,
                'lon': lon,
                'logo': logo,
            })

        if meetups:
            regions[region] = meetups

    return regions


def build_source(regions):
    parts = [
        '<!DOCTYPE html>',
        '<html lang="en"><head><meta charset="UTF-8"><title>Bitcoin Events UK meetup data</title></head><body>'
    ]
    active_total = 0
    total = 0

    for region in REGION_ORDER:
        meetups = regions.get(region, [])
        if not meetups:
            continue

        parts.append(
            f'<div class="region-section"><div class="region-header">{html.escape(region)}</div><ul class="meetup-list">'
        )

        for meetup in meetups:
            total += 1
            status = meetup['status']
            if status.lower() == 'active':
                active_total += 1
            status_class = 'status-active' if status.lower() == 'active' else 'status-paused'
            attrs = []
            if meetup['lat'] is not None and meetup['lon'] is not None:
                attrs.append(f'data-lat="{html.escape(meetup["lat"], quote=True)}"')
                attrs.append(f'data-lon="{html.escape(meetup["lon"], quote=True)}"')
            if meetup['logo']:
                attrs.append(f'data-logo="{html.escape(meetup["logo"], quote=True)}"')
            attr_text = (' ' + ' '.join(attrs)) if attrs else ''

            parts.append(f'<li class="meetup-item"{attr_text}>')
            parts.append(
                f'<div class="meetup-name">{html.escape(meetup["name"])}'
                f'<span class="status-tag {status_class}">{html.escape(status)}</span></div>'
            )
            parts.append(f'<div class="meetup-schedule">{html.escape(meetup["description"])}</div>')

            if meetup['links'] or meetup['plain_text']:
                links_html = ''.join(
                    f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener" class="link-chip">{html.escape(label)}</a>'
                    for label, url in meetup['links']
                )
                links_html += html.escape(meetup['plain_text'])
                parts.append(f'<div class="meetup-links">{links_html}</div>')

            parts.append('</li>')

        parts.append('</ul></div>')

    parts.append('</body></html>')
    return '\n'.join(parts), active_total, total


def main():
    try:
        meetup_file = find_meetup_file()
    except FileNotFoundError as exc:
        print(f'ERROR: {exc}')
        sys.exit(1)

    regions = parse_table_markdown(meetup_file.read_text())
    source_html, active_total, total = build_source(regions)
    OUTPUT_PATH.write_text(source_html)
    print(f'✓ Generated {total} meetup listings ({active_total} active) in {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
