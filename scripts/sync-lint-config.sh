#!/bin/bash
# Sync canonical lint configuration from cajias/lint-configs repository
# Run this script to update .ruff.toml with the latest upstream rules

set -e

echo "Syncing Ruff configuration from cajias/lint-configs..."
echo "Note: .ruff.toml is manually maintained based on cajias/lint-configs"
echo "      Visit: https://github.com/cajias/lint-configs/blob/main/python/pyproject-linters.toml"
echo ""
echo "To update .ruff.toml:"
echo "1. Review changes at https://github.com/cajias/lint-configs"
echo "2. Update .ruff.toml with any new rules or settings"
echo "3. Run 'ruff check plangen/' to verify"
echo ""
echo "Current config: .ruff.toml"
