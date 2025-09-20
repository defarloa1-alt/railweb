"""Simple KerML parser for the Railweb intake KerML export.

This is intentionally small and tolerant: it extracts requirement blocks and a basic trace table
(req_id, short_title, source_artifact). It is not a full KerML parser but is good enough for
hand-off and downstream tooling for the current repo.

Usage:
    python tools\parse_kerml.py <kerml_file> --out-dir <out_dir>

Outputs:
    - <out_dir>/requirements_<sha>.json  # list of requirement objects
    - <out_dir>/requirements_<sha>_trace.csv  # CSV mapping req_id -> source

"""
import re
import json
import csv
import sys
from pathlib import Path

REQ_BLOCK_RE = re.compile(r'requirement\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_\-]+)\s+id\s*=\s*"([^"]+)"\s*\{([^}]*)\}', re.DOTALL)
FIELD_RE = re.compile(r'([a-zA-Z_]+)\s*=\s*"([^"]*)";')


def parse_requirements(text):
    results = []
    for m in REQ_BLOCK_RE.finditer(text):
        kind = m.group(1)
        key = m.group(2)
        req_id = m.group(3)
        body = m.group(4)
        fields = dict(FIELD_RE.findall(body))
        # derive a short title from text or the id
        short = fields.get('text', '').strip()
        if len(short) > 120:
            short = short[:117] + '...'
        entry = {
            'id': req_id,
            'kind': kind,
            'key': key,
            'text': fields.get('text','').strip(),
            'rationale': fields.get('rationale','').strip(),
            'verify': fields.get('verify','').strip(),
            'source': fields.get('source','').strip(),
            'type': fields.get('type','').strip(),
            'acceptance': fields.get('acceptance','').strip(),
            'measure': fields.get('measure','').strip(),
            'target': fields.get('target','').strip(),
        }
        results.append(entry)
    return results


def main():
    if len(sys.argv) < 2:
        print('Usage: parse_kerml.py <file.kerml> [--out-dir out]')
        sys.exit(2)
    path = Path(sys.argv[1])
    out_dir = Path('intake/exports')
    if '--out-dir' in sys.argv:
        out_dir = Path(sys.argv[sys.argv.index('--out-dir')+1])
    out_dir.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding='utf-8')
    reqs = parse_requirements(text)
    sha = path.stem.split('_')[-1]
    json_path = out_dir / f'requirements_{sha}.json'
    csv_path = out_dir / f'requirements_{sha}_trace.csv'
    json_path.write_text(json.dumps(reqs, indent=2, ensure_ascii=False), encoding='utf-8')
    with csv_path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['req_id','short_text','source'])
        for r in reqs:
            writer.writerow([r['id'], r['text'][:200], r['source']])
    print('Wrote', json_path, csv_path)


if __name__ == '__main__':
    main()
