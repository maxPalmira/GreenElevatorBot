# Test Runner Documentation

The test runner provides a streamlined way to execute tests with improved formatting and error handling.

## Basic Usage

```bash
# Run all tests
python tests/run_tests.py

# Run specific types of tests
python tests/run_tests.py --test-type unit

# Run tests matching a regex pattern
python tests/run_tests.py --pattern "menu|core"

# Set a custom timeout (default is 30 seconds)
python tests/run_tests.py --timeout 60
```

## Command Line Arguments

| Option | Description |
|--------|-------------|
| `--pattern PATTERN` | Run tests matching the specified regex pattern |
| `--test-type {unit,integration,all}` | Specify the type of tests to run |
| `--ignore-errors` | Continue running tests even if some fail |
| `--fix-imports` | Automatically fix import errors |
| `--fail-fast` | Stop on first failure |
| `--strict` | Treat errors during collection as failures |
| `--timeout TIMEOUT` | Set timeout in seconds (default: 30) |
| `--traceback-mode {auto,long,short,line,native,no}` | Traceback print mode |

## Command Parameters Cheatsheet

The test runner uses the following pytest parameters:

- `-v`: Verbose output
- `-s`: Show print statements (don't capture)
- `--capture=tee-sys`: Capture and show stdout/stderr
- `--log-cli-level=INFO`: Show INFO level logs
- `--showlocals`: Show local variables in failures
- `--tb=auto`: Automatic traceback formatting
- `--continue-on-collection-errors`: Continue on collection errors
- `--color=yes`: Use colored output

## Output Format

The test output includes:
- Clear test headers with shorter section borders
- Color-coded INFO, WARNING, and ERROR logs
- Blue-colored expected/actual text comparisons 
- Indented output for better readability
- Passed/failed status indicators
- A simplified test summary that shows the number of tests (e.g., `=== 7 tests passed in 0.06s ===`)
- Summary of tests at the end 