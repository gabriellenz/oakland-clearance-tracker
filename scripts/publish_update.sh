#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PUBLIC_REPO_DIR="$(pwd)"
SUPERPROJECT_DIR="$(git rev-parse --show-superproject-working-tree 2>/dev/null || true)"

python3 scripts/build_public_data.py
python3 -m json.tool data/oakland-2026.json >/dev/null

if command -v node >/dev/null 2>&1; then
  node --check app.js
  node --check updates.js
fi

if [[ -n "$SUPERPROJECT_DIR" ]]; then
  python3 "$SUPERPROJECT_DIR/Oakland/scripts/audit_public_data.py"
fi

public_data_changed=0
if git diff --quiet -- data/oakland-2026.json; then
  echo "No public data changes to publish."
else
  public_data_changed=1
  git add data/oakland-2026.json
  git commit -m "Update Oakland tracker public data"
  git push
fi

if [[ -n "$SUPERPROJECT_DIR" ]]; then
  cd "$SUPERPROJECT_DIR"
  git add -A Oakland data_dictionary.md README.md .gitignore .gitmodules public/oakland-clearance-tracker

  if git diff --cached --quiet; then
    echo "No private tracker or submodule pointer changes to back up."
  else
    if [[ "$public_data_changed" -eq 1 ]]; then
      git commit -m "Back up Oakland tracker update and public pointer"
    else
      git commit -m "Back up Oakland tracker update"
    fi
    git push backup main
  fi
fi
