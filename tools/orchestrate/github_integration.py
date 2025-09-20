import os
import json
import requests
from typing import Optional


def create_github_issue_for_run(run_id: str, meta: dict, repo: str = None, token: str = None) -> Optional[str]:
    """Create a GitHub issue for the run and return a string id like 'GH#123' or None.

    Uses GITHUB_TOKEN and GITHUB_REPOSITORY from env if values are not passed.
    meta may include 'assignee' (github username) and 'labels' (list of labels).
    """
    token = token or os.environ.get('GITHUB_TOKEN')
    if not token:
        return None

    repo = repo or os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        # default to repository owner set in repo metadata if missing
        repo = 'defarloa1-alt/railweb'

    title = f"Review run {run_id}"
    body_lines = [f"Run ID: {run_id}"]
    if isinstance(meta, dict):
        prov = meta.get('provenance')
        if prov and isinstance(prov, dict):
            src = prov.get('source', {})
            body_lines.append(f"Source: {src.get('id')} - {src.get('title')}")

    body = "\n".join(body_lines)

    payload = {'title': title, 'body': body}
    if isinstance(meta, dict):
        assignee = meta.get('assignee')
        labels = meta.get('labels')
        if assignee:
            payload['assignee'] = assignee
        if labels:
            payload['labels'] = list(labels) if isinstance(labels, (list, tuple)) else [str(labels)]

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'railweb-script'
    }

    url = f'https://api.github.com/repos/{repo}/issues'
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        r.raise_for_status()
        j = r.json()
        # return a short identifier
        num = j.get('number')
        if num:
            return f'GH#{num}'
    except Exception:
        return None
    return None
