# Issue Creation Workflow

This document provides a visual overview of how the issue creation tool works.

## Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      PENDING_TASKS.md                           │
│  Contains structured tasks with priorities and checkboxes       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              create_issues_from_tasks.py                        │
│  Parses markdown structure and extracts actionable tasks        │
│                                                                 │
│  Features:                                                      │
│  • Identifies priority levels (Priority 1-8)                   │
│  • Extracts sections and subsections                           │
│  • Finds tasks with checkboxes: - [ ] Task                    │
│  • Assigns labels based on content                            │
│  • Generates formatted issue descriptions                      │
└────────────┬───────────────────────────────────┬───────────────┘
             │                                   │
             │                                   │
    ┌────────▼────────┐                 ┌───────▼──────┐
    │   Dry-Run Mode  │                 │  Create Mode │
    │   (--dry-run)   │                 │   (default)  │
    └────────┬────────┘                 └───────┬──────┘
             │                                   │
             ▼                                   ▼
    ┌─────────────────┐             ┌──────────────────────┐
    │  Preview Issues │             │   GitHub CLI (gh)    │
    │  on Console     │             │  Creates Issues via  │
    │                 │             │   GitHub API         │
    └─────────────────┘             └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │  GitHub Issues       │
                                    │  Created with:       │
                                    │  • Title             │
                                    │  • Description       │
                                    │  • Task checklist    │
                                    │  • Labels            │
                                    │  • Context           │
                                    └──────────────────────┘
```

## Input: PENDING_TASKS.md Structure

```markdown
## Priority X: Section Name
### X.Y Subsection Name
**Status:** Description text
**Details:** More details

- [ ] Task item 1
- [ ] Task item 2
- [ ] Task item 3
```

## Output: GitHub Issue

```markdown
Title: [TYPE]: Subsection Name
Labels: priority:level, scope:category

## Description
From Priority X: Section Name

## Tasks
- [ ] Task item 1
- [ ] Task item 2
- [ ] Task item 3

## Context
This issue was automatically created from PENDING_TASKS.md to track work items.
**Priority**: Priority X
**Section**: Section Name
```

## Label Assignment Logic

### Priority Labels
- Priority 1, 8 → `priority:high`
- Priority 2, 3, 4 → `priority:medium`
- Priority 5, 6, 7 → `priority:low`

### Scope Labels (Content-Based)
- Contains "documentation", "doc" → `scope:documentation`
- Contains "test", "coverage" → `scope:testing`
- Contains "infrastructure", "ci", "cd" → `scope:infrastructure`
- Contains "api", "async", "callback" → `scope:api-design`
- Contains "visualization", "viz" → `scope:visualization`
- Contains "performance" → `scope:performance`
- Contains "architecture" → `scope:architecture`
- Default → `type:feature`

### Type Prefixes
- Contains "test", "coverage" → `[TEST]`
- Contains "documentation", "doc" → `[DOC]`
- Contains "infrastructure", "ci", "cd" → `[CICD]`
- Contains "bug", "fix" → `[BUG]`
- Default → `[FEAT]`

## Usage Patterns

### Pattern 1: Preview Before Creating
```bash
# Step 1: See what would be created
python create_issues_from_tasks.py --dry-run

# Step 2: Review the output

# Step 3: Create the issues
python create_issues_from_tasks.py
```

### Pattern 2: Selective Creation
```bash
# Create only high-priority items
python create_issues_from_tasks.py --priority 1 8

# Create only medium-priority items
python create_issues_from_tasks.py --priority 2 3 4
```

### Pattern 3: Manual Creation
```bash
# Step 1: Generate reference document
# (already done: ISSUES_TO_CREATE.md)

# Step 2: Open GitHub and create issues manually
# Copy content from ISSUES_TO_CREATE.md
```

## Current Results

From PENDING_TASKS.md, the tool identified:

```
Priority 8: API Enhancement for Orchestration Framework Integration
├── 8.1 Async Support Implementation → Issue 1
├── 8.2 Callback/Observer System → Issue 2
├── 8.3 Type Safety Improvements → Issue 3
├── 8.4 Configuration Object Pattern → Issue 4
├── 8.5 Workflow Customization/Exposure → Issue 5
├── 8.6 Streaming Support → Issue 6
└── 8.7 Verifier Composition → Issue 7

Total: 7 issues ready to be created
```

## Error Handling

The script handles several error cases:

1. **File not found**: Returns error message and exits
2. **No tasks found**: Reports 0 issues to create
3. **GitHub CLI not available**: Fails gracefully with helpful error
4. **Authentication issues**: Returns GitHub CLI error message
5. **No checkboxes in priority**: Returns 0 issues for that priority

## Future Enhancements

Potential improvements documented in CREATE_ISSUES_README.md:
- Duplicate detection (check existing issues)
- Milestone assignment
- Assignee assignment
- Integration with project boards
- Support for more complex markdown structures
- Automatic linking of related issues
