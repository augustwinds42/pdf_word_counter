# Test Suite Documentation

This document provides an overview of the comprehensive test suite developed for the PDF Word Counter application.

## Test Categories

The test suite is organized into several categories, each focusing on different aspects of the application:

### 1. Unit Tests (PDFWordCounterTests)

Basic tests for core functionality:
- Text preprocessing (`test_preprocess_text`)
- Word counting (`test_count_word_occurrences`)
- Empty word/text handling (`test_count_word_occurrences_empty`)
- File upload validation (`test_invalid_file_upload`)
- UI components (`test_sample_text_checkbox`)
- Session handling (`test_session_handling`)
- Page view routing (`test_view_page_route`)

### 2. Integration Tests (IntegrationTests)

Tests that verify the integration between components:
- PDF processing with real PDFs (`test_pdf_processing`)
- Hyphenation handling in complex PDFs (`test_complex_pdf_processing`)
- End-to-end workflow (`test_end_to_end_processing`)
- No occurrences scenario (`test_no_occurrences`)
- Case insensitivity (`test_case_insensitive_search`)

### 3. Performance Tests (PerformanceTests)

Tests focused on performance and scalability:
- Large text processing (`test_large_text_processing`)
- Text preprocessing with large inputs (`test_text_preprocessing_performance`)

### 4. Security Tests (SecurityTests)

Tests focused on security aspects:
- File size limits (`test_file_size_limit`)
- Path traversal protection (`test_path_traversal`)

### 5. Deployment Tests (DeploymentTests)

Tests to ensure deployment readiness:
- WSGI setup (`test_wsgi_setup`)
- Required packages (`test_requirements`)

## Running Tests

There are several ways to run the tests:

### Run All Tests

```bash
python -m unittest discover
```

### Run with Coverage Reporting

```bash
./run_tests.py
```

This will generate a coverage report and HTML output in the `coverage_html` directory.

### Run a Specific Test

```bash
./run_specific_test.py TestClassName.test_method
```

For example:
```bash
./run_specific_test.py PDFWordCounterTests.test_count_word_occurrences
```

## Test Dependencies

The test suite requires the following packages:
- unittest (built-in)
- coverage
- pytest (for advanced features)
- reportlab (optional, for PDF generation in tests)

## Notes on Test Data

Some tests require test PDF files. If reportlab is available, these are generated automatically. Otherwise, those tests are skipped.

## Continuous Integration

The test suite is integrated with GitHub Actions for continuous integration and deployment:

### GitHub Actions Workflow

Tests are automatically run on each push to the main branch:
- Python environment is set up
- Dependencies are installed
- Full test suite is executed
- Coverage report is generated

### Azure Deployment

After successful test execution, the application is automatically deployed to Azure App Service:
- Only deployments from the main branch are pushed to production
- Code must pass all tests before deployment is initiated
- Code coverage is tracked for quality assurance

To view the CI/CD pipeline details, check the `.github/workflows/azure-deploy.yml` file.

## Coverage Goals

The project maintains the following code coverage targets:
- Overall application code: ≥85% coverage
- Core functionality (PDF processing and word counting): ≥90% coverage
- API endpoints and routes: ≥80% coverage

The current coverage report is available in the `coverage_improvement_report.md` file.
