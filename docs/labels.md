# Labeling and Issue Automation

This document describes the `copilot-eligible` label and how it fits into the Digital Doorway governance model.

## `copilot-eligible`

- Name: `copilot-eligible`
- Color: `#ffd966` (yellow/orange for visibility)
- Description: "Mark this issue as eligible to be assigned to GitHub Copilot coding agent (maintainers only)."

## Policy

- Only repository maintainers may add the `copilot-eligible` label. The label indicates that an issue has been triaged and is low-risk enough to assign to Copilot for an autonomous attempt.
- Add the label _before_ assigning the issue to Copilot.

## How to create the label (recommended)

Use the included helper (requires `gh` CLI and authentication):

```bash
./tools/labels/create_copilot_label.sh defarloa1-alt/railweb ffd966 "Mark this issue as eligible to be assigned to GitHub Copilot coding agent (maintainers only)."
```

Or create manually in the GitHub UI: Repository -> Issues -> Labels -> New label.
