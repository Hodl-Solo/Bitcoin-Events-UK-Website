#!/usr/bin/env python3
"""Generate Bitcoin Events UK directory HTML from Obsidian master list."""

import re
import sys
from pathlib import Path

REGION_ORDER = [
    'London', 'South', 'Midlands', 'North',
    'Scotland', 'Wales', 'Northern Ireland', 'Ireland'
]

MEETUP_FILE_CANDIDATES = [
    'UK-Bitcoin-Meetups-Directory.md',
    '../bill-mission-control/UK-Bitcoin-Meetups-Directory.md',
    '../UK-Bitcoin-Meetups-Directory.md',
]


def find_meetup_file() -> Path:
    for candidate in MEETUP_FILE_CANDIDATES:
        p = Path(candidate)
        if p.exists():
            return p
    raise FileNotFoundError('Could not locate UK-Bitcoin-Meetups-Directory.md')


def parse_table_markdown(text: str):
    sections = re.split(r'^##\s+', text, flags=re.MULTILINE)[1:]
    regions: dict[str, list[dict]] = {}

    for section in sections:
        lines = section.strip().split('\n')
        region = lines[0].strip()
        table_rows = [line for line in lines if line.startswith('|') and '---' not in line]

        meetups = []
        for row in table_rows:
            cols = [col.strip() for col in row.split('|')[1:-1]]
            if len(cols) < 4 or cols[0] in ('Name', ''):
                continue

            name, schedule, venue, status = cols[:4]
            links_cell = cols[4] if len(cols) > 4 else ''
            status_value = status.strip().lower()

            if status_value != 'active':
                continue

            description = schedule.strip()
            venue = venue.strip()
            if venue and venue not in description:
                description = f"{description} · {venue}" if description else venue

            link_matches = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', links_cell)
            links = [{'label': label, 'url': url} for label, url in link_matches]

            meetups.append({
                'name': name.strip(),
                'description': description,
                'links': links,
            })

        regions[region] = meetups

    return regions


def build_directory_html(regions: dict[str, list[dict]]):
    html_parts = []
    active_total = 0

    for region in REGION_ORDER:
        meetups = regions.get(region, [])
        if not meetups:
            continue

        active_total += len(meetups)
        html_parts.append(f'''
        <!-- {region} -->
        <div class="region-section">
            <div class="region-header">{region}</div>
            <ul class="meetup-list">''')

        for meetup in meetups:
            links_html = ''
            if meetup['links']:
                chips = ''.join(
                    f"<a href=\"{link['url']}\" target=\"_blank\" rel=\"noopener\" class=\"link-chip\">{link['label']}</a>"
                    for link in meetup['links']
                )
                links_html = f"\n                    <div class=\"meetup-links\">{chips}</div>"

            html_parts.append(f'''
                <li class="meetup-item">
                    <div class="meetup-name">{meetup['name']}<span class="status-tag status-active">Active</span></div>
                    <div class="meetup-schedule">{meetup['description']}</div>{links_html}
                </li>''')

        html_parts.append('''
            </ul>
        </div>''')

    return '\n'.join(html_parts), active_total


def update_index_html(generated_html: str, active_total: int):
    index_path = Path('index.html')
    index_html = index_path.read_text()

    index_html = re.sub(
        r'<div class="directory-grid">.*?</div>\s*</main>',
        f'<div class="directory-grid">\n{generated_html}\n        </div>\n    </main>',
        index_html,
        flags=re.DOTALL
    )

    index_html = re.sub(
        r'<div class="stats-number">\d+</div>',
        f'<div class="stats-number">{active_total}</div>',
        index_html,
        count=1
    )

    index_path.write_text(index_html)


def main():
    try:
        meetup_file = find_meetup_file()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print(f"Reading from: {meetup_file}")
    regions = parse_table_markdown(meetup_file.read_text())
    directory_html, active_total = build_directory_html(regions)
    update_index_html(directory_html, active_total)

    print(f"✓ Generated HTML for {active_total} active meetups")


if __name__ == '__main__':
    main()
