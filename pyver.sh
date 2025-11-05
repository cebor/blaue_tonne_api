#!/usr/bin/env bash

# Check if version argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <python-version>"
    echo "Example: $0 3.12"
    exit 1
fi

VERSION=$1

# Validate version format
if ! echo $VERSION | grep -q '^3\.[0-9]\+$'; then
    echo "Error: Version must be in format 3.x (e.g., 3.12)"
    exit 1
fi

# Update .python-version
echo $VERSION > .python-version

# Update pyproject.toml
sed -i '' "s/requires-python.*>=.*\"/requires-python = \">=$VERSION\"/" pyproject.toml

# Update Dockerfile (multiple occurrences)
awk -v ver="$VERSION" '
    /^FROM python:/ { gsub(/python:[0-9]+\.[0-9]+/, "python:" ver); }
    { print }
' Dockerfile > Dockerfile.tmp && mv Dockerfile.tmp Dockerfile

# Update .gitlab-ci.yml (only the test job)
awk -v ver="$VERSION" '
    /^  image: python:/ { gsub(/python:[0-9]+\.[0-9]+/, "python:" ver); }
    { print }
' .gitlab-ci.yml > .gitlab-ci.yml.tmp && mv .gitlab-ci.yml.tmp .gitlab-ci.yml

echo "Python version updated to $VERSION in:"
echo "- .python-version"
echo "- pyproject.toml"
echo "- Dockerfile"
echo "- .gitlab-ci.yml"

echo
echo "Note: Don't forget to:"
echo "1. Update your local Python environment"
echo "2. Run 'uv sync' to update dependencies"
echo "3. Test the application"
