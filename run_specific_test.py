#!/usr/bin/env python3
# Script to run a specific test or test case

import sys
import unittest

def run_specific_test():
    """Run a specific test or test case"""
    if len(sys.argv) < 2:
        print("Usage: python run_specific_test.py TestClassName.test_method")
        sys.exit(1)
    
    test_path = sys.argv[1]
    
    # Load the tests module
    import tests
    
    # Try to find the specified test
    loader = unittest.TestLoader()
    if '.' in test_path:
        class_name, method_name = test_path.split('.')
        test_class = getattr(tests, class_name)
        test_suite = loader.loadTestsFromName(method_name, test_class)
    else:
        test_class = getattr(tests, test_path)
        test_suite = loader.loadTestsFromTestCase(test_class)
    
    # Run the test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return appropriate exit code for CI/CD
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_specific_test())
