Notion setup — quick copy-paste instructions

2) Notion setup (quick)

Create an internal integration in Notion

1. Open https://www.notion.com/my-integrations and sign in.
2. Go to Settings & Members → Integrations → Develop your own integrations → New integration.
3. Name it “railweb-sync” (or your choice), add an icon if you want, keep the workspace as-is, then create.
4. Copy the Integration Secret. This is your NOTION_TOKEN. Store it securely.

Share the target database with the integration

1. Open the Notion page that contains the database you want to sync.
2. If the database is inline, open it as a full page: click the database title → Open as page.
3. Click Share (top right) → Invite → type the integration name (e.g., railweb-sync) → Add.
4. Verify it appears in the Share list with access.

Find the 32-character database ID

1. With the database open as a full page, look at the URL, for example:
   https://www.notion.so/yourworkspace/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx?v=…
2. Copy the 32-character hex ID (xxxxxxxx…); that’s your NOTION_DATABASE_ID.
3. If you see a 36-char UUID with dashes, remove the dashes to get 32 hex chars.

Permissions and API version notes

- If the integration isn’t invited to the database, queries will return 403.
- Treat the integration token as a secret. Add it in GitHub under Settings → Secrets and variables → Actions.
- The script defaults to Notion-Version: 2022-06-28. If you change this, update NOTION_VERSION in the script to match.

3) Test locally (dry-run, Windows Command Prompt)

Purpose: validate the script and README injection using the bundled sample_notion_response.json without hitting Notion.

Prereqs checklist

- Python 3.10+ installed and available in PATH
- README.md contains the markers:
  <!--TABLE:START-->
  <!--TABLE:END-->
- No secrets are needed for dry-run

Create and activate a virtual environment

```cmd
py -3 -m venv .venv
.venv\Scripts\activate
```

Install dependencies (if needed)

```cmd
python -m pip install --upgrade pip
pip install requests
```

Run the script in dry-run mode

If your script lives at `.github/scripts/notion_to_md.py`:

```cmd
python .github\scripts\notion_to_md.py --dry-run
```

If it’s at repo root (as `notion_to_md.py`):

```cmd
python notion_to_md.py --dry-run
```

Expected result

- The script loads `sample_notion_response.json`
- Renders a Markdown table using the default `COLUMN_MAP`
- Injects the table between `<!--TABLE:START-->` and `<!--TABLE:END-->` in `README.md`
- Prints “README updated” on success

Inspect and optionally commit

```cmd
git status
git diff README.md
```

If looks good:

```cmd
git add README.md
git commit -m "Dry-run: inject sample Notion table into README"
git push
```

Real Notion call locally (not dry-run)

Set env vars (replace values):

```cmd
set NOTION_TOKEN=secret_xxx
set NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
python .github\scripts\notion_to_md.py
```

This will call Notion with pagination and inject real data into README.md

Troubleshooting

- Empty table or “No pages returned”:
  - Ensure the integration is invited to the database via Share → Invite integration
  - Re-check the 32-char DB ID from the full-page database URL
- 401/403 errors:
  - Wrong token or integration not invited to that database
- Rate limiting:
  - For very large databases, add a short sleep per page in the pagination loop
- Wrong columns or blank cells:
  - Update `COLUMN_MAP` in `notion_to_md.py` to match exact property names and types, then re-run dry-run

Example mapping entries:

```python
# "Name": {"type": "title"}
# "Status": {"type": "status"}
# "Notes": {"type": "rich_text"}
# "Link": {"type": "url"}
```

Verification in GitHub Actions (first real run)

1) Add repo secrets in GitHub
   - `NOTION_TOKEN` = your integration secret
   - `NOTION_DATABASE_ID` = 32-char DB ID
2) Run the workflow
   - GitHub → Actions → “Update Notion table” → Run workflow
   - Or wait for the daily schedule at 06:00 UTC
3) Confirm results
   - Open the workflow run → check logs for the script step
   - If it committed, README.md will be updated and the commit author will be github-actions[bot]
   - If it failed, the logs will show the HTTP error and stack trace

If you send me your exact property names and desired column order, I can provide a ready-to-paste COLUMN_MAP and, if you want, enable:

- URL values as clickable markdown
- Status emojis or badges
- Multi-select values as comma-separated chips

