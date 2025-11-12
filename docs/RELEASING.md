# Release Process

Quick reference guide for maintainers publishing new versions of PlanGEN.

## Quick Start

### First Time Setup

1. **Get PyPI API Tokens**:
   - TestPyPI: https://test.pypi.org/manage/account/
   - Production PyPI: https://pypi.org/manage/account/

2. **Add to GitHub Secrets**:
   - Go to repository Settings → Secrets → Actions
   - Add `TEST_PYPI_API_TOKEN` (for TestPyPI)
   - Add `PYPI_API_TOKEN` (for production PyPI)

### Publishing a New Version

1. **Go to Actions**: https://github.com/cajias/plangen/actions/workflows/publish-pypi.yml

2. **Click "Run workflow"**:
   - **version**: Enter version number (e.g., `0.2.0`)
   - **pypi_environment**: 
     - Choose `test` for testing on TestPyPI
     - Choose `production` for release to PyPI

3. **Test the Release** (if using TestPyPI):
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ plangen
   ```

4. **Verify Installation**:
   ```bash
   python -c "import plangen; print(plangen.__version__)"
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **X.0.0** - Breaking changes
- **0.X.0** - New features (backward compatible)
- **0.0.X** - Bug fixes (backward compatible)

## Workflow Details

The workflow (`.github/workflows/publish-pypi.yml`) automatically:
1. Builds the package with Poetry
2. Publishes to TestPyPI or PyPI (based on your selection)
3. Creates a GitHub release with built artifacts
4. Updates version in `pyproject.toml` (if needed)

## Pre-Release Checklist

Before publishing to production:

- [ ] All tests pass: `pytest`
- [ ] Linting passes: `ruff .` and `black .`
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if you maintain one)
- [ ] Version number follows semantic versioning
- [ ] Test on TestPyPI first

## Post-Release Checklist

After publishing to PyPI:

- [ ] Verify at https://pypi.org/project/plangen/
- [ ] Test installation: `pip install plangen`
- [ ] Update release notes on GitHub
- [ ] Announce on relevant channels

## Troubleshooting

See the comprehensive [Publishing Guide](../PUBLISHING.md) for detailed troubleshooting and advanced topics.

## Additional Resources

- **Full Publishing Guide**: [PUBLISHING.md](../PUBLISHING.md)
- **PyPI Project Page**: https://pypi.org/project/plangen/
- **TestPyPI Project Page**: https://test.pypi.org/project/plangen/
- **Workflow File**: `.github/workflows/publish-pypi.yml`
