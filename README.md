# PDF Word Counter Web Application

A web-based application that allows users to upload PDF files and search for specific words, displaying the occurrences of the word on each page along with previews of the page content.

## Features

- Advanced PDF text extraction that preserves word integrity
- Handles hyphenation and word breaks common in PDFs
- Interactive web interface with modern design
- Shows page-by-page word occurrence counts
- Ability to view full text of any page with highlighted search terms
- Responsive design that works on mobile and desktop

## Prerequisites

- Python 3.7 or higher
- Flask
- pdfminer.six

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pdf-word-counter-web
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Deployment

### GitHub and Azure Deployment

This application is set up for automated deployment to Azure App Service using GitHub Actions:

1. Push your code to GitHub:
   ```bash
   git push origin main
   ```

2. The GitHub Actions workflow will automatically:
   - Run all tests with coverage reporting
   - Deploy to Azure if tests pass

For detailed deployment instructions, see:
- [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) - Different methods to deploy to Azure
- [AZURE_CONFIGURATION.md](AZURE_CONFIGURATION.md) - How to configure your Azure Web App
- [TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md) - Information about the test suite

### Required Secrets for GitHub Actions

In your GitHub repository, add these secrets:
- `AZURE_WEBAPP_NAME`: Your Azure Web App name
- `AZURE_WEBAPP_PUBLISH_PROFILE`: Content of the publish profile from Azure

This application can be deployed to Azure Web App Service. See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for detailed deployment instructions.

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
  - `base.html`: Base template with layout and styles
  - `index.html`: Home page with file upload form
  - `results.html`: Results page showing word occurrences
  - `page_view.html`: Page view showing full text with highlighted search terms
- `static/css/`: CSS styles
  - `style.css`: Main stylesheet
- `uploads/`: Temporary folder for uploaded PDF files
- `requirements.txt`: List of Python dependencies
- `wsgi.py`: WSGI entry point for production deployment
- `tests.py`: Comprehensive test suite
- `run_tests.py`: Script to run tests with coverage reporting

## Testing

The application includes a comprehensive test suite covering:

1. Unit tests for core functions like text preprocessing and word counting
2. Integration tests for PDF processing functionality
3. End-to-end tests for web application flow
4. Performance tests for text processing with large inputs
5. Security tests for file uploads and path traversal protection
6. Deployment readiness tests

To run the tests:

```bash
# Run basic tests
python -m unittest tests.py

# Run tests with coverage reporting
./run_tests.py
```

After running the coverage report, you can view the HTML coverage report in the `coverage_html` directory.

## How It Works

1. The user uploads a PDF file and enters a search word
2. The application processes the PDF using pdfminer.six with optimized layout parameters
3. Text is extracted from each page and preprocessed to handle word breaks
4. Word occurrences are counted using regular expressions with word boundaries
5. Results are displayed showing pages with occurrences
6. The user can view full text of any page with the search term highlighted

## License

MIT
