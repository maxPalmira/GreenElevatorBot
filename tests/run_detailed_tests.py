#!/usr/bin/env python3
"""
Custom test runner that shows detailed output for tests.
This script runs pytest with options to show detailed output.

Changes:
- 2025-03-23: Added support for specifying test type (unit, integration, functional)
- 2025-03-23: Added better error handling and reporting
- 2025-03-23: Improved output formatting for test results
- 2025-03-23: Added ability to filter tests by pattern
- 2025-03-23: Renamed from run_detailed_tests.py to run_tests.py
"""

import os
import sys
import subprocess
import argparse
import re
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'
    BG_GREEN = '\033[42m'
    BG_RED = '\033[41m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

def print_header(text, color=Colors.HEADER):
    """Print a formatted header."""
    width = 80
    print("\n" + color + Colors.BOLD + "═" * width + Colors.ENDC)
    print(color + Colors.BOLD + f" {text} ".center(width) + Colors.ENDC)
    print(color + Colors.BOLD + "═" * width + Colors.ENDC + "\n")

def print_subheader(text, color=Colors.CYAN):
    """Print a formatted subheader."""
    print(color + Colors.BOLD + f"\n▶ {text}" + Colors.ENDC)

def print_section(text, color=Colors.BLUE):
    """Print a section divider with text."""
    width = 80
    print("\n" + color + "─" * width + Colors.ENDC)
    print(color + Colors.BOLD + f" {text} " + Colors.ENDC)
    print(color + "─" * width + Colors.ENDC)

def print_error(text, color=Colors.RED):
    """Print an error message."""
    print(f"\n{color}{Colors.BOLD}ERROR: {text}{Colors.ENDC}")

def process_output(line):
    """Process and format a line of output."""
    # Skip collecting line and test session starts line
    if line.strip().startswith("collecting ...") or "collected" in line or "test session starts" in line:
        return ""
    
    # Skip live log call separator
    if "live log call" in line:
        return ""
    
    # Skip the test file path lines with timestamps (these are the duplicated logs at the beginning)
    if line.strip().startswith("tests/") and "INFO:" in line:
        return ""
    
    # Skip duplicate log messages
    if "INFO:" in line:
        # Skip timestamp logs (they're duplicates)
        if line.strip().startswith("20"):
            return ""
        # Only show the non-timestamp logs with green color
        return f"{Colors.GREEN}{line.strip()}{Colors.ENDC}\n"
    
    # Format section dividers
    if line.strip().startswith("=====") and "=====" in line:
        section_title = line.strip().replace("=", "").strip()
        return f"\n{Colors.BG_BLUE}{Colors.BOLD} {section_title} {Colors.ENDC}\n"
    
    # Format test headers
    if "===== Testing" in line:
        test_name = line.strip().replace("===== Testing", "").strip()
        return f"\n\n{Colors.BG_GREEN}{Colors.BOLD}{'=' * 15} TEST: {test_name} {'=' * 15}{Colors.ENDC}\n"
    
    # Format expected text
    if line.startswith("▶ EXPECTED TEXT:"):
        return f"\n{Colors.BLUE}{Colors.BOLD}▶ EXPECTED TEXT:{Colors.ENDC}\n{Colors.BLUE}{line[17:].strip()}{Colors.ENDC}\n"
    
    # Format actual text
    if line.startswith("▶ ACTUAL TEXT:"):
        return f"\n{Colors.BLUE}{Colors.BOLD}▶ ACTUAL TEXT:{Colors.ENDC}\n{Colors.BLUE}{line[15:].strip()}{Colors.ENDC}\n"
    
    # Format expected markup
    if line.startswith("▶ EXPECTED MARKUP:"):
        return f"\n{Colors.GREEN}{Colors.BOLD}▶ EXPECTED BUTTONS:{Colors.ENDC}\n"
    
    # Format actual markup
    if line.startswith("▶ ACTUAL MARKUP:"):
        return f"\n{Colors.GREEN}{Colors.BOLD}▶ ACTUAL BUTTONS:{Colors.ENDC}\n"
    
    # Format row information in markup
    if line.strip().startswith("Row "):
        return f"{Colors.GREEN}  {line.strip()}{Colors.ENDC}\n"
    
    # Format expected values
    if line.startswith("Expected:"):
        return f"\n{Colors.BLUE}{Colors.BOLD}▶ EXPECTED:{Colors.ENDC}\n{Colors.BLUE}{line[9:].strip()}{Colors.ENDC}\n"
    
    # Format actual values
    if line.startswith("Actual:"):
        return f"\n{Colors.BLUE}{Colors.BOLD}▶ ACTUAL:{Colors.ENDC}\n{Colors.BLUE}{line[7:].strip()}{Colors.ENDC}\n"
    
    # Format markup
    if line.startswith("Markup:"):
        return f"\n{Colors.GREEN}{Colors.BOLD}▶ BUTTONS:{Colors.ENDC}\n{Colors.GREEN}{line[7:].strip()}{Colors.ENDC}\n"
    
    # Format keyboard
    if line.startswith("Keyboard:"):
        return f"{Colors.GREEN}{Colors.BOLD}▶ KEYBOARD:{Colors.ENDC} {Colors.GREEN}{line[9:].strip()}{Colors.ENDC}\n"
    
    # Format first row
    if line.startswith("First row:"):
        return f"{Colors.GREEN}{Colors.BOLD}▶ FIRST ROW:{Colors.ENDC} {Colors.GREEN}{line[10:].strip()}{Colors.ENDC}\n"
    
    # Format first button
    if line.startswith("First button:"):
        return f"{Colors.GREEN}{Colors.BOLD}▶ FIRST BUTTON:{Colors.ENDC} {Colors.GREEN}{line[13:].strip()}{Colors.ENDC}\n"
    
    # Format type of first button
    if line.startswith("Type of first button:"):
        return f"{Colors.GREEN}{Colors.BOLD}▶ TYPE:{Colors.ENDC} {Colors.GREEN}{line[21:].strip()}{Colors.ENDC}\n"
    
    # Highlight import errors
    if "ImportError:" in line or "ModuleNotFoundError:" in line:
        return f"{Colors.BG_RED}{Colors.BOLD} IMPORT ERROR {Colors.ENDC} {Colors.RED}{line.strip()}{Colors.ENDC}\n"
    
    # Format log messages
    if "WARNING:" in line:
        return f"{Colors.YELLOW}{line.strip()}{Colors.ENDC}\n"
    if "ERROR:" in line:
        return f"{Colors.RED}{line.strip()}{Colors.ENDC}\n"
    
    # Format test results
    if "PASSED" in line:
        return f"\n{Colors.BG_GREEN}{Colors.BOLD} PASSED ✓ {Colors.ENDC} {Colors.GREEN}Test completed successfully{Colors.ENDC}\n\n{Colors.BG_GREEN}{Colors.BOLD}{'=' * 40}{Colors.ENDC}\n"
    if "FAILED" in line:
        return f"\n{Colors.BG_RED}{Colors.BOLD} FAILED ✗ {Colors.ENDC} {Colors.RED}Test failed{Colors.ENDC}\n\n{Colors.BG_RED}{Colors.BOLD}{'=' * 40}{Colors.ENDC}\n"
    
    # Format pytest collectors warnings
    if "PytestCollectionWarning:" in line:
        return f"{Colors.YELLOW}{line.strip()}{Colors.ENDC}\n"
    
    # Format separators
    if re.match(r'^-{3,}.*-{3,}$', line.strip()):
        return ""
    
    # Format pytest headers
    if re.match(r'^={3,}.*={3,}$', line.strip()):
        return ""
    
    # Format pytest summary
    if re.match(r'^={3,}\s*\d+\s*passed.*in\s*\d+\.\d+s\s*={3,}$', line.strip()):
        return ""
    
    # Skip test file path lines
    if line.strip().startswith("tests/") and "::" in line:
        return ""
    
    # Return the line as is if no formatting is applied
    return line

def main():
    parser = argparse.ArgumentParser(description='Run tests with detailed output')
    parser.add_argument('test_path', nargs='?', default='tests', help='Path to the test file or directory')
    parser.add_argument('--test-name', help='Specific test to run (e.g., TestClass::test_method)')
    parser.add_argument('--test-type', choices=['unit', 'integration', 'functional', 'all'], 
                        default='all', help='Type of tests to run')
    parser.add_argument('--pattern', help='Search pattern to filter test files (e.g., "menu" for menu-related tests)')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--fail-fast', action='store_true', help='Stop on first failure')
    parser.add_argument('--tb', choices=['auto', 'long', 'short', 'line', 'native', 'no'], 
                        default='auto', help='Traceback print mode')
    parser.add_argument('--fix-imports', action='store_true', 
                        help='Attempt to fix common import issues before running tests')
    parser.add_argument('--ignore-errors', action='store_true',
                       help='Continue running tests even if collection errors occur')
    args = parser.parse_args()

    # Disable colors if requested
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')

    # Print run information
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print_header(f"Test Run - {now}", Colors.CYAN)
    
    # Determine test path based on test type
    test_path = args.test_path
    if args.test_type != 'all' and args.test_path == 'tests':
        test_path = f"tests/{args.test_type}"
        if not os.path.exists(test_path):
            print_error(f"Test type directory '{test_path}' does not exist!")
            sys.exit(1)
    
    # Apply pattern filtering if specified
    if args.pattern:
        if os.path.isdir(test_path):
            matching_files = []
            for root, dirs, files in os.walk(test_path):
                # Skip __pycache__ directories
                if "__pycache__" in root:
                    continue
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        # Use regex pattern matching
                        if re.search(args.pattern, file):
                            matching_files.append(os.path.join(root, file))
            
            if not matching_files:
                print_error(f"No test files matching pattern '{args.pattern}' found in '{test_path}'!")
                sys.exit(1)
            
            # Instead of joining with spaces, we'll pass individual files as separate arguments
            test_path = matching_files
    
    # Print test information
    print(f"{Colors.BOLD}Test Path:{Colors.ENDC} {test_path}")
    if args.test_name:
        print(f"{Colors.BOLD}Test Name:{Colors.ENDC} {args.test_name}")
    print(f"{Colors.BOLD}Test Type:{Colors.ENDC} {args.test_type}")
    if args.pattern:
        print(f"{Colors.BOLD}Pattern:{Colors.ENDC} {args.pattern}")
    print(f"{Colors.BOLD}Traceback Mode:{Colors.ENDC} {args.tb}")
    print(f"{Colors.BOLD}Fail Fast:{Colors.ENDC} {'Yes' if args.fail_fast else 'No'}")
    print(f"{Colors.BOLD}Ignore Collection Errors:{Colors.ENDC} {'Yes' if args.ignore_errors else 'No'}")
    
    # Always run fix_imports for convenience
    print_subheader("Fixing imports...", Colors.YELLOW)
    try:
        # Check if fix_imports.py exists in the project root
        if os.path.exists("fix_imports.py"):
            subprocess.run(["python", "fix_imports.py"], check=True)
            print(f"{Colors.GREEN}Successfully fixed imports{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}fix_imports.py not found. Skipping import fixes.{Colors.ENDC}")
    except subprocess.CalledProcessError:
        print_error("Failed to fix imports")
    
    # Build the command
    cmd = ['python', '-m', 'pytest']
    
    # Add the test path and name if specified
    if args.test_name:
        # Handle both full path and just test name formats
        if "::" in args.test_name:
            cmd.append(args.test_name)
        else:
            if isinstance(test_path, list):
                # If we have multiple files, we need to select one
                if len(test_path) > 0:
                    cmd.append(f"{test_path[0]}::{args.test_name}")
                else:
                    print_error(f"No test files found to run test {args.test_name}")
                    sys.exit(1)
            else:
                cmd.append(f"{test_path}::{args.test_name}")
    else:
        # Add each test file as a separate argument
        if isinstance(test_path, list):
            cmd.extend(test_path)
        else:
            cmd.append(test_path)
    
    # Add options for detailed output
    cmd.extend([
        '-v',                # Verbose output
        '-s',                # Show print statements
        '--capture=tee-sys', # Capture and show stdout/stderr
        '--log-cli-level=INFO', # Show INFO level logs
        '--showlocals',      # Show local variables in failures
        f'--tb={args.tb}',   # Traceback print mode
    ])
    
    # Add fail fast if requested
    if args.fail_fast:
        cmd.append('-x')
        
    # Add ignore collection errors if requested
    if args.ignore_errors:
        cmd.append('--continue-on-collection-errors')
    
    # Add color option
    if args.no_color:
        cmd.append('--color=no')
    else:
        cmd.append('--color=yes')
    
    # Print the command being run
    print_subheader("Command", Colors.YELLOW)
    print(f"{' '.join(cmd)}")
    
    print_header("Test Output", Colors.GREEN)
    
    try:
        # Run the command and capture output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Process and print output line by line
        output_buffer = []
        collection_errors = 0
        
        # Check if stdout is None before using it
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ''):
                output_buffer.append(line)
                # Track collection errors
                if "error during collection" in line:
                    collection_errors += 1
                # Process and print the line with formatting
                formatted_line = process_output(line)
                print(formatted_line, end='')
        
        # Wait for process to complete
        exit_code = process.wait()
        
        # Print summary
        print_header("Test Summary", Colors.BLUE)
        
        # Count test results from the output
        output_text = ''.join(output_buffer)
        passed = output_text.count("PASSED")
        failed = output_text.count("FAILED")
        error = output_text.count("ERROR")
        
        # Handle collection errors
        if collection_errors > 0:
            print(f"{Colors.RED}{Colors.BOLD}Collection Errors:{Colors.ENDC} {collection_errors}")
            
            # Look for common import errors
            imports = re.findall(r"ImportError: No module named ['\"]([^'\"]+)['\"]", output_text)
            if imports:
                print(f"\n{Colors.YELLOW}{Colors.BOLD}Missing Imports:{Colors.ENDC}")
                for imp in set(imports):
                    print(f"{Colors.YELLOW}- {imp}{Colors.ENDC}")
        
        print(f"{Colors.BOLD}Total tests:{Colors.ENDC} {passed + failed + error}")
        print(f"{Colors.GREEN}{Colors.BOLD}Passed:{Colors.ENDC} {passed}")
        print(f"{Colors.RED}{Colors.BOLD}Failed:{Colors.ENDC} {failed}")
        if error > 0:
            print(f"{Colors.RED}{Colors.BOLD}Errors:{Colors.ENDC} {error}")
        
        # Determine exit code based on ignore_errors flag
        if (failed > 0 or error > 0) or (collection_errors > 0 and not args.ignore_errors):
            print_header("TEST SUITE FAILED", Colors.RED)
            sys.exit(1)
        else:
            print_header("TEST SUITE PASSED", Colors.GREEN)
            sys.exit(0)
            
    except KeyboardInterrupt:
        print_error("Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Error running tests: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 