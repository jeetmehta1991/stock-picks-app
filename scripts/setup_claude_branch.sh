#!/bin/bash
# scripts/setup_claude_branch.sh
# Run this ONCE to set up the claude-updates branch.
# After this, Claude pushes all changes to claude-updates.
# You sync to main by triggering the GitHub Actions workflow.

set -e

echo "=== Setting up claude-updates branch ==="

# Ensure we're on main
git checkout main

# Create claude-updates branch from main if it doesn't exist
if git show-ref --quiet refs/heads/claude-updates; then
  echo "claude-updates branch already exists"
else
  git checkout -b claude-updates
  git push -u origin claude-updates
  git checkout main
  echo "Created and pushed claude-updates branch"
fi

# Create .archive directory for version snapshots
mkdir -p .archive
touch .archive/.gitkeep
git add .archive/.gitkeep
git commit -m "Add .archive directory for version snapshots" --allow-empty
git push origin main

echo ""
echo "=== Setup complete ==="
echo ""
echo "Branch structure:"
echo "  main           — live working version (never edit directly)"
echo "  claude-updates — Claude pushes all changes here"
echo "  .archive/      — automatic snapshots before each sync"
echo ""
echo "Workflow:"
echo "  1. Claude makes changes (pushes to claude-updates)"
echo "  2. You go to GitHub → Actions → Sync from Claude → Run workflow"
echo "  3. Type a description of what changed"
echo "  4. Click Run workflow"
echo "  5. In your Codespace: git pull"
echo "  Done."
