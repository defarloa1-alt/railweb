import os
import requests
import json
from typing import Optional

LINEAR_API_URL = 'https://api.linear.app/graphql'


def create_issue_for_run(run_id: str, meta: dict) -> Optional[str]:
    """Create a Linear issue for the given run and return the issue id or None.

    Requires environment variables:
      LINEAR_API_KEY - the Linear API key (server-side)
      LINEAR_TEAM_ID - optional team id to assign the issue to
    If missing, the function returns None.
    """
    api_key = os.environ.get('LINEAR_API_KEY')
    if not api_key:
        # fallback: attempt to create a GitHub issue if available
        try:
            from .github_integration import create_github_issue_for_run
            gh = create_github_issue_for_run(run_id, meta)
            return gh
        except Exception:
            return None

    team_id = os.environ.get('LINEAR_TEAM_ID')

    title = f"Review run {run_id}"
    body_lines = [f"Run ID: {run_id}"]
    if isinstance(meta, dict):
        # include provenance summary if present
        prov = meta.get('provenance')
        if prov and isinstance(prov, dict):
            src = prov.get('source', {})
            body_lines.append(f"Source: {src.get('id')} - {src.get('title')}")
            body_lines.append(f"Confidence: {prov.get('confidence')}")

    body = "\n".join(body_lines)

    mutation = '''mutation IssueCreate($input: IssueCreateInput!) { issueCreate(input: $input) { success, issue { id } } }'''
    variables = {
        'input': {
            'title': title,
            'description': body,
        }
    }
    # allow optional assignee and labels to be provided via meta
    if isinstance(meta, dict):
        assignee = meta.get('assignee')
        labels = meta.get('labels')
        if assignee:
            variables['input']['assigneeId'] = assignee
        if labels:
            # Linear GraphQL accepts labelIds as a list of strings
            variables['input']['labelIds'] = list(labels) if isinstance(labels, (list, tuple)) else [str(labels)]
    if team_id:
        variables['input']['teamId'] = team_id

    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json',
    }

    payload = {'query': mutation, 'variables': variables}

    try:
        resp = requests.post(LINEAR_API_URL, headers=headers, data=json.dumps(payload), timeout=10)
        resp.raise_for_status()
        j = resp.json()
        issue = j.get('data', {}).get('issueCreate', {}).get('issue')
        if issue:
            return issue.get('id')
    except Exception:
        # don't crash the runner for integration failures
        return None
    return None
