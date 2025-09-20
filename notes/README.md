Obsidian + railweb notes policy

Purpose

This document explains how to use an Obsidian vault with the railweb repository.

Policy

1. The Obsidian vault may live locally in the repository folder for convenience, but workspace and plugin state must remain local-only and excluded from source control.
   - The repository already ignores `.obsidian/` via `.gitignore`.
2. Only Markdown notes that are intended to be shared, reviewed, and versioned should be placed under `notes/` or `docs/`.
   - Use `notes/` for personal drafts and `docs/` for canonical, team-facing documents.
3. Do not store API keys, credentials, or other secrets in notes or plugin configs.
4. When preparing content for PRs, move canonical notes to `docs/` and open a PR for review.

How to make the vault local-only

- If `.obsidian/` appears as a tracked deletion in git, run the following from the repo root to restore a local copy and stop tracking it:

```powershell
# restore local copy from HEAD
git restore .obsidian
# untrack .obsidian so it remains local-only
git rm -r --cached .obsidian
git commit -m "chore: stop tracking .obsidian workspace files (local-only vault)"
```

If you prefer to keep a shared Obsidian configuration, create a minimal `docs/obsidian-config.md` describing required plugins and templates and keep it under source control.
