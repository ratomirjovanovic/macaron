#!/usr/bin/env python3
"""
MACARON - Test Runner
Simple test runner for the MACARON application

Author: Ratomir Jovanovic
Website: ratomir.com
Version: 1.0
License: MIT (Personal Use) / Commercial License Required for Business Use
Copyright (c) 2025
"""

import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        return False
    print(f"Python version: {sys.version}")
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import tkinter
        print("✓ tkinter available")
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        import unittest
        print("✓ unittest available")
    except ImportError:
        missing_deps.append("unittest")
    
    try:
        from unittest.mock import Mock, patch
        print("✓ unittest.mock available")
    except ImportError:
        missing_deps.append("unittest.mock")
    
    if missing_deps:
        print(f"Missing dependencies: {missing_deps}")
        return False
    
    return True

def run_syntax_check():
    """Check syntax of main application"""
    try:
        import ast
        with open('main.py', 'r') as f:
            source = f.read()
        ast.parse(source)
        print("✓ main.py syntax check passed")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking main.py: {e}")
        return False

def run_unit_tests():
    """Run the unit test suite"""
    try:
        from test_macaron import run_tests
        return run_tests()
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def main():
    """Main test runner"""
    print("MACARON - Test Runner")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("\nInstall missing dependencies:")
        print("sudo apt install python3-tk  # Ubuntu/Debian")
        print("sudo yum install tkinter      # CentOS/RHEL")
        print("sudo pacman -S tk             # Arch Linux")
        return False
    
    # Syntax check
    if not run_syntax_check():
        return False
    
    print("\n" + "=" * 40)
    print("Running Unit Tests...")
    print("=" * 40)
    
    # Run tests
    success = run_unit_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 