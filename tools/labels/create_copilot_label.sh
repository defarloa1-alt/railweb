#!/usr/bin/env bash
set -euo pipefail

# create_copilot_label.sh
# Usage: ./create_copilot_label.sh [repo] [color] [description]
# Example: ./create_copilot_label.sh defarloa1-alt/railweb ffd966 "Mark this issue as eligible to be assigned to GitHub Copilot coding agent (maintainers only)."

REPO="${1:-defarloa1-alt/railweb}"
LABEL_NAME="copilot-eligible"
COLOR="${2:-ffd966}"
DESC="${3:-Mark this issue as eligible to be assigned to GitHub Copilot coding agent (maintainers only).}"

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh (GitHub CLI) is required. Install from https://cli.github.com/" >&2
  exit 2
fi

echo "Creating or updating label '$LABEL_NAME' on repository $REPO"
if gh label create "$LABEL_NAME" --repo "$REPO" --color "$COLOR" --description "$DESC" >/dev/null 2>&1; then
  echo "Label created: $LABEL_NAME"
else
  echo "Label may already exist, attempting to update..."
  gh label edit "$LABEL_NAME" --repo "$REPO" --color "$COLOR" --description "$DESC"
  echo "Label updated: $LABEL_NAME"
fi

echo "Done."
#!/usr/bin/env bash
set -euo pipefail

# create_copilot_label.sh
# Usage: ./create_copilot_label.sh [repo] [color] [description]
# Example: ./create_copilot_label.sh defarloa1-alt/railweb ffd966 "Mark this issue as eligible to be assigned to GitHub Copilot coding agent (maintainers only)."

REPO="${1:-defarloa1-alt/railweb}"
LABEL_NAME="copilot-eligible"
COLOR="${2:-ffd966}"
DESC="${3:-Mark this issue as eligible to be assigned to GitHub Copilot coding agent (maintainers only).}"

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh (GitHub CLI) is required. Install from https://cli.github.com/" >&2
  exit 2
fi

echo "Creating or updating label '$LABEL_NAME' on repository $REPO"
if gh label create "$LABEL_NAME" --repo "$REPO" --color "$COLOR" --description "$DESC" >/dev/null 2>&1; then
  echo "Label created: $LABEL_NAME"
else
  echo "Label may already exist, attempting to update..."
  gh label edit "$LABEL_NAME" --repo "$REPO" --color "$COLOR" --description "$DESC"
  echo "Label updated: $LABEL_NAME"
fi

echo "Done."
