#!/usr/bin/env python3
"""
Script to parse PENDING_TASKS.md and create GitHub issues for tasks that aren't yet tracked.

This script:
1. Parses the PENDING_TASKS.md file to extract structured tasks
2. Creates GitHub issues for high-priority tasks
3. Assigns appropriate labels and priorities
"""

import re
import subprocess
import sys
from typing import List, Dict, Tuple
from pathlib import Path


def parse_pending_tasks(file_path: str) -> List[Dict]:
    """Parse PENDING_TASKS.md and extract actionable tasks."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    issues = []
    current_priority = None
    current_section = None
    current_subsection = None
    in_task_list = False
    task_items = []
    section_description = []
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Match priority sections (e.g., "## Priority 1: Critical Issues")
        priority_match = re.match(r'^## (Priority \d+): (.+)$', line)
        if priority_match:
            # Save previous section if it had tasks
            if current_subsection and task_items:
                issues.append({
                    'priority': current_priority,
                    'section': current_section,
                    'subsection': current_subsection,
                    'description': '\n'.join(section_description),
                    'tasks': task_items.copy()
                })
            
            current_priority = priority_match.group(1)
            current_section = priority_match.group(2)
            current_subsection = None
            task_items = []
            section_description = []
            in_task_list = False
            i += 1
            continue
        
        # Match subsections (e.g., "### 1.1 Test Infrastructure Failures")
        subsection_match = re.match(r'^### ([\d.]+) (.+)$', line)
        if subsection_match:
            # Save previous subsection if it had tasks
            if current_subsection and task_items:
                issues.append({
                    'priority': current_priority,
                    'section': current_section,
                    'subsection': current_subsection,
                    'description': '\n'.join(section_description),
                    'tasks': task_items.copy()
                })
            
            current_subsection = subsection_match.group(2)
            task_items = []
            section_description = []
            in_task_list = False
            i += 1
            continue
        
        # Match task items (checkboxes)
        task_match = re.match(r'^- \[([ x])\] (.+)$', line)
        if task_match and current_subsection:
            in_task_list = True
            task_text = task_match.group(2)
            task_items.append(task_text)
            i += 1
            continue
        
        # Collect section description (before tasks start)
        if current_subsection and not in_task_list and line.strip() and not line.startswith('#'):
            # Skip certain metadata lines
            if not line.startswith('**') and not line.startswith('- '):
                section_description.append(line)
        
        i += 1
    
    # Don't forget the last section
    if current_subsection and task_items:
        issues.append({
            'priority': current_priority,
            'section': current_section,
            'subsection': current_subsection,
            'description': '\n'.join(section_description),
            'tasks': task_items.copy()
        })
    
    return issues


def get_priority_label(priority: str) -> str:
    """Map priority level to GitHub label."""
    if 'Priority 1' in priority or 'Priority 8' in priority:
        return 'priority:high'
    elif 'Priority 2' in priority or 'Priority 3' in priority or 'Priority 4' in priority:
        return 'priority:medium'
    else:
        return 'priority:low'


def get_scope_label(section: str, subsection: str) -> str:
    """Determine scope label from section content."""
    text = f"{section} {subsection}".lower()
    
    if 'documentation' in text or 'doc' in text:
        return 'scope:documentation'
    elif 'test' in text or 'coverage' in text:
        return 'scope:testing'
    elif 'infrastructure' in text or 'ci' in text or 'cd' in text:
        return 'scope:infrastructure'
    elif 'api' in text or 'async' in text or 'callback' in text:
        return 'scope:api-design'
    elif 'visualization' in text or 'viz' in text:
        return 'scope:visualization'
    elif 'performance' in text:
        return 'scope:performance'
    elif 'architecture' in text:
        return 'scope:architecture'
    else:
        return 'type:feature'


def get_issue_type_prefix(section: str, subsection: str) -> str:
    """Determine issue type prefix."""
    text = f"{section} {subsection}".lower()
    
    if 'test' in text or 'coverage' in text:
        return '[TEST]'
    elif 'documentation' in text or 'doc' in text:
        return '[DOC]'
    elif 'infrastructure' in text or 'ci' in text or 'cd' in text:
        return '[CICD]'
    elif 'bug' in text or 'fix' in text:
        return '[BUG]'
    else:
        return '[FEAT]'


def create_github_issue(issue_data: Dict, dry_run: bool = True) -> bool:
    """Create a GitHub issue using gh CLI."""
    # Build issue title
    prefix = get_issue_type_prefix(issue_data['section'], issue_data['subsection'])
    title = f"{prefix}: {issue_data['subsection']}"
    
    # Build issue body
    body_parts = [
        f"## Description",
        f"From {issue_data['priority']}: {issue_data['section']}",
        "",
    ]
    
    if issue_data['description'].strip():
        body_parts.append(issue_data['description'])
        body_parts.append("")
    
    body_parts.append("## Tasks")
    for task in issue_data['tasks']:
        body_parts.append(f"- [ ] {task}")
    
    body_parts.extend([
        "",
        "## Context",
        f"This issue was automatically created from PENDING_TASKS.md to track work items.",
        f"**Priority**: {issue_data['priority']}",
        f"**Section**: {issue_data['section']}",
    ])
    
    body = '\n'.join(body_parts)
    
    # Get labels
    priority_label = get_priority_label(issue_data['priority'])
    scope_label = get_scope_label(issue_data['section'], issue_data['subsection'])
    
    if dry_run:
        print(f"\n{'='*80}")
        print(f"WOULD CREATE ISSUE:")
        print(f"Title: {title}")
        print(f"Labels: {priority_label}, {scope_label}")
        print(f"\nBody:\n{body}")
        print(f"{'='*80}")
        return True
    
    try:
        # Create the issue using gh CLI
        cmd = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', body,
            '--label', priority_label,
            '--label', scope_label,
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Created issue: {title}")
        print(f"  URL: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create issue: {title}")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Main function to parse tasks and create issues."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create GitHub issues from PENDING_TASKS.md')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be created without actually creating issues')
    parser.add_argument('--priority', type=int, nargs='+',
                       help='Only create issues for specific priorities (e.g., --priority 1 8)')
    parser.add_argument('--file', default='PENDING_TASKS.md',
                       help='Path to the pending tasks file')
    
    args = parser.parse_args()
    
    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    # Parse the tasks file
    print(f"Parsing {args.file}...")
    issues = parse_pending_tasks(str(file_path))
    
    # Filter by priority if specified
    if args.priority:
        priority_filters = [f"Priority {p}" for p in args.priority]
        issues = [i for i in issues if any(pf in i['priority'] for pf in priority_filters)]
    
    print(f"Found {len(issues)} task sections to convert to issues")
    
    if args.dry_run:
        print("\n*** DRY RUN MODE - No issues will be created ***\n")
    
    # Create issues
    created = 0
    for issue_data in issues:
        if create_github_issue(issue_data, dry_run=args.dry_run):
            created += 1
    
    if args.dry_run:
        print(f"\n*** DRY RUN COMPLETE ***")
        print(f"Would have created {created} issues")
        print(f"\nTo actually create issues, run without --dry-run flag")
        print(f"To create only high-priority issues: --priority 1 8")
    else:
        print(f"\n✓ Successfully created {created} issues")


if __name__ == '__main__':
    main()
