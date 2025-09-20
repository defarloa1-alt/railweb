#!/usr/bin/env python3
"""Pull a Notion database, render to Markdown table, and inject into README.md.

Supports --dry-run to use sample JSON at .github/scripts/sample_notion_response.json
Configurable mapping via COLUMN_MAP constant. Handles pagination.
"""
import os
import sys
import json
import re
import argparse
from typing import List
import requests

NOTION_VERSION = os.environ.get('NOTION_VERSION', '2022-06-28')

# Customize which Notion properties map to which columns in the output table.
# Format: (Column header, property_name, property_type)
# property_type: title, rich_text, status, select, multi_select, people, number, url, checkbox
COLUMN_MAP = [
    {"header": "Name", "prop": "Task Name", "type": "title"},
    {"header": "Status", "prop": "Status", "type": "select", "render": {"style": "badge"}},
    {"header": "Notes", "prop": "Notes", "type": "rich_text"},
    {"header": "Link", "prop": "GitHub PR URL", "type": "url", "render": {"label_from": "Task Name"}},
    {"header": "Last Updated", "prop": "__page_last_edited_time__", "type": "last_edited_time", "format": "%Y-%m-%d"},
]

# Default query payload scoped to the V2.1 view (page_size, filter and sorts)
DEFAULT_QUERY_PAYLOAD = {
    "page_size": 100,
    "filter": {
        "property": "Milestone",
        "select": {"equals": "V2.1"}
    },
    "sorts": [
        {"property": "Priority", "direction": "descending"},
        {"property": "Story Points", "direction": "descending"}
    ]
}

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), 'sample_notion_response.json')

README_PATH = os.path.join(os.getcwd(), 'README.md')
START_MARK = '<!--TABLE:START-->'
END_MARK = '<!--TABLE:END-->'


def query_db(db_id, token, dry_run=False):
    if dry_run:
        with open(SAMPLE_PATH, 'r', encoding='utf8') as f:
            return json.load(f)['results']

    headers = {
        'Authorization': f'Bearer {token}',
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json',
    }
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    results = []
    payload = {}
    while True:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            # provide helpful debug information without printing secrets
            print(f'Notion query POST {url} returned status {r.status_code}', file=sys.stderr)
            try:
                # print short response body to stderr for quick diagnosis
                print('Response body:', r.text, file=sys.stderr)
            except Exception:
                pass
            try:
                # also write full response to a debug file for later inspection
                dbg_path = os.path.join(os.getcwd(), 'notion_query_debug.json')
                with open(dbg_path, 'w', encoding='utf8') as dbg:
                    dbg.write(r.text)
                print(f'Wrote debug response to {dbg_path}', file=sys.stderr)
            except Exception:
                pass
            raise
        j = r.json()
        results.extend(j.get('results', []))
        if not j.get('has_more'):
            break
        payload['start_cursor'] = j.get('next_cursor')
    return results


def extract_cell(prop, prop_type):
    try:
        if not prop:
            return ''
        if prop_type == 'title':
            vals = prop.get('title', [])
            return ''.join(t.get('plain_text', '') for t in vals)
        if prop_type == 'rich_text':
            vals = prop.get('rich_text', [])
            return ''.join(t.get('plain_text', '') for t in vals)
        # handle both status and select types by checking both keys
        if prop_type in ('status', 'select'):
            s = prop.get('status') or prop.get('select')
            return s.get('name') if s else ''
        if prop_type == 'multi_select':
            ms = prop.get('multi_select', [])
            return ', '.join(m.get('name','') for m in ms)
        if prop_type == 'number':
            return str(prop.get('number',''))
        if prop_type == 'url':
            return prop.get('url','')
        if prop_type == 'checkbox':
            return '✅' if prop.get('checkbox') else ''
    except Exception:
        return ''
    return ''


def to_rows(notion_pages, column_map=COLUMN_MAP):
    """Return list of rendered row strings for the table.

    We first extract raw values per property, then apply per-column render rules
    (e.g., render Link as [Name](url), status badges, date formatting).
    """
    rows = []
    for p in notion_pages:
        props = p.get('properties', {})
        # collect raw values
        raw = {}
        for col in column_map:
            prop_name = col.get('prop')
            prop_type = col.get('type')
            if prop_type == 'last_edited_time':
                # special: last_edited_time at page level
                raw[prop_name] = p.get('last_edited_time') or ''
            else:
                prop = props.get(prop_name, {})
                raw[prop_name] = extract_cell(prop, prop_type)

        # render with fallbacks
        row = []
        for col in column_map:
            header = col.get('header')
            prop_name = col.get('prop')
            prop_type = col.get('type')
            render = col.get('render', {}) or {}
            val = raw.get(prop_name, '') or ''

            # Last edited formatting
            if prop_type == 'last_edited_time':
                if val:
                    try:
                        from datetime import datetime

                        # strip Z for fromisoformat compatibility
                        v = val.rstrip('Z')
                        dt = datetime.fromisoformat(v)
                        fmt = col.get('format', '%Y-%m-%d')
                        val = dt.strftime(fmt)
                    except Exception:
                        val = val
                else:
                    val = ''

            # Link rendering: use label_from if present
            if prop_type == 'url' and val:
                label_from = render.get('label_from')
                if label_from:
                    label = raw.get(label_from, '')
                    if label:
                        val = f'[{label}]({val})'
                    else:
                        val = val

            # Status badge rendering
            if prop_type == 'status' and val:
                # try to get color from properties if available
                try:
                    # prop object isn't available here; attempt to fetch color via original properties
                    prop_obj = props.get(prop_name, {})
                    status_obj = prop_obj.get('status') if isinstance(prop_obj, dict) else None
                    color = status_obj.get('color') if status_obj else None
                except Exception:
                    color = None
                val = render_status_badge(val, color) if render.get('style') == 'badge' else val

            # Multi-selects are already joined by extract_cell

            # Empty value fallback
            if not val:
                val = '—'

            row.append(val)
        rows.append(row)
    return rows


def render_status_badge(name: str, color: str | None) -> str:
    """Render a status badge using color emoji mapping or fallback text."""
    color_map = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴',
        'blue': '🔵',
        'purple': '🟣',
        'pink': '💗',
        'gray': '⚪',
        'orange': '🟠',
        'brown': '🟤',
    }
    emoji = color_map.get(color, '') if color else ''
    if emoji:
        return f"{emoji} {name}"
    return name


def md_table(rows, header=None):
    # Derive header names if not explicitly provided. COLUMN_MAP may use dict entries
    # with a 'header' key (the legacy code assumed sequence entries).
    if header is None:
        header = []
        for c in COLUMN_MAP:
            if isinstance(c, dict):
                header.append(str(c.get('header', '')))
            elif isinstance(c, (list, tuple)) and len(c) > 0:
                header.append(str(c[0]))
            else:
                header.append('')

    cols = len(header)
    widths = [len(h) for h in header]
    for r in rows:
        # normalize row length
        if len(r) < cols:
            r = r + [''] * (cols - len(r))
        for i in range(cols):
            widths[i] = max(widths[i], len(str(r[i])))

    def fmt(row):
        return '| ' + ' | '.join(str(row[i]).ljust(widths[i]) for i in range(cols)) + ' |'

    sep = '| ' + ' | '.join('-' * w for w in widths) + ' |'
    return '\n'.join([fmt(header), sep] + [fmt(r) for r in rows])


def inject_readme(md, path=README_PATH, start=START_MARK, end=END_MARK):
    if not os.path.exists(path):
        print(f'No README.md at {path} - aborting')
        sys.exit(1)
    with open(path, 'r', encoding='utf8') as f:
        readme = f.read()
    pattern = re.compile(re.escape(start) + '.*?' + re.escape(end), flags=re.S)
    new_block = f"{start}\n\n{md}\n\n{end}"
    if pattern.search(readme):
        readme = pattern.sub(new_block, readme)
    else:
        # insert after first H1 or at top
        # find first blank line after intro
        parts = readme.splitlines()
        insert_at = 0
        for i, line in enumerate(parts):
            if line.strip() == '':
                insert_at = i+1
                break
        parts.insert(insert_at, new_block)
        readme = '\n'.join(parts)
    with open(path, 'w', encoding='utf8') as f:
        f.write(readme)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', help='use sample JSON instead of calling Notion')
    p.add_argument('--db', default=os.environ.get('NOTION_DATABASE_ID'))
    p.add_argument('--token', default=os.environ.get('NOTION_TOKEN'))
    p.add_argument('--out', default=README_PATH)
    args = p.parse_args()

    if args.dry_run:
        print('Running in dry-run mode')
    if not args.db and not args.dry_run:
        print('NOTION_DATABASE_ID must be set via env or --db')
        sys.exit(1)

    pages = query_db(args.db, args.token, dry_run=args.dry_run)
    rows = to_rows(pages)
    table_md = md_table(rows)
    inject_readme(table_md, path=args.out)
    print('README updated')


if __name__ == '__main__':
    main()
