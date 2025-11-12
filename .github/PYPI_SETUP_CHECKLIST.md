# PyPI Publishing Setup Checklist

This checklist guides you through the one-time setup required to enable PyPI publishing for the PlanGEN repository.

## ✅ Completed (Already Done)

- [x] PyPI publishing workflow created (`.github/workflows/publish-pypi.yml`)
- [x] Workflow permissions configured correctly
- [x] Package build configuration verified (`pyproject.toml`, `setup.py`)
- [x] Documentation created (`PUBLISHING.md`, `docs/RELEASING.md`)
- [x] README updated with contributing guidelines

## 🔧 Required Actions (Repository Owner)

### Step 1: Create PyPI Account (if needed)

- [ ] Create or log in to PyPI account at https://pypi.org/
- [ ] Create or log in to TestPyPI account at https://test.pypi.org/
- [ ] Enable 2FA on both accounts (recommended for security)

### Step 2: Generate API Tokens

#### For TestPyPI:
- [ ] Go to https://test.pypi.org/manage/account/
- [ ] Navigate to "API tokens" section
- [ ] Click "Add API token"
- [ ] Name: `PlanGEN GitHub Actions`
- [ ] Scope: `Entire account` (or project-specific after first upload)
- [ ] Copy the token (starts with `pypi-...`)
- [ ] Save it securely (you won't see it again!)

#### For Production PyPI:
- [ ] Go to https://pypi.org/manage/account/
- [ ] Navigate to "API tokens" section
- [ ] Click "Add API token"
- [ ] Name: `PlanGEN GitHub Actions`
- [ ] Scope: `Entire account` (or project-specific for `plangen`)
- [ ] Copy the token (starts with `pypi-...`)
- [ ] Save it securely (you won't see it again!)

### Step 3: Configure GitHub Repository Secrets

- [ ] Go to https://github.com/cajias/plangen/settings/secrets/actions
- [ ] Click "New repository secret"
- [ ] Add first secret:
  - Name: `TEST_PYPI_API_TOKEN`
  - Value: [paste TestPyPI token]
  - Click "Add secret"
- [ ] Click "New repository secret" again
- [ ] Add second secret:
  - Name: `PYPI_API_TOKEN`
  - Value: [paste PyPI token]
  - Click "Add secret"

### Step 4: Test the Workflow

- [ ] Go to https://github.com/cajias/plangen/actions/workflows/publish-pypi.yml
- [ ] Click "Run workflow"
- [ ] Select branch: `main` (or your default branch)
- [ ] Enter version: `0.1.0` (or current version)
- [ ] Select environment: `test`
- [ ] Click "Run workflow"
- [ ] Wait for workflow to complete
- [ ] Check for any errors in the logs

### Step 5: Verify TestPyPI Publication

- [ ] Go to https://test.pypi.org/project/plangen/
- [ ] Verify the package appears
- [ ] Test installation:
  ```bash
  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ plangen
  ```
- [ ] Test basic functionality:
  ```bash
  python -c "import plangen; print(plangen.__version__)"
  ```

### Step 6: Publish to Production PyPI (when ready)

- [ ] Ensure all tests pass
- [ ] Ensure documentation is complete
- [ ] Run workflow again with `production` environment
- [ ] Verify at https://pypi.org/project/plangen/
- [ ] Test installation: `pip install plangen`

### Step 7: Final Setup

- [ ] Document the release process for other maintainers
- [ ] Set up branch protection rules (optional but recommended)
- [ ] Configure release automation (optional)
- [ ] Close the PyPI publishing issue

## 📚 Documentation References

- **Detailed Guide**: [PUBLISHING.md](../PUBLISHING.md)
- **Quick Reference**: [docs/RELEASING.md](../docs/RELEASING.md)
- **Contributing Guide**: [README.md](../README.md#contributing)

## 🔒 Security Best Practices

- ✓ Never commit API tokens to the repository
- ✓ Use repository secrets for sensitive data
- ✓ Enable 2FA on PyPI accounts
- ✓ Use project-scoped tokens when possible
- ✓ Rotate tokens periodically (every 6-12 months)
- ✓ Monitor PyPI account for unauthorized uploads

## ❓ Need Help?

- Check the troubleshooting section in [PUBLISHING.md](../PUBLISHING.md#troubleshooting)
- Review GitHub Actions logs for error details
- Verify secrets are correctly named and configured
- Ensure tokens haven't expired

## ✅ Completion

Once all steps are completed:
- [ ] Delete this checklist file (optional)
- [ ] Update team documentation
- [ ] Announce PyPI availability to users
- [ ] Close the PyPI setup issue

---

**Created**: 2025-11-11
**Status**: Pending repository owner action
**Issue**: Setup PyPI publishing workflow
