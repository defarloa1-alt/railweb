#!/usr/bin/env python3
"""yaml_to_md.py

Simple utility to convert a YAML file to readable Markdown for fast review.
Usage: python tools/yaml_to_md.py path/to/file.yaml
Outputs Markdown to stdout.
"""
import sys
from pathlib import Path
import yaml


def to_md(obj, indent=0):
    """Recursively render YAML Python objects to Markdown."""
    md_lines = []
    prefix = '  ' * indent
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, (dict, list)):
                md_lines.append(f"{prefix}- **{key}**:\n")
                md_lines.extend(to_md(val, indent + 1))
            else:
                md_lines.append(f"{prefix}- **{key}**: `{val}`\n")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                md_lines.append(f"{prefix}-\n")
                md_lines.extend(to_md(item, indent + 1))
            else:
                md_lines.append(f"{prefix}- `{item}`\n")
    else:
        md_lines.append(f"{prefix}- `{obj}`\n")
    return md_lines


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/yaml_to_md.py path/to/file.yaml", file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    try:
        with path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading YAML: {e}", file=sys.stderr)
        sys.exit(2)

    md = to_md(data)
    print('\n'.join(md))


if __name__ == '__main__':
    main()
