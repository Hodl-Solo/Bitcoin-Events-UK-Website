#!/usr/bin/env python3
"""Generate meetups HTML from meetups-directory.md"""

import re
import os

def parse_meetups(filename):
    """Parse meetups from markdown file"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by region headers
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)[1:]
    
    meetups = []
    regions = {}
    
    for section in sections:
        lines = section.strip().split('\n')
        region = lines[0].strip()
        regions[region] = []
        
        # Find all meetup entries in this region
        entry = {}
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- name:'):
                if entry:
                    regions[region].append(entry)
                entry = {'region': region}
                entry['name'] = line.replace('- name:', '').strip().strip('"')
            elif line.startswith('schedule:') and entry:
                entry['schedule'] = line.replace('schedule:', '').strip().strip('"')
            elif line.startswith('status:') and entry:
                entry['status'] = line.replace('status:', '').strip()
        
        if entry:
            regions[region].append(entry)
    
    return regions

def generate_html(regions):
    """Generate HTML for meetups"""
    
    html_parts = []
    
    # Group by region
    region_order = ['London', 'South East', 'South West', 'Midlands', 'North West', 'North East', 'Scotland', 'Wales', 'Northern Ireland', 'Ireland']
    
    for region in region_order:
        if region in regions:
            meetups = regions[region]
            active_meetups = [m for m in meetups if m.get('status') == 'active']
            
            if active_meetups:
                html_parts.append(f'''
        <!-- {region} -->
        <div class="region-section">
            <div class="region-header">{region}</div>
            <ul class="meetup-list">''')
                
                for m in active_meetups:
                    status_class = 'status-active'
                    html_parts.append(f'''
                <li class="meetup-item">
                    <div class="meetup-name">{m['name']}<span class="status-tag {status_class}">Active</span></div>
                    <div class="meetup-schedule">{m.get('schedule', '')}</div>
                </li>''')
                
                html_parts.append('''
            </ul>
        </div>''')
    
    return '\n'.join(html_parts)

def main():
    regions = parse_meetups('meetups-directory.md')
    html = generate_html(regions)
    
    # Update index.html
    with open('index.html', 'r') as f:
        index = f.read()
    
    # Replace the directory-grid section
    pattern = r'<!--\s*DIRECTORY_START\s*-->.*?<!--\s*DIRECTORY_END\s*-->'
    
    new_section = f'''<!-- DIRECTORY_START -->
        <div class="directory-grid">
            {html}
        </div>
        <!-- DIRECTORY_END -->'''
    
    # If no markers exist, find and replace the directory-grid div
    if 'directory-grid' in index:
        index = re.sub(r'<div class="directory-grid">.*?</div>\s*</main>', 
                       f'<div class="directory-grid">\n{html}\n        </div>\n    </main>', 
                       index, flags=re.DOTALL)
    
    with open('index.html', 'w') as f:
        f.write(index)
    
    print("✓ Generated meetups HTML")

if __name__ == '__main__':
    main()
