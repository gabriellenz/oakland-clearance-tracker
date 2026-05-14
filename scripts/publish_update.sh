#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/build_public_data.py

if git diff --quiet -- data/oakland-2026.json; then
  echo "No public data changes to publish."
  exit 0
fi

git add data/oakland-2026.json
git commit -m "Update Oakland tracker public data"
git push
