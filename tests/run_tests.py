#!/usr/bin/env python3
"""
Test runner for Dyson2MQTT test suite.
"""

import sys
import os
import subprocess
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_tests(test_type='all', verbose=False, coverage=False, quiet=False):
    """Run the test suite."""
    
    # Base pytest command
    cmd = [sys.executable, '-m', 'pytest']
    
    # Add test directory
    cmd.append('tests/')
    
    # Add verbosity
    if verbose:
        cmd.append('-v')
    elif quiet:
        cmd.append('-q')
    
    # Add coverage if requested
    if coverage:
        cmd.extend(['--cov=dyson2mqtt', '--cov-report=term-missing', '--cov-report=html'])
    
    # Filter by test type
    if test_type == 'unit':
        cmd.append('tests/unit/')
    elif test_type == 'integration':
        cmd.append('tests/integration/')
    elif test_type == 'mocks':
        cmd.append('tests/mocks/')
    elif test_type == 'oscillation':
        cmd.append('test_oscillation_angles.py')
    
    # Run the tests
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run Dyson2MQTT test suite')
    parser.add_argument(
        '--type', '-t',
        choices=['all', 'unit', 'integration', 'mocks', 'oscillation'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet output (minimal verbosity)'
    )
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install test dependencies'
    )
    
    args = parser.parse_args()
    
    # Run tests
    exit_code = run_tests(args.type, args.verbose, args.coverage, args.quiet)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    sys.exit(exit_code)
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'pytest', 'pytest-cov', 'pytest-mock'
        ])
        print("Dependencies installed!")
        print()
    
    # Run tests
    exit_code = run_tests(args.type, args.verbose, args.coverage)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main() 