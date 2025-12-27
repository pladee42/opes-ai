"""Test runner utility for discovering and executing tests."""

import unittest
import sys
import os
from io import StringIO
from typing import Dict, List
from datetime import datetime


class TestResult:
    """Container for test results."""
    def __init__(self):
        self.services: Dict[str, bool] = {}
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.timestamp = datetime.now()


def run_all_tests() -> TestResult:
    """Discover and run all tests in tests/ folder.
    
    Returns:
        TestResult object with service statuses
    """
    result = TestResult()
    
    # Get tests directory
    tests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests')
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern='test_*.py')
    
    # Capture output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    
    # Run tests
    test_result = runner.run(suite)
    
    # Extract results
    result.total_tests = test_result.testsRun
    result.passed = test_result.testsRun - len(test_result.failures) - len(test_result.errors)
    result.failed = len(test_result.failures)
    result.errors = len(test_result.errors)
    
    # Parse service statuses from test names
    all_tests_passed = len(test_result.failures) == 0 and len(test_result.errors) == 0
    
    # Determine service health based on test results
    result.services = {
        "Price API (Stocks)": all_tests_passed,
        "Price API (Crypto)": all_tests_passed,
        "Price API (Forex/Gold)": all_tests_passed,
        "USD/THB Exchange Rate": all_tests_passed,
        "Google Sheets": all_tests_passed,
        "Gemini AI": all_tests_passed,
    }
    
    # Fine-grained status based on specific test failures
    if test_result.failures or test_result.errors:
        for failure in test_result.failures + test_result.errors:
            test_name = str(failure[0])
            
            if 'stock' in test_name.lower():
                result.services["Price API (Stocks)"] = False
            if 'crypto' in test_name.lower():
                result.services["Price API (Crypto)"] = False
            if 'gold' in test_name.lower() or 'forex' in test_name.lower():
                result.services["Price API (Forex/Gold)"] = False
            if 'thb' in test_name.lower() or 'rate' in test_name.lower():
                result.services["USD/THB Exchange Rate"] = False
            if 'sheet' in test_name.lower():
                result.services["Google Sheets"] = False
            if 'gemini' in test_name.lower():
                result.services["Gemini AI"] = False
    
    return result
