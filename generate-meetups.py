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


def find_meetup_file() -> Path:
    for candidate in MEETUP_FILE_CANDIDATES:
        p = Path(candidate)
        if p.exists():
            return p
    raise FileNotFoundError('Could not locate UK-Bitcoin-Meetups-Directory.md')


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

            meetups.append({
                'name': name.strip(),
                'description': description,
                'status': status.strip().title(),
                'links': links,
                'plain_text': plain_text,
            })

        if meetups:
            regions[region] = meetups

    return regions


def build_source(regions):
    parts = ['<!DOCTYPE html>', '<html lang="en"><head><meta charset="UTF-8"><title>Bitcoin Events UK meetup data</title></head><body>']
    active_total = 0
    total = 0

    for region in REGION_ORDER:
        meetups = regions.get(region, [])
        if not meetups:
            continue

        parts.append(f'<div class="region-section"><div class="region-header">{html.escape(region)}</div><ul class="meetup-list">')
        for meetup in meetups:
            total += 1
            status = meetup['status']
            if status.lower() == 'active':
                active_total += 1
            status_class = 'status-active' if status.lower() == 'active' else 'status-paused'
            parts.append('<li class="meetup-item">')
            parts.append(f'<div class="meetup-name">{html.escape(meetup["name"])}<span class="status-tag {status_class}">{html.escape(status)}</span></div>')
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
