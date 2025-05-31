import unittest
from tests import PDFWordCounterTests, IntegrationTests, PerformanceTests, SecurityTests, DeploymentTests
from additional_tests import AdditionalCoverageTests

if __name__ == '__main__':
    # Create a test suite with all test cases
    suite = unittest.TestSuite()
    
    # Add original test cases
    suite.addTest(unittest.makeSuite(PDFWordCounterTests))
    suite.addTest(unittest.makeSuite(IntegrationTests))
    suite.addTest(unittest.makeSuite(PerformanceTests))
    suite.addTest(unittest.makeSuite(SecurityTests))
    suite.addTest(unittest.makeSuite(DeploymentTests))
    
    # Add new test cases for additional coverage
    suite.addTest(unittest.makeSuite(AdditionalCoverageTests))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
