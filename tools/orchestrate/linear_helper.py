"""Helper to create a Linear issue payload for a run.

Usage:
  python tools/orchestrate/linear_helper.py --run <run_id>

Outputs a JSON payload ready to POST to Linear's API (https://api.linear.app/graphql) or to be used with the web UI.
"""
import argparse
import json


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', required=True)
    p.add_argument('--assignee', default='')
    p.add_argument('--team', default='')
    args = p.parse_args()

    title = f"Create run {args.run}"
    description = f"Run ID: {args.run}\n\nUse the create_run API to reproduce and verify results."

    payload = {
        'title': title,
        'description': description,
        'assignee': args.assignee,
        'team': args.team,
    }
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
