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
- 2025-03-23: Added timeout feature to prevent hanging tests
- 2025-03-23: Simplified test summary formatting with fewer = signs
- 2025-03-24: Removed TEXT RESPONSE and BUTTONS headers from output
"""

import os
import sys
import subprocess
import argparse
import re
import signal
import threading
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
    # Skip the "TEXT RESPONSE" and "BUTTONS" headers
    if text in ["TEXT RESPONSE", "BUTTONS"]:
        return
        
    print(color + Colors.BOLD + f" {text} " + Colors.ENDC)

def print_error(text, color=Colors.RED):
    """Print an error message."""
    print(f"\n{color}{Colors.BOLD}ERROR: {text}{Colors.ENDC}")

def print_command_cheatsheet():
    """Print a cheatsheet for the pytest parameters."""
    cheatsheet = {
        "-v": "Verbose output",
        "-s": "Show print statements (don't capture)",
        "--capture=tee-sys": "Capture and show stdout/stderr",
        "--log-cli-level=INFO": "Show INFO level logs",
        "--showlocals": "Show local variables in failures",
        "--tb=auto": "Automatic traceback formatting",
        "--continue-on-collection-errors": "Continue on collection errors",
        "--color=yes": "Use colored output"
    }
    
    print(f"\n{Colors.GRAY}{Colors.BOLD}▶ Command Cheatsheet:{Colors.ENDC}")
    for param, desc in cheatsheet.items():
        print(f"{Colors.GRAY}  {param.ljust(30)} {desc}{Colors.ENDC}")

def process_output(line):
    """Process and format a line of output."""
    # Skip TEXT RESPONSE and BUTTONS lines completely - with more padding variations
    stripped_line = line.strip()
    for pattern in ["TEXT RESPONSE", " TEXT RESPONSE ", "BUTTONS", " BUTTONS "]:
        if pattern in stripped_line or stripped_line == pattern:
            return ""
    
    # Skip collecting line and test session starts line
    if stripped_line.startswith("collecting ...") or "collected" in stripped_line or "test session starts" in stripped_line:
        return ""
    
    # Skip live log call separator
    if "live log call" in stripped_line:
        return ""
    
    # Skip the test file path lines with timestamps (these are the duplicated logs at the beginning)
    if stripped_line.startswith("tests/") and "INFO:" in stripped_line:
        return ""
    
    # Skip duplicate log messages
    if "INFO:" in stripped_line:
        # Skip timestamp logs (they're duplicates)
        if stripped_line.startswith("20"):
            return ""
        # Only show the non-timestamp logs with green color
        return f"      {Colors.GREEN}{stripped_line}{Colors.ENDC}\n"
    
    # Format section dividers
    if stripped_line.startswith("=====") and "=====" in stripped_line:
        section_title = stripped_line.strip().replace("=", "").strip()
        return f"\n{Colors.BG_BLUE}{Colors.BOLD} {section_title} {Colors.ENDC}\n"
    
    # Exact match for the admin menu test line
    if stripped_line == "Testing admin menu":
        return create_test_header("TESTING ADMIN MENU")
    
    # Special case for admin_menu test format
    if "==" in stripped_line and "Testing admin menu" in stripped_line:
        return create_test_header("TESTING ADMIN MENU")
    
    # Check for Testing admin menu in any form
    if "admin menu" in stripped_line and "Testing" in stripped_line:
        return create_test_header("TESTING ADMIN MENU")
    
    # Special case for the 'Testing invalid command handling' text
    if "invalid command handling" in stripped_line:
        return create_test_header("TESTING INVALID COMMAND HANDLING")
    
    # Format test headers for known prefixes
    if stripped_line.startswith("Testing "):
        return create_test_header(stripped_line.strip().upper())
    
    # Format test headers
    if "===== Testing" in stripped_line:
        test_name = stripped_line.strip().replace("===== Testing", "").strip()
        return create_test_header(f"TEST: {test_name.upper()}")
    
    # Format expected text
    if stripped_line.startswith("▶ EXPECTED TEXT:"):
        return f"\n    {Colors.BLUE}{Colors.BOLD}▶ EXPECTED TEXT:{Colors.ENDC}\n      {stripped_line[17:].strip()}\n"
    
    # Format actual text
    if stripped_line.startswith("▶ ACTUAL TEXT:"):
        return f"\n    {Colors.BLUE}{Colors.BOLD}▶ ACTUAL TEXT:{Colors.ENDC}\n      {stripped_line[15:].strip()}\n"
    
    # Format expected markup
    if stripped_line.startswith("▶ EXPECTED MARKUP:"):
        return f"\n    {Colors.BLUE}{Colors.BOLD}▶ EXPECTED BUTTONS:{Colors.ENDC}\n"
    
    # Format actual markup
    if stripped_line.startswith("▶ ACTUAL MARKUP:"):
        return f"\n    {Colors.BLUE}{Colors.BOLD}▶ ACTUAL BUTTONS:{Colors.ENDC}\n"
    
    # Format row information in markup
    if stripped_line.strip().startswith("Row "):
        return f"      {stripped_line.strip()}\n"
    
    # Format expected values
    if stripped_line.startswith("Expected:"):
        return f"\n    {Colors.BLUE}{Colors.BOLD}▶ EXPECTED:{Colors.ENDC}\n      {stripped_line[9:].strip()}\n"
    
    # Format actual values
    if line.startswith("Actual:"):
        return f"\n    {Colors.BLUE}{Colors.BOLD}▶ ACTUAL:{Colors.ENDC}\n      {line[7:].strip()}\n"
    
    # Format markup
    if line.startswith("Markup:"):
        return f"\n    {Colors.BLUE}{Colors.BOLD}▶ BUTTONS:{Colors.ENDC}\n      {line[7:].strip()}\n"
    
    # Format keyboard
    if line.startswith("Keyboard:"):
        return f"    {Colors.BLUE}{Colors.BOLD}▶ KEYBOARD:{Colors.ENDC}      {line[9:].strip()}\n"
    
    # Format first row
    if line.startswith("First row:"):
        return f"    {Colors.BLUE}{Colors.BOLD}▶ FIRST ROW:{Colors.ENDC}      {line[10:].strip()}\n"
    
    # Format first button
    if line.startswith("First button:"):
        return f"    {Colors.BLUE}{Colors.BOLD}▶ FIRST BUTTON:{Colors.ENDC}      {line[13:].strip()}\n"
    
    # Format type of first button
    if line.startswith("Type of first button:"):
        return f"    {Colors.BLUE}{Colors.BOLD}▶ TYPE:{Colors.ENDC}      {line[21:].strip()}\n"
    
    # Highlight import errors
    if "ImportError:" in line or "ModuleNotFoundError:" in line:
        return f"{Colors.BG_RED}{Colors.BOLD} IMPORT ERROR {Colors.ENDC} {Colors.RED}{line.strip()}{Colors.ENDC}\n"
    
    # Format log messages
    if "WARNING:" in line:
        return f"      {Colors.YELLOW}{line.strip()}{Colors.ENDC}\n"
    if "ERROR:" in line:
        return f"      {Colors.RED}{line.strip()}{Colors.ENDC}\n"
    
    # Format test results
    if "PASSED" in line:
        return f"\n    {Colors.BG_GREEN}{Colors.BOLD} PASSED ✓ {Colors.ENDC} {Colors.GREEN}Test completed successfully{Colors.ENDC}\n\n{Colors.GREEN}{'─' * 80}{Colors.ENDC}\n"
    if "FAILED" in line:
        return f"\n    {Colors.BG_RED}{Colors.BOLD} FAILED ✗ {Colors.ENDC} {Colors.RED}Test failed{Colors.ENDC}\n\n{Colors.RED}{'─' * 80}{Colors.ENDC}\n"
    
    # Format pytest collectors warnings
    if "PytestCollectionWarning:" in line:
        return f"      {Colors.YELLOW}{line.strip()}{Colors.ENDC}\n"
    
    # Format separators
    if re.match(r'^-{3,}.*-{3,}$', line.strip()):
        return ""
    
    # Format pytest headers
    if re.match(r'^={3,}.*={3,}$', line.strip()):
        return ""
    
    # Format the summary line with the special pattern
    if "passed in" in stripped_line and "=" in stripped_line:
        # Extract the numbers from the summary (e.g., "7 passed in 0.07s")
        match = re.search(r'(\d+)\s+(passed|failed|skipped).*in\s+(\d+\.\d+)s', stripped_line)
        if match:
            count = match.group(1)
            status = match.group(2).upper()
            time = match.group(3)
            
            # Choose color based on status
            color = Colors.GREEN if status == "PASSED" else Colors.RED
            
            # Create a shorter summary with fewer equal signs
            return f"\n{color}{Colors.BOLD} === {count} tests {status} in {time}s === {Colors.ENDC}\n"
        return ""
    
    # Skip test file path lines
    if line.strip().startswith("tests/") and "::" in line:
        return ""
    
    # Return the line as is if no formatting is applied
    return f"      {line}"

def create_test_header(header_text):
    """Create a standardized, prominent test header."""
    header = f"\n\n{'=' * 40}\n"  # Reduced from 80 to 40
    header += f"{Colors.BG_BLUE}{Colors.BOLD}{' ' * 5}{header_text}{' ' * 5}{Colors.ENDC}\n"
    header += f"{'=' * 40}\n"  # Reduced from 80 to 40
    return header

def run_pytest(test_files, args=None, traceback_mode="auto", timeout=30):
    """Run pytest with specified arguments."""
    args = args or []
    
    # Monkeypatch the test files to suppress unwanted headers
    patch_test_utilities()
    
    # Base command
    cmd = [
        "python", "-m", "pytest",
        *test_files,
        "-v",
        "-s",
        "--capture=tee-sys",
        "--log-cli-level=INFO",
        "--showlocals",
        f"--tb={traceback_mode}",
        "--continue-on-collection-errors",
        "--color=yes",
    ]
    
    # Add any additional arguments
    cmd.extend(args)
    
    # Print the command being run
    print_subheader("Command", Colors.YELLOW)
    print(f"{' '.join(cmd)}")
    
    # Print the command parameter cheatsheet
    print_command_cheatsheet()
    
    print_header("Test Output", Colors.GREEN)
    
    # Use a timeout to prevent tests from hanging
    result = {"returncode": None, "output": "", "timeout": False}
    
    def target():
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        output_lines = []
        
        # Process output in real-time
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ""):
                # Skip unwanted header lines
                if line.strip() in ["TEXT RESPONSE", "BUTTONS"]:
                    continue
                    
                formatted_line = process_output(line)
                if formatted_line:
                    print(formatted_line, end="")
                    output_lines.append(formatted_line)
            
            process.stdout.close()
        
        return_code = process.wait()
        result["returncode"] = return_code
        result["output"] = "".join(output_lines)
    
    # Run the test with a timeout
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    # Check if the thread is still alive (timeout occurred)
    if thread.is_alive():
        print(f"\n{Colors.BG_RED}{Colors.BOLD} TIMEOUT {Colors.ENDC} {Colors.RED}Test execution exceeded {timeout} seconds timeout.{Colors.ENDC}\n")
        result["timeout"] = True
        result["returncode"] = 1  # Set error code
        return result
    
    return result

def patch_test_utilities():
    """Patch the test_utilities.py file to remove unwanted headers."""
    utility_file = "tests/test_utilities.py"
    try:
        if os.path.exists(utility_file):
            with open(utility_file, "r") as f:
                content = f.read()
                
            # Check if we need to patch the file
            if "print('TEXT RESPONSE')" in content or "print('BUTTONS')" in content:
                # Remove print statements for TEXT RESPONSE and BUTTONS
                patched_content = content.replace("print('TEXT RESPONSE')", "# Removed TEXT RESPONSE header")
                patched_content = patched_content.replace("print('BUTTONS')", "# Removed BUTTONS header")
                
                with open(utility_file, "w") as f:
                    f.write(patched_content)
                    
                print("Patched test_utilities.py to remove unwanted headers")
    except Exception as e:
        print(f"Warning: Could not patch test_utilities.py: {e}")

def process_test_output(result):
    """Process the test output and summarize results."""
    # Extract test count and status from the output
    summary_pattern = r'===+\s*(\d+)\s+(passed|failed|skipped).*in\s+(\d+\.\d+)s\s*==+'
    match = re.search(summary_pattern, result["output"])
    
    # Initialize counts
    total_count = 0
    pass_count = 0
    fail_count = 0
    
    if match:
        total_count = int(match.group(1))
        status = match.group(2)
        time_taken = match.group(3)
        
        if status == "passed":
            pass_count = total_count
        elif status == "failed":
            fail_count = total_count
    
    # Print the summary
    print_header("Test Summary", Colors.BLUE)
    print(f"Total tests: {total_count}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {fail_count}")
    
    # Print the final status
    if fail_count == 0 and pass_count > 0:
        print_header("TEST SUITE PASSED", Colors.GREEN)
        # Add a shortened test summary line
        print(f"\n{Colors.GREEN}{Colors.BOLD} === {pass_count} tests PASSED in {time_taken}s === {Colors.ENDC}\n")
    else:
        print_header("TEST SUITE FAILED", Colors.RED)
        # Add a shortened test summary line for failures
        print(f"\n{Colors.RED}{Colors.BOLD} === {fail_count} tests FAILED in {time_taken}s === {Colors.ENDC}\n")
    
    # Return the test result code
    return 0 if fail_count == 0 and result["returncode"] == 0 else 1

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
    parser.add_argument('--strict', action='store_true',
                       help='Fail immediately on collection errors (strict mode)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Timeout in seconds for the test run (default: 30)')
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
    print(f"{Colors.BOLD}Strict Mode:{Colors.ENDC} {'Yes' if args.strict else 'No'}")
    print(f"{Colors.BOLD}Timeout:{Colors.ENDC} {args.timeout} seconds")
    
    # Always run fix_imports for convenience
    print_subheader("Fixing imports...", Colors.YELLOW)
    try:
        # Check if fix_imports.py exists in the tests directory
        fix_imports_path = "tests/fix_imports.py"
        if os.path.exists(fix_imports_path):
            subprocess.run(["python", fix_imports_path], check=True)
            print(f"{Colors.GREEN}Successfully fixed imports{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}fix_imports.py not found in tests directory. Skipping import fixes.{Colors.ENDC}")
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
        
    # Add ignore collection errors by default unless strict mode is enabled
    if not args.strict:
        cmd.append('--continue-on-collection-errors')
    
    # Add color option
    if args.no_color:
        cmd.append('--color=no')
    else:
        cmd.append('--color=yes')
    
    # Print the command being run
    print_subheader("Command", Colors.YELLOW)
    print(f"{' '.join(cmd)}")
    
    # Print the command parameter cheatsheet
    print_command_cheatsheet()
    
    print_header("Test Output", Colors.GREEN)
    
    try:
        # Create a process to run the tests with timeout
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Set up timeout mechanism
        timed_out = False
        terminate_process = False
        
        def timeout_handler():
            nonlocal timed_out, terminate_process
            timed_out = True
            terminate_process = True
            print_error(f"Test run timed out after {args.timeout} seconds!")
            # Force kill the process on timeout
            if process.poll() is None:
                if hasattr(signal, 'SIGKILL'):
                    try:
                        os.kill(process.pid, signal.SIGKILL)
                    except OSError:
                        pass
                else:
                    # Windows fallback
                    process.kill()
        
        # Start timeout timer
        timer = threading.Timer(args.timeout, timeout_handler)
        timer.daemon = True
        timer.start()
        
        # Process and print output line by line
        output_buffer = []
        collection_errors = 0
        
        try:
            # Check if stdout is None before using it
            if process.stdout is not None:
                for line in iter(process.stdout.readline, ''):
                    if terminate_process:
                        break
                    
                    output_buffer.append(line)
                    # Track collection errors
                    if "error during collection" in line:
                        collection_errors += 1
                    # Process and print the line with formatting
                    formatted_line = process_output(line)
                    print(formatted_line, end='')
        except IOError:
            # Handle pipe errors gracefully
            pass
            
        # Wait for process to complete, but not indefinitely
        try:
            exit_code = process.wait(timeout=1)  # Short timeout as we have our own main timeout
        except subprocess.TimeoutExpired:
            exit_code = -1
        
        # Cancel the timeout timer if process completed normally
        timer.cancel()
        
        # Print summary
        print_header("Test Summary", Colors.BLUE)
        
        # Count test results from the output
        output_text = ''.join(output_buffer)
        passed = output_text.count("PASSED")
        failed = output_text.count("FAILED")
        error = output_text.count("ERROR")
        
        # Handle timeout
        if timed_out:
            print(f"{Colors.RED}{Colors.BOLD}Test run timed out after {args.timeout} seconds!{Colors.ENDC}")
            
        # Handle collection errors
        if collection_errors > 0:
            print(f"{Colors.YELLOW}{Colors.BOLD}Collection Errors:{Colors.ENDC} {collection_errors}")
            
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
        
        # Determine exit code based on test results and settings
        if timed_out or (failed > 0 or error > 0) or (collection_errors > 0 and args.strict):
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