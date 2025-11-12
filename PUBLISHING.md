# Publishing Guide for PlanGEN

This guide explains how to publish the PlanGEN package to PyPI and TestPyPI using the automated GitHub Actions workflow.

## Prerequisites

Before you can publish to PyPI, you need to set up API tokens as GitHub repository secrets.

### 1. Create PyPI API Tokens

#### For TestPyPI (Development/Testing)

1. Go to https://test.pypi.org/manage/account/
2. Log in or create an account
3. Navigate to "API tokens" section
4. Click "Add API token"
5. Give it a name like "PlanGEN GitHub Actions"
6. Set scope to "Entire account" (or project-specific if you prefer)
7. Click "Add token"
8. **Important**: Copy the token immediately - it will only be shown once!

#### For Production PyPI

1. Go to https://pypi.org/manage/account/
2. Log in with your account
3. Navigate to "API tokens" section
4. Click "Add API token"
5. Give it a name like "PlanGEN GitHub Actions"
6. Set scope to "Entire account" (or project-specific for "plangen")
7. Click "Add token"
8. **Important**: Copy the token immediately - it will only be shown once!

### 2. Configure GitHub Repository Secrets

1. Go to the GitHub repository: https://github.com/cajias/plangen
2. Click "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add the following secrets:

   **For TestPyPI:**
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Paste the token from TestPyPI (starts with `pypi-`)

   **For Production PyPI:**
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the token from PyPI (starts with `pypi-`)

## Publishing Process

The publishing workflow (`.github/workflows/publish-pypi.yml`) supports two methods:

### Method 1: Manual Workflow Dispatch (Recommended)

This method gives you full control over the version and destination.

1. **Navigate to Actions**:
   - Go to https://github.com/cajias/plangen/actions
   - Click on "Publish Python Package to PyPI" workflow

2. **Run Workflow**:
   - Click "Run workflow" button
   - Fill in the parameters:
     - **version**: Package version (e.g., `0.1.0`, `0.2.0`, `1.0.0`)
     - **pypi_environment**: Choose destination
       - `test` - Publishes to TestPyPI (for testing)
       - `production` - Publishes to production PyPI

3. **Wait for Completion**:
   - Monitor the workflow run
   - Check for any errors in the logs
   - The workflow will also create a GitHub release with the artifacts

### Method 2: GitHub Release (Automatic)

When you create a GitHub release, it automatically publishes to TestPyPI.

1. **Create a Release**:
   - Go to https://github.com/cajias/plangen/releases
   - Click "Draft a new release"
   - Create a new tag (e.g., `v0.1.0`)
   - Fill in release title and description
   - Click "Publish release"

2. **Automatic Publishing**:
   - The workflow triggers automatically
   - Package is published to TestPyPI
   - GitHub release includes the built artifacts

## Best Practices

### Testing Before Production Release

**Always test on TestPyPI first!**

1. Run workflow with `pypi_environment: test` and desired version
2. Install from TestPyPI to verify:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ plangen
   ```
3. Test the installed package thoroughly
4. If everything works, run workflow again with `pypi_environment: production`

### Version Management

1. **Update version in code first** (optional, workflow can handle this):
   - Edit `pyproject.toml` - update `version = "x.y.z"`
   - Edit `setup.py` - update `version="x.y.z"`
   - Commit changes before running workflow

2. **Or let the workflow handle it**:
   - The workflow automatically updates the version when using manual dispatch
   - Specify the version in the workflow inputs

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

Examples:
- Development: `0.1.0`, `0.2.0`, `0.3.0`
- First stable: `1.0.0`
- Bug fixes: `1.0.1`, `1.0.2`
- New features: `1.1.0`, `1.2.0`
- Breaking changes: `2.0.0`

## Workflow Details

### What the Workflow Does

1. **Checkout**: Checks out the repository code
2. **Setup Python**: Installs Python 3.9
3. **Install Poetry**: Sets up Poetry for building
4. **Update Version** (if workflow_dispatch): Updates version in pyproject.toml
5. **Build**: Creates wheel and source distribution
6. **Publish to TestPyPI** (if selected): Uploads to test.pypi.org
7. **Publish to PyPI** (if production selected): Uploads to pypi.org
8. **Create GitHub Release** (if workflow_dispatch): Creates a GitHub release with artifacts

### Workflow File Location

`.github/workflows/publish-pypi.yml`

### Required Secrets

- `TEST_PYPI_API_TOKEN` - For TestPyPI publishing
- `PYPI_API_TOKEN` - For production PyPI publishing
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

## Troubleshooting

### Common Issues

#### "Invalid or non-existent authentication information"
- Check that secrets are correctly configured in GitHub
- Verify token hasn't expired
- Ensure token has correct permissions

#### "File already exists"
- You're trying to upload a version that already exists
- Increment the version number
- Note: The workflow has `skip-existing: true` to handle this gracefully

#### "Package name doesn't match"
- Ensure `pyproject.toml` and `setup.py` both specify `name = "plangen"`
- Check that you haven't changed the package name

#### Build Failures
- Run locally first: `python -m build`
- Check `pyproject.toml` and `setup.py` are in sync
- Ensure all dependencies are correctly specified

### Testing Locally

Test the build locally before publishing:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the built package
twine check dist/*

# Test upload to TestPyPI (optional)
twine upload --repository testpypi dist/*
```

## Verifying Published Package

### From TestPyPI

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ plangen

# Verify installation
python -c "import plangen; print(plangen.__version__)"

# Test basic functionality
python -c "from plangen import PlanGen; print('Success!')"
```

### From Production PyPI

```bash
# Install from PyPI
pip install plangen

# Verify installation
python -c "import plangen; print(plangen.__version__)"

# Test basic functionality
python -c "from plangen import PlanGen; print('Success!')"
```

## Post-Release Checklist

After successfully publishing to production PyPI:

- [ ] Verify package is visible at https://pypi.org/project/plangen/
- [ ] Test installation: `pip install plangen`
- [ ] Update README.md if installation instructions changed
- [ ] Announce release on relevant channels
- [ ] Update documentation site (if applicable)
- [ ] Close any related issues or PRs
- [ ] Start planning next release

## Security Considerations

1. **Never commit API tokens** to the repository
2. **Use repository secrets** for all sensitive data
3. **Rotate tokens periodically** (every 6-12 months)
4. **Use project-scoped tokens** when possible
5. **Monitor PyPI account** for unauthorized uploads
6. **Enable 2FA** on PyPI and TestPyPI accounts

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [TestPyPI](https://test.pypi.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Poetry Documentation](https://python-poetry.org/docs/)

## Support

If you encounter issues with the publishing workflow:

1. Check the workflow run logs in GitHub Actions
2. Review this guide for common issues
3. Check PyPI status page: https://status.python.org/
4. Open an issue on GitHub with details and logs
