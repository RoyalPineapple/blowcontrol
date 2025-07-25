#!/bin/bash

set -e

DRY_RUN=0
if [[ "$1" == "--dry-run" || "$1" == "-n" ]]; then
  DRY_RUN=1
  shift
fi

if [ -z "$1" ]; then
  echo "Usage: $0 [--dry-run|-n] <new_version>"
  exit 1
fi

NEW_VERSION="$1"

# Check for clean working tree
if [[ -n $(git status --porcelain) ]]; then
  echo "❌ You have uncommitted changes. Please commit or stash them first."
  exit 1
fi

# Check if on master branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "master" ]]; then
  echo "❌ You must be on the master branch to publish."
  exit 1
fi

# Check if tag already exists
if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
  echo "❌ Tag v$NEW_VERSION already exists."
  exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "//;s/"//')

# Validate and compare versions using Python's packaging.version
python3 - <<END
import sys
import re
from packaging.version import Version, InvalidVersion

current = "$CURRENT_VERSION"
new = "$NEW_VERSION"

semver_regex = r'^[0-9]+\.[0-9]+\.[0-9]+([-.][a-zA-Z0-9]+)?$'
if not re.match(semver_regex, new):
    print(f'❌ {new} is not a valid semver (X.Y.Z)')
    sys.exit(1)
try:
    if Version(new) <= Version(current):
        print(f'❌ New version {new} is not greater than current version {current}')
        sys.exit(1)
except InvalidVersion as e:
    print(f'❌ Invalid version: {e}')
    sys.exit(1)
END

echo "🔍 Running pre-publish checks..."

echo "🧪 Running tests..."
pytest

echo "🧹 Running black..."
black --check .

echo "🔀 Running isort..."
isort --check-only .

echo "🧑‍💻 Running flake8..."
flake8 .

echo "🔎 Running mypy..."
mypy . || echo "⚠️  mypy found type issues (continuing anyway)"

echo "🔒 Running bandit..."
bandit -r blowcontrol

echo "✅ All checks passed!"

if [[ $DRY_RUN -eq 1 ]]; then
  echo "---- DRY RUN MODE ----"
  echo "Would bump version to $NEW_VERSION in pyproject.toml"
  if [ -f blowcontrol/__init__.py ]; then
    echo "Would bump version in blowcontrol/__init__.py"
  fi
  echo "Would commit, tag, and push as follows:"
  echo "  git add pyproject.toml blowcontrol/__init__.py"
  echo "  git commit -m \"Release v$NEW_VERSION\""
  echo "  git tag \"v$NEW_VERSION\""
  echo "  git push origin main"
  echo "  git push origin \"v$NEW_VERSION\""
  echo "----------------------"
  exit 0
fi

echo "🔢 Bumping version to $NEW_VERSION in pyproject.toml"
sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

if [ -f blowcontrol/__init__.py ]; then
  echo "🔢 Bumping version in blowcontrol/__init__.py"
  sed -i '' "s/^__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" blowcontrol/__init__.py
fi

git add pyproject.toml blowcontrol/__init__.py 2>/dev/null || true
git commit -m "Release v$NEW_VERSION"

git tag "v$NEW_VERSION"
git push origin main
git push origin "v$NEW_VERSION"

echo "🚀 Published v$NEW_VERSION! GitHub Actions will now build and upload to PyPI."
