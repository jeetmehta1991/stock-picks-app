#!/bin/sh
# Pass 53 Day-9 v8h+1 owner-mandated git hook installer (POSIX/git-bash).
# Run ONCE to enable pre-commit enforcement of CHECKLIST rules.

set -e

cd "$(git rev-parse --show-toplevel)"

if [ ! -d .git/hooks ]; then
    echo "ERROR: .git/hooks not found. Are you in a git repo?"
    exit 1
fi

cp scripts/git_hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "Installed: .git/hooks/pre-commit"
echo "Test it: python scripts/preflight.py --staged"
echo ""
echo "To bypass once (NOT recommended): git commit --no-verify"
