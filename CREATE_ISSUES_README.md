# Creating GitHub Issues from PENDING_TASKS.md

This directory contains tools to automatically create GitHub issues from tasks described in `PENDING_TASKS.md`.

## Files

- **`create_issues_from_tasks.py`** - Python script that parses PENDING_TASKS.md and creates GitHub issues
- **`ISSUES_TO_CREATE.md`** - Pre-generated list of issues that should be created (for manual reference)
- **`PENDING_TASKS.md`** - Source file containing all pending tasks and features

## Usage

### Option 1: Automatic Creation (Recommended)

This requires GitHub CLI (`gh`) to be installed and authenticated.

```bash
# Preview what would be created (dry-run mode)
python create_issues_from_tasks.py --dry-run

# Create only Priority 8 issues (API enhancements)
python create_issues_from_tasks.py --priority 8

# Create issues for specific priorities (e.g., Priority 1 and 8)
python create_issues_from_tasks.py --priority 1 8

# Create all issues from all priorities that have checkboxes
python create_issues_from_tasks.py
```

### Option 2: Manual Creation

If you don't have gh CLI or prefer manual creation, refer to `ISSUES_TO_CREATE.md` for a detailed list of all issues that should be created, including:
- Full descriptions
- Task checklists
- Priority and labels
- Estimated effort
- Files to modify

You can copy the content from `ISSUES_TO_CREATE.md` directly into GitHub's issue creation form.

## Prerequisites

### For Automatic Creation

1. **Install GitHub CLI**:
   ```bash
   # macOS
   brew install gh
   
   # Linux
   sudo apt install gh  # or appropriate package manager
   
   # Windows
   winget install GitHub.cli
   ```

2. **Authenticate with GitHub**:
   ```bash
   gh auth login
   ```

3. **Verify authentication**:
   ```bash
   gh auth status
   ```

### For GitHub Actions

If running in GitHub Actions, set the `GH_TOKEN` environment variable:

```yaml
- name: Create issues from tasks
  env:
    GH_TOKEN: ${{ github.token }}
  run: python create_issues_from_tasks.py --priority 8
```

## Script Features

The `create_issues_from_tasks.py` script:

- **Parses structured markdown**: Extracts priorities, sections, subsections, and task lists
- **Smart labeling**: Automatically assigns appropriate labels based on content:
  - Priority labels: `priority:high`, `priority:medium`, `priority:low`
  - Scope labels: `scope:documentation`, `scope:testing`, `scope:api-design`, etc.
  - Type prefixes: `[FEAT]`, `[TEST]`, `[DOC]`, `[BUG]`, `[CICD]`
- **Dry-run mode**: Preview issues before creating them
- **Selective creation**: Filter by priority level
- **Detailed metadata**: Includes context from PENDING_TASKS.md

## Current State

As of the last scan, the script found **7 task sections** with actionable items (from Priority 8):

1. Async Support Implementation
2. Callback/Observer System
3. Type Safety Improvements
4. Configuration Object Pattern
5. Workflow Customization/Exposure
6. Streaming Support
7. Verifier Composition

These are all API enhancement features that are not yet tracked as GitHub issues.

## Example Output

```bash
$ python create_issues_from_tasks.py --priority 8

Parsing PENDING_TASKS.md...
Found 7 task sections to convert to issues
✓ Created issue: [FEAT]: Async Support Implementation
  URL: https://github.com/cajias/plangen/issues/28
✓ Created issue: [FEAT]: Callback/Observer System
  URL: https://github.com/cajias/plangen/issues/29
...
✓ Successfully created 7 issues
```

## Customization

To modify how issues are created, edit `create_issues_from_tasks.py`:

- `get_priority_label()` - Adjust priority mapping
- `get_scope_label()` - Adjust scope detection
- `get_issue_type_prefix()` - Adjust issue type prefixes
- `create_github_issue()` - Modify issue body template

## Troubleshooting

### "gh: command not found"
Install GitHub CLI using the instructions in the Prerequisites section.

### "GH_TOKEN not set"
Authenticate with `gh auth login` or set the `GH_TOKEN` environment variable.

### "Permission denied"
Ensure your GitHub token has the `repo` scope to create issues.

### Script finds no issues
Check that PENDING_TASKS.md has sections with checkbox task lists in the format:
```markdown
### X.Y Section Title
- [ ] Task description
- [ ] Another task
```

## Future Enhancements

Potential improvements to the script:
- Support for milestone assignment
- Support for assignee assignment
- Duplicate detection (check existing issues before creating)
- Support for more complex markdown structures
- Integration with project boards
- Automatic linking of related issues

## Contributing

When adding new tasks to `PENDING_TASKS.md`:
1. Use consistent markdown structure with priorities and subsections
2. Use checkboxes `- [ ]` for actionable tasks
3. Include enough context for the task to be understood standalone
4. Consider grouping related tasks under one subsection

Then run the script to create corresponding GitHub issues.
