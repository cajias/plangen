#!/usr/bin/env python3
"""
Generate coverage percentage from coverage.xml for GitHub Actions workflow.
"""

import os
import sys
import xml.etree.ElementTree as ET


def get_coverage_from_xml(coverage_xml):
    """
    Extract coverage percentage from coverage.xml
    """
    try:
        tree = ET.parse(coverage_xml)
        root = tree.getroot()
        coverage = root.get('line-rate')
        if coverage:
            # Convert from decimal (0.75) to percentage (75)
            coverage_pct = round(float(coverage) * 100)
            return coverage_pct
        return None
    except Exception as e:
        print(f"Error parsing coverage XML: {e}")
        return None


def get_coverage_color(coverage_pct):
    """
    Return appropriate color based on coverage percentage
    """
    if coverage_pct >= 90:
        return "brightgreen"
    elif coverage_pct >= 80:
        return "green"
    elif coverage_pct >= 70:
        return "yellowgreen"
    elif coverage_pct >= 60:
        return "yellow"
    elif coverage_pct >= 50:
        return "orange"
    else:
        return "red"


def main():
    """
    Main function to extract coverage and set GitHub Actions environment variables
    """
    if len(sys.argv) > 1:
        coverage_xml = sys.argv[1]
    else:
        coverage_xml = "coverage.xml"

    coverage_pct = get_coverage_from_xml(coverage_xml)
    
    if coverage_pct is not None:
        color = get_coverage_color(coverage_pct)
        
        # Set GitHub Actions environment variables
        github_env = os.environ.get('GITHUB_ENV')
        if github_env:
            with open(github_env, 'a') as f:
                f.write(f"COVERAGE={coverage_pct}\n")
                f.write(f"COVERAGE_COLOR={color}\n")
            print(f"Set coverage to {coverage_pct}% ({color})")
        else:
            print(f"Coverage: {coverage_pct}% ({color})")
    else:
        print("Could not determine coverage")
        # Set default values
        github_env = os.environ.get('GITHUB_ENV')
        if github_env:
            with open(github_env, 'a') as f:
                f.write("COVERAGE=unknown\n")
                f.write("COVERAGE_COLOR=lightgrey\n")


if __name__ == "__main__":
    main()