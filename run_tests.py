#!/usr/bin/env python3
# Script to run tests with coverage reporting

import os
import sys
import coverage
import unittest

def run_tests_with_coverage():
    """Run the test suite with coverage reporting"""
    # Start coverage measurement
    cov = coverage.Coverage(
        source=['app', 'pdf_word_counter', 'pdf_word_counter_enhanced', 'pdf_word_counter_advanced'],
        omit=['*/tests.py', '*/run_tests.py', '*/wsgi.py']
    )
    cov.start()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('.')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # End coverage measurement
    cov.stop()
    cov.save()
    
    # Report coverage
    print("\nCoverage Report:")
    cov.report()
    
    # Generate HTML report
    html_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coverage_html')
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
    
    print(f"\nGenerating HTML coverage report in {html_dir}")
    cov.html_report(directory=html_dir)
    
    # Return test result status for CI/CD integration
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests_with_coverage())
