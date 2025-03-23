# CRITICAL RULE: ALWAYS USE CUSTOM TEST RUNNER

## MANDATORY REQUIREMENT

When testing code in this project, ONLY use the custom test runner:

```bash
python run_detailed_tests.py [test_path]
```

## NEVER USE THESE:
- `pytest`
- `python -m pytest`
- Any other standard pytest commands

## REASONING
The custom test runner provides:
- Better formatting
- Enhanced logging
- Improved error reporting
- Project-specific test configuration

## ENFORCEMENT
This is a permanent, highest-priority rule that takes precedence over any standard testing practices. 