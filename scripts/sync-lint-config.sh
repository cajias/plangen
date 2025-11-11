#!/bin/bash
# Sync canonical lint configuration from cajias/lint-configs repository
# Downloads the v1.0.0 release configuration and updates .ruff.toml

set -e

VERSION="v1.0.0"
REPO_URL="https://raw.githubusercontent.com/cajias/lint-configs"
SOURCE_FILE="${REPO_URL}/${VERSION}/python/pyproject-linters.toml"
RUFF_CONFIG=".ruff.toml"

echo "Syncing Ruff configuration from cajias/lint-configs ${VERSION}..."

# Download the source and extract [tool.ruff] sections
# Convert [tool.ruff] to root-level sections for standalone .ruff.toml
curl -fsSL "${SOURCE_FILE}" | \
  awk '/^\[tool\.ruff\]/,/^$/ {
    if ($0 ~ /^\[tool\.ruff\]$/) next;
    if ($0 ~ /^\[tool\.ruff\./) { sub(/^\[tool\.ruff\./, "["); print; next; }
    print
  }' > "${RUFF_CONFIG}.tmp"

if [ $? -eq 0 ] && [ -s "${RUFF_CONFIG}.tmp" ]; then
    # Add header
    {
        echo "# Canonical Ruff Configuration"
        echo "# Source: https://github.com/cajias/lint-configs/releases/tag/${VERSION}"
        echo "# Based on: python/pyproject-linters.toml from ${VERSION} release"
        echo "# Run scripts/sync-lint-config.sh to update from upstream"
        echo ""
        cat "${RUFF_CONFIG}.tmp"
    } > "${RUFF_CONFIG}"

    rm "${RUFF_CONFIG}.tmp"

    echo "✓ Successfully synced ${RUFF_CONFIG}"
    echo "  Source: ${SOURCE_FILE}"
    echo ""
    echo "Run 'ruff check plangen/' to verify the new configuration."
else
    echo "✗ Failed to sync Ruff configuration"
    rm -f "${RUFF_CONFIG}.tmp"
    exit 1
fi
