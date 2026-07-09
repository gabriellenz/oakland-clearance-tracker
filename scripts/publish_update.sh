#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PUBLIC_REPO_DIR="$(pwd)"
SUPERPROJECT_DIR="$(git rev-parse --show-superproject-working-tree 2>/dev/null || true)"
PAGES_WORKFLOW=".github/workflows/pages.yml"

check_github_pages_deploy() {
  local head_sha="$1"
  local discovery_timeout_seconds="${GITHUB_ACTIONS_DISCOVERY_TIMEOUT_SECONDS:-300}"
  local completion_timeout_seconds="${GITHUB_ACTIONS_CHECK_TIMEOUT_SECONDS:-1200}"
  local started_at
  local run_id=""
  local run_url=""

  if [[ "${SKIP_GITHUB_ACTIONS_CHECK:-0}" == "1" ]]; then
    echo "Skipping GitHub Actions deployment check because SKIP_GITHUB_ACTIONS_CHECK=1."
    return 0
  fi

  if ! command -v gh >/dev/null 2>&1; then
    echo "Refusing to publish without deployment verification: GitHub CLI is not installed." >&2
    exit 1
  fi

  if ! gh auth status >/dev/null 2>&1; then
    echo "Refusing to publish without deployment verification: GitHub CLI is not authenticated." >&2
    exit 1
  fi

  echo "Waiting for GitHub Pages workflow to start for commit $head_sha..."
  started_at="$(date +%s)"
  while [[ -z "$run_id" ]]; do
    run_id="$(gh run list \
      --workflow pages.yml \
      --branch main \
      --commit "$head_sha" \
      --limit 1 \
      --json databaseId \
      --jq '.[0].databaseId // ""' 2>/dev/null || true)"

    if [[ -n "$run_id" ]]; then
      run_url="$(gh run view "$run_id" --json url --jq '.url' 2>/dev/null || true)"
      break
    fi

    if (( $(date +%s) - started_at >= discovery_timeout_seconds )); then
      echo "GitHub Pages workflow did not start within ${discovery_timeout_seconds}s for commit $head_sha." >&2
      exit 1
    fi

    sleep 10
  done

  echo "Watching GitHub Pages workflow run $run_id: $run_url"
  started_at="$(date +%s)"
  while true; do
    local status
    local conclusion

    status="$(gh run view "$run_id" --json status --jq '.status' 2>/dev/null || true)"
    conclusion="$(gh run view "$run_id" --json conclusion --jq '.conclusion // ""' 2>/dev/null || true)"

    if [[ "$status" == "completed" ]]; then
      if [[ "$conclusion" == "success" ]]; then
        echo "GitHub Pages deployment succeeded: $run_url"
        return 0
      fi

      echo "GitHub Pages deployment failed with conclusion '$conclusion': $run_url" >&2
      echo "Failed step logs:" >&2
      gh run view "$run_id" --log-failed >&2 || true
      exit 1
    fi

    if (( $(date +%s) - started_at >= completion_timeout_seconds )); then
      echo "GitHub Pages workflow did not complete within ${completion_timeout_seconds}s: $run_url" >&2
      exit 1
    fi

    sleep 15
  done
}

if [[ -f "$PAGES_WORKFLOW" ]]; then
  required_actions=(
    "actions/checkout@v5"
    "actions/configure-pages@v6"
    "actions/upload-pages-artifact@v5"
    "actions/deploy-pages@v5"
  )

  for action in "${required_actions[@]}"; do
    if ! grep -q "uses: $action" "$PAGES_WORKFLOW"; then
      echo "Refusing to publish: $PAGES_WORKFLOW must use $action." >&2
      exit 1
    fi
  done

  if grep -q "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" "$PAGES_WORKFLOW"; then
    echo "Refusing to publish: remove FORCE_JAVASCRIPT_ACTIONS_TO_NODE24 from $PAGES_WORKFLOW." >&2
    exit 1
  fi
fi

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
  check_github_pages_deploy "$(git rev-parse HEAD)"
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
