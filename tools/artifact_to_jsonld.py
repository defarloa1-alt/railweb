#!/usr/bin/env python3
"""Convert an intake artifact (Markdown with YAML front-matter) to JSON-LD.

Usage: tools/artifact_to_jsonld.py path/to/artifact.md > artifact.jsonld
"""
import sys
import json
from pathlib import Path
import yaml

CONTEXT_PATH = Path(__file__).resolve().parents[1] / 'intake' / 'context.jsonld'


def load_front_matter(path: Path):
    text = path.read_text(encoding='utf8')
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return fm, body
    # fallback: try parse whole as yaml
    try:
        obj = yaml.safe_load(text)
        return obj, ''
    except Exception:
        raise ValueError('No YAML front-matter found')


def to_jsonld(fm: dict, body: str):
    ctx = json.loads(CONTEXT_PATH.read_text(encoding='utf8'))
    node = {
        "@context": ctx['@context'],
        "@id": fm.get('id') or f"urn:railweb:{fm.get('type','artifact')}:{fm.get('title','').lower().replace(' ','-')}",
        "@type": f"rw:{fm.get('type','Artifact').capitalize()}",
        "title": fm.get('title'),
        "description": fm.get('description') or body,
        "tags": fm.get('tags', []),
        "provenance": fm.get('provenance', {})
    }
    return node


def main():
    if len(sys.argv) < 2:
        print('Usage: artifact_to_jsonld.py path/to/artifact.md', file=sys.stderr)
        sys.exit(2)
    p = Path(sys.argv[1])
    fm, body = load_front_matter(p)
    node = to_jsonld(fm, body)
    print(json.dumps(node, indent=2))


if __name__ == '__main__':
    main()
