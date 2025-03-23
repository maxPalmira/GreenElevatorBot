#!/usr/bin/env python3
"""
Fix imports in test files.

This script fixes common import issues in test files, particularly focusing on:
1. Updating references from src.utils.test_utils to tests.utils.test_utils
2. Other common import path issues in the project

Changes:
- 2025-03-23: Enhanced to fix imports in all test files systematically
- 2025-03-23: Added detection and fixing of test_utils import paths
- 2025-03-23: Added logging and error handling
- 2025-03-23: Moved to tests/ directory for better organization
"""

import os
import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Define import mappings (old_import -> new_import)
IMPORT_MAPPINGS = {
    'src.utils.test_utils': 'tests.utils.test_utils',
    # Add more mappings as needed
}

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    modified = False
    
    # Apply import mappings
    for old_import, new_import in IMPORT_MAPPINGS.items():
        # Fix direct imports
        pattern = rf'from\s+{old_import}\s+import'
        replacement = f'from {new_import} import'
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
            logger.info(f"Fixed import from {old_import} to {new_import} in {file_path}")
        
        # Fix 'import x as y' style imports
        pattern = rf'import\s+{old_import}'
        replacement = f'import {new_import}'
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
            logger.info(f"Fixed import {old_import} to {new_import} in {file_path}")
    
    # Update change log if modified
    if modified:
        # Look for a Change section in the docstring
        change_section = re.search(r'Changes:(.*?)(\n\n|\n[^\n-]|\Z)', content, re.DOTALL)
        today = "2025-03-23"  # Hardcoded for consistency
        
        if change_section:
            # Add our change to the existing change section
            existing_changes = change_section.group(1)
            new_change = f"{existing_changes}\n- {today}: Fixed import paths"
            content = content.replace(existing_changes, new_change)
        else:
            # Look for a docstring to add changes to
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1)
                new_docstring = f"{docstring}\n\nChanges:\n- {today}: Fixed import paths"
                content = content.replace(docstring, new_docstring)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    return False

def find_test_files(root_dir='..'):
    """Find all test files in the project."""
    test_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip virtual environment and hidden directories
        if 'venv' in root or '/.git' in root or '/__pycache__' in root:
            continue
            
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    return test_files

def main():
    """Run the import fixer on all test files."""
    logger.info("Starting import fix process")
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the project root (parent of tests directory)
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    test_files = find_test_files('.')
    logger.info(f"Found {len(test_files)} test files to check")
    
    fixed_count = 0
    error_count = 0
    
    for file_path in test_files:
        try:
            if fix_imports_in_file(file_path):
                fixed_count += 1
        except Exception as e:
            logger.error(f"Error fixing imports in {file_path}: {str(e)}")
            error_count += 1
    
    logger.info(f"Import fix completed. Fixed {fixed_count} files. Errors in {error_count} files.")
    if fixed_count > 0:
        logger.info("Successfully fixed imports. Please run tests to verify.")
    else:
        logger.info("No imports needed fixing.")

if __name__ == "__main__":
    main() 