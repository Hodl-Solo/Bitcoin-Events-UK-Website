#!/usr/bin/env python3
"""Generate meetups HTML from UK-Bitcoin-Meetups-Directory.md"""

import re
import os
import sys

def parse_markdown_tables(filename):
    """Parse meetups from markdown file with tables"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by region headers (## London, ## South, etc.)
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)[1:]
    
    regions_data = {}
    
    for section in sections:
        lines = section.strip().split('\n')
        region = lines[0].strip()
        
        # Find the table
        table_start = -1
        for i, line in enumerate(lines):
            if line.startswith('|'):
                table_start = i
                break
        
        if table_start == -1:
            continue
        
        # Parse table rows
        meetups = []
        for line in lines[table_start:]:
            if not line.startswith('|') or '---' in line:
                continue
            
            # Split by | and clean up
            cols = [c.strip() for c in line.split('|')[1:-1]]
            
            if len(cols) >= 4 and cols[0] and cols[0] != 'Name':
                name = cols[0]
                schedule = cols[1] if len(cols) > 1 else ''
                venue = cols[2] if len(cols) > 2 else ''
                status = cols[3].lower() if len(cols) > 3 else 'active'
                links = cols[4] if len(cols) > 4 else ''
                
                # Skip removed/deleted
                if status in ['remove', 'deleted']:
                    continue
                
                meetups.append({
                    'name': name,
                    'schedule': f"{schedule} · {venue}" if schedule and venue else schedule or venue,
                    'status': status,
                    'links': links
                })
        
        regions_data[region] = meetups
    
    return regions_data

def generate_html(regions_data):
    """Generate HTML for meetups"""
    
    # Define region order
    region_order = ['London', 'South', 'Midlands', 'North', 'Scotland', 'Wales', 'Northern Ireland', 'Ireland']
    
    html_parts = []
    
    for region in region_order:
        if region in regions_data:
            meetups = regions_data[region]
            
            if meetups:
                html_parts.append(f'''
        <!-- {region} -->
        <div class="region-section">
            <div class="region-header">{region}</div>
            <ul class="meetup-list">''')
                
                for m in meetups:
                    status_class = 'status-active' if m['status'] == 'active' else 'status-paused'
                    status_text = 'Active' if m['status'] == 'active' else 'Paused'
                    
                    html_parts.append(f'''
                <li class="meetup-item">
                    <div class="meetup-name">{m['name']}<span class="status-tag {status_class}">{status_text}</span></div>
                    <div class="meetup-schedule">{m['schedule']}</div>
                </li>''')
                
                html_parts.append('''
            </ul>
        </div>''')
    
    return '\n'.join(html_parts)

def main():
    # Try to find the meetups directory file
    possible_paths = [
        '../bill-mission-control/UK-Bitcoin-Meetups-Directory.md',
        '../UK-Bitcoin-Meetups-Directory.md',
        'UK-Bitcoin-Meetups-Directory.md',
    ]
    
    meetups_file = None
    for path in possible_paths:
        if os.path.exists(path):
            meetups_file = path
            break
    
    if not meetups_file:
        print("ERROR: Could not find UK-Bitcoin-Meetups-Directory.md")
        sys.exit(1)
    
    print(f"Reading from: {meetups_file}")
    
    regions_data = parse_markdown_tables(meetups_file)
    html = generate_html(regions_data)
    
    # Update index.html
    with open('index.html', 'r') as f:
        index = f.read()
    
    # Find and replace the directory-grid section
    if '<div class="directory-grid">' in index:
        index = re.sub(
            r'<div class="directory-grid">.*?</div>\s*</main>',
            f'<div class="directory-grid">\n{html}\n        </div>\n    </main>',
            index,
            flags=re.DOTALL
        )
    
    with open('index.html', 'w') as f:
        f.write(index)
    
    total = sum(len(meetups) for meetups in regions_data.values())
    print(f"✓ Generated HTML for {total} meetups across {len(regions_data)} regions")

if __name__ == '__main__':
    main()
