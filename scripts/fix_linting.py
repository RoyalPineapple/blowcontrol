#!/usr/bin/env python3
"""
Simple script to fix common linting issues.
Run this before committing to ensure code quality.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running {description}...")
    try:
        # Add user bin directory to PATH for ARM64 tools
        env = os.environ.copy()
        env['PATH'] = f"{os.path.expanduser('~/Library/Python/3.9/bin')}:{env.get('PATH', '')}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"✗ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ {description} failed with exception: {e}")
        return False
    return True


def main():
    """Main function to run all linting fixes."""
    print("🔧 Running linting fixes...")

    # Get the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # List of commands to run - use direct tool calls instead of python3 -m
    commands = [
        ("find . -name '*.py' -exec sed -i '' 's/[[:space:]]*$//' {} \\;", "Remove trailing whitespace"),
        ("find . -name '*.py' -exec sed -i '' '$a\\' {} \\;", "Ensure files end with newline"),
        ("black dyson2mqtt/ tests/ --line-length=88", "Format code with Black"),
        ("isort dyson2mqtt/ tests/ --profile=black", "Sort imports with isort"),
    ]

    success = True
    for cmd, description in commands:
        if not run_command(cmd, description):
            success = False

    if success:
        print("\n🎉 All linting fixes completed successfully!")
        print("You can now commit your changes.")
    else:
        print("\n❌ Some linting fixes failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

