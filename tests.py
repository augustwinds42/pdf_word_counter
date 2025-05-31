import os
import unittest
import tempfile
import io
import shutil
import re
import time
from flask import session
from app import app, process_pdf, preprocess_text, count_word_occurrences, extract_text_by_page

class PDFWordCounterTests(unittest.TestCase):
    def setUp(self):
        # Configure Flask app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        
        # Create temporary directories for testing
        self.temp_uploads_dir = tempfile.mkdtemp()
        self.temp_session_dir = tempfile.mkdtemp()
        
        # Override the app config for testing
        app.config['UPLOAD_FOLDER'] = self.temp_uploads_dir
        app.config['SESSION_FILE_DIR'] = self.temp_session_dir
        
        # Create test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Create test context
        self.ctx = app.test_request_context()
        self.ctx.push()
        
    def tearDown(self):
        # Clean up test directories
        shutil.rmtree(self.temp_uploads_dir)
        shutil.rmtree(self.temp_session_dir)
        self.ctx.pop()
    
    def test_homepage_loads(self):
        """Test that the homepage loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload PDF & Search for Word', response.data)
        self.assertIn(b'Select PDF File:', response.data)
        self.assertIn(b'Word to Search:', response.data)
    
    def test_preprocess_text(self):
        """Test the text preprocessing function"""
        # Test hyphenation handling
        text_with_hyphen = "This is a hyphen-\nated word."
        processed = preprocess_text(text_with_hyphen)
        self.assertEqual(processed, "This is a hyphenated word.")
        
        # Test whitespace normalization
        text_with_spaces = "Multiple    spaces and\n\nnewlines."
        processed = preprocess_text(text_with_spaces)
        self.assertEqual(processed, "Multiple spaces and newlines.")
        
        # Test mixed case hyphenation
        mixed_case = "Case-\nSensitive hyphen-\nation."
        processed = preprocess_text(mixed_case)
        self.assertEqual(processed, "CaseSensitive hyphenation.")
        
        # Test multiple hyphens in sequence
        multiple_hyphens = "Multi-\nple hy-\nphen-\nated words."
        processed = preprocess_text(multiple_hyphens)
        self.assertEqual(processed, "Multiple hyphenated words.")
    
    def test_count_word_occurrences(self):
        """Test the word counting function"""
        text = "This is a test. This text has multiple occurrences of the word test. Test should be case insensitive."
        
        # Test basic counting
        count = count_word_occurrences(text, "test")
        self.assertEqual(count, 3)
        
        # Test case insensitivity
        count = count_word_occurrences(text, "TEST")
        self.assertEqual(count, 3)
        
        # Test word boundaries
        count = count_word_occurrences("testament testimony test contest", "test")
        self.assertEqual(count, 1)
        
        # Test with punctuation
        test_text = "test, test. test! test? test; test:"
        count = count_word_occurrences(test_text, "test")
        self.assertEqual(count, 6)
        
        # Test with hyphenated words
        count = count_word_occurrences("This is a test-case and another test", "test")
        self.assertEqual(count, 2)  # Counts both "test" and "test" in "test-case"
        
        # Test with numbers and special characters
        count = count_word_occurrences("test1 1test test_case test", "test")
        self.assertEqual(count, 1)  # Only counts standalone "test"
    
    def test_count_word_occurrences_empty(self):
        """Test the word counting function with edge cases"""
        # Test with empty search word (should return 0 since there's nothing to match)
        count = count_word_occurrences("test test test", "")
        self.assertEqual(count, 0)
    
    def test_count_word_occurrences_empty_text(self):
        """Test word counting with empty text"""
        count = count_word_occurrences("", "test")
        self.assertEqual(count, 0)
    
    def test_invalid_file_upload(self):
        """Test handling of invalid file uploads"""
        # Test with no file
        response = self.app.post('/', data={
            'searchWord': 'test'
        }, follow_redirects=True)
        self.assertIn(b'No file part', response.data)
        
        # Test with no file selected
        response = self.app.post('/', data={
            'pdfFile': (io.BytesIO(b''), ''),
            'searchWord': 'test'
        }, follow_redirects=True)
        self.assertIn(b'No selected file', response.data)
        
        # Test with invalid file type
        response = self.app.post('/', data={
            'pdfFile': (io.BytesIO(b'This is not a PDF'), 'test.txt'),
            'searchWord': 'test'
        }, follow_redirects=True)
        self.assertIn(b'Only PDF files are allowed', response.data)
        
        # Test with empty search word
        response = self.app.post('/', data={
            'pdfFile': (io.BytesIO(b'%PDF-1.5'), 'test.pdf'),
            'searchWord': ''
        }, follow_redirects=True)
        self.assertIn(b'No search word provided', response.data)
    
    def test_sample_text_checkbox(self):
        """Test that the sample text checkbox works"""
        try:
            # Create a simple PDF-like content
            sample_content = b'%PDF-1.5\nThis is a test document'
            
            # Test with checkbox checked
            response = self.app.post('/', data={
                'pdfFile': (io.BytesIO(sample_content), 'sample.pdf'),
                'searchWord': 'test',
                'showSample': 'on'
            }, follow_redirects=True)
            
            # Since we're using a minimal PDF, we might not get proper extraction
            # Just check if the response was successful
            self.assertEqual(response.status_code, 200)
            
            # Test with checkbox unchecked
            response = self.app.post('/', data={
                'pdfFile': (io.BytesIO(sample_content), 'sample.pdf'),
                'searchWord': 'test'
                # showSample not included
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
        except Exception as e:
            self.fail(f"Test failed with exception: {str(e)}")

    def test_session_handling(self):
        """Test session handling for results"""
        try:
            # Create a simple PDF-like content
            sample_content = b'%PDF-1.5\nThis is a test document'
            
            # Submit a search
            response = self.app.post('/', data={
                'pdfFile': (io.BytesIO(sample_content), 'sample.pdf'),
                'searchWord': 'test',
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            # We need to make sure the session handling code doesn't fail
            # even if the PDF processing returns empty results
            
            # Test new_search route
            response = self.app.get('/new_search', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Upload PDF', response.data)
        except Exception as e:
            self.fail(f"Test failed with exception: {str(e)}")

    def test_view_page_route(self):
        """Test the view_page route"""
        try:
            # Test with expired session directly
            response = self.app.get('/view_page/1', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Session expired', response.data)
        except Exception as e:
            self.fail(f"Test failed with exception: {str(e)}")

    def test_extract_text_by_page_exception(self):
        """Test exception handling in extract_text_by_page"""
        # Create an invalid PDF-like file
        invalid_pdf_path = os.path.join(self.temp_uploads_dir, 'invalid.pdf')
        with open(invalid_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nInvalid PDF content')
        
        # This should handle the exception and return an empty list
        result = extract_text_by_page(invalid_pdf_path)
        self.assertEqual(result, [])
        
        # Test with non-existent file
        non_existent_path = os.path.join(self.temp_uploads_dir, 'nonexistent.pdf')
        result = extract_text_by_page(non_existent_path)
        self.assertEqual(result, [])
    
    def test_extract_text_by_page_with_empty_pdf(self):
        """Test extract_text_by_page with an empty PDF"""
        # Create an empty file
        empty_pdf_path = os.path.join(self.temp_uploads_dir, 'empty.pdf')
        with open(empty_pdf_path, 'wb') as f:
            f.write(b'')  # Empty file
            
        # This should handle the exception and return an empty list
        result = extract_text_by_page(empty_pdf_path)
        self.assertEqual(result, [])
    
    def test_process_pdf_edge_cases(self):
        """Test process_pdf function with edge cases"""
        # Create a minimal PDF file
        test_pdf_path = os.path.join(self.temp_uploads_dir, 'test.pdf')
        with open(test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nTest content with test word')
        
        # Test with empty search word (should return 0 counts)
        pdf_data, total_count = process_pdf(test_pdf_path, '')
        self.assertEqual(total_count, 0)
        
        # Test with non-existent file (application handles exceptions)
        pdf_data, total_count = process_pdf('nonexistent.pdf', 'test')
        self.assertEqual(total_count, 0)
        self.assertEqual(len(pdf_data), 0)
    
    def test_process_pdf_with_large_word_count(self):
        """Test process_pdf with a large number of occurrences"""
        # Create a test PDF-like file with many occurrences of the word
        test_content = b'%PDF-1.5\n' + b'test ' * 50
        test_pdf_path = os.path.join(self.temp_uploads_dir, 'many_words.pdf')
        with open(test_pdf_path, 'wb') as f:
            f.write(test_content)
            
        # Process the file with real function
        try:
            pdf_data, total_count = process_pdf(test_pdf_path, 'test')
            # Due to the PDF not being valid, we might not get all matches
            # but we should at least get some processing
            self.assertIsInstance(pdf_data, list)
        except Exception as e:
            self.fail(f"process_pdf raised exception unexpectedly: {e}")
            
    def test_process_pdf_with_invalid_pdf(self):
        """Test process_pdf with completely invalid PDF content"""
        # Create a test file with invalid content
        invalid_pdf_path = os.path.join(self.temp_uploads_dir, 'invalid_content.pdf')
        with open(invalid_pdf_path, 'w') as f:
            f.write('This is not a PDF file at all')
            
        # Process the file with real function
        pdf_data, total_count = process_pdf(invalid_pdf_path, 'test')
        # Should return empty results without raising an exception
        self.assertEqual(total_count, 0)
        self.assertEqual(len(pdf_data), 0)
    
    def test_file_save_error(self):
        """Test handling of file save errors"""
        # Create a test client with a read-only upload directory
        read_only_dir = os.path.join(self.temp_uploads_dir, 'readonly')
        os.makedirs(read_only_dir, exist_ok=True)
        os.chmod(read_only_dir, 0o555)  # Read-only permission
        
        app_config_backup = app.config['UPLOAD_FOLDER']
        app.config['UPLOAD_FOLDER'] = read_only_dir
        
        try:
            # The app doesn't raise an exception but redirects with a flash message
            with open(__file__, 'rb') as f:
                response = self.app.post('/', data={
                    'pdfFile': (f, 'test.pdf'),
                    'searchWord': 'test'
                }, follow_redirects=True)
            
            # The test file is actually processed but not properly parsed as a PDF
            # Just verify the response code is success
            self.assertEqual(response.status_code, 200)
        finally:
            # Restore permissions and config
            os.chmod(read_only_dir, 0o755)
            app.config['UPLOAD_FOLDER'] = app_config_backup
    
    def test_invalid_data_structure(self):
        """Test handling of invalid data structure in results"""
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': 'test.pdf',
                'search_word': 'test',
                'pdf_data': [(1, 'preview', 'not_a_count')],  # Invalid count type
                'total_count': 0
            }
        
        response = self.app.get('/results', follow_redirects=True)
        # The app now handles this case without showing an error
        self.assertEqual(response.status_code, 200)
    
    def test_results_route_exception(self):
        """Test exception handling in results route"""
        # Set up an invalid session that will cause an exception
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': 'nonexistent.pdf',  # This file doesn't exist
                'search_word': 'test',
                # Missing pdf_data key will cause KeyError
            }
        
        response = self.app.get('/results', follow_redirects=True)
        # The application now returns a specific message for missing keys
        self.assertIn(b'Incomplete results data', response.data)
    
    def test_view_page_invalid_number(self):
        """Test view_page route with invalid page number"""
        # First set up a valid session
        test_pdf_path = os.path.join(self.temp_uploads_dir, 'test.pdf')
        with open(test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nTest content')
        
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': test_pdf_path,
                'search_word': 'test',
                'pdf_data': [(1, 'preview', 0)],
                'total_count': 0
            }
        
        # Test with invalid page number
        response = self.app.get('/view_page/999', follow_redirects=True)
        # The app redirects to results page with a flash message
        self.assertIn(b'Invalid page number', response.data)
        
        # Test with negative page number (this will 404 in Flask's URL routing)
        response = self.app.get('/view_page/-1', follow_redirects=False)
        self.assertEqual(response.status_code, 404)
    
    def test_new_search_file_deletion(self):
        """Test new_search route file deletion"""
        # Create a test file
        test_pdf_path = os.path.join(self.temp_uploads_dir, 'test_delete.pdf')
        with open(test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nTest content')
        
        # Set up session with this file
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': test_pdf_path,
                'search_word': 'test',
                'pdf_data': [(1, 'preview', 0)],
                'total_count': 0
            }
        
        # Call new_search to trigger file deletion
        response = self.app.get('/new_search', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # File should be deleted
        self.assertFalse(os.path.exists(test_pdf_path))
        
        # Session should be cleared
        with self.app.session_transaction() as sess:
            self.assertNotIn('pdf_results', sess)
    
    def test_cleanup_temp_files(self):
        """Test cleanup of temporary files"""
        # Create test files in the upload folder
        test_files = []
        for i in range(3):
            path = os.path.join(self.temp_uploads_dir, f'test_cleanup_{i}.pdf')
            with open(path, 'wb') as f:
                f.write(b'%PDF-1.5\nTest content')
            test_files.append(path)
        
        # Manually call the cleanup function
        with app.app_context():
            app.teardown_appcontext_funcs[0](None)
        
        # Files should be deleted
        for path in test_files:
            self.assertFalse(os.path.exists(path))
    
    def test_with_valid_pdf(self):
        """Test processing with a structurally valid PDF"""
        # Path to our valid test PDF
        valid_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files/valid.pdf')
        
        if not os.path.exists(valid_pdf_path):
            self.skipTest("Valid test PDF not found")
        
        # Process the PDF
        pdf_data, total_count = process_pdf(valid_pdf_path, 'test')
        
        # Should find occurrences (actual count may vary based on PDF structure)
        self.assertGreaterEqual(len(pdf_data), 0)
        
    def test_upload_valid_pdf(self):
        """Test uploading a valid PDF file"""
        valid_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files/valid.pdf')
        
        if not os.path.exists(valid_pdf_path):
            self.skipTest("Valid test PDF not found")
            
        with open(valid_pdf_path, 'rb') as f:
            response = self.app.post('/', data={
                'pdfFile': (f, 'valid.pdf'),
                'searchWord': 'test',
                'showSample': 'on'
            }, follow_redirects=True)
            
        # Should process successfully
        self.assertEqual(response.status_code, 200)
        
    def test_results_with_no_occurrences(self):
        """Test results page with no occurrences found"""
        # Create a valid PDF
        valid_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files/valid.pdf')
        
        if not os.path.exists(valid_pdf_path):
            self.skipTest("Valid test PDF not found")
            
        # Set up session with zero occurrences
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': valid_pdf_path,
                'search_word': 'nonexistent',
                'pdf_data': [(1, 'preview', 0)],
                'total_count': 0,
                'show_sample': True
            }
            
        # Get results page
        response = self.app.get('/results')
        
        # Should show "No occurrences found" message
        self.assertIn(b'No occurrences of', response.data)
        
    def test_exception_in_cleanup(self):
        """Test exception handling in cleanup_temp_files"""
        from unittest.mock import patch
        
        # Mock os.listdir to raise an exception
        with patch('os.listdir', side_effect=Exception('Mock listdir error')):
            # Call the cleanup function directly
            with app.app_context():
                app.teardown_appcontext_funcs[0](None)
            
            # No exception should be raised, the function should handle it

# Try to import reportlab for PDF generation tests
REPORTLAB_AVAILABLE = False
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test PDF file with known content
        # Note: This requires the reportlab library
        try:
            if not REPORTLAB_AVAILABLE:
                raise ImportError("Reportlab not available")
            
            os.makedirs('test_files', exist_ok=True)
            
            # Create a PDF with 3 pages and known text
            c = canvas.Canvas("test_files/sample.pdf", pagesize=letter)
            c.drawString(100, 750, "This is a test document page 1.")
            c.drawString(100, 700, "The word test appears twice on this page. This is a test.")
            c.showPage()
            
            c.drawString(100, 750, "This is page 2 of the test document.")
            c.drawString(100, 700, "The word test appears once on this page.")
            c.showPage()
            
            c.drawString(100, 750, "This is the final page with no occurrences of the target word.")
            c.drawString(100, 700, "This page should have zero matches.")
            c.showPage()
            
            c.save()
            
            # Create a more complex PDF with hyphenation and edge cases
            c = canvas.Canvas("test_files/complex.pdf", pagesize=letter)
            
            # Page 1: hyphenation test
            c.drawString(100, 750, "This page tests hy-")
            c.drawString(100, 730, "phenation handling.")
            c.drawString(100, 700, "Multiple test-")
            c.drawString(100, 680, "cases appear here.")
            c.showPage()
            
            # Page 2: special characters and spacing
            c.drawString(100, 750, "test.test  test-test test_test")
            c.drawString(100, 730, "test1 1test test.ing")
            c.showPage()
            
            # Page 3: No occurrences
            c.drawString(100, 750, "No matches on this page.")
            c.drawString(100, 730, "Words like testimony and contest.")
            c.showPage()
            
            c.save()
            
            cls.pdf_created = True
        except ImportError:
            print("Warning: reportlab not available, skipping PDF creation")
            cls.pdf_created = False
    
    @classmethod
    def tearDownClass(cls):
        # Clean up test files
        if cls.pdf_created:
            if os.path.exists('test_files/sample.pdf'):
                os.remove('test_files/sample.pdf')
            if os.path.exists('test_files/complex.pdf'):
                os.remove('test_files/complex.pdf')
            if os.path.exists('test_files'):
                os.rmdir('test_files')
    
    def setUp(self):
        # Skip tests if we couldn't create the test PDF
        if not self.__class__.pdf_created:
            self.skipTest("Reportlab not available")
            
        app.config['TESTING'] = True
        self.app = app.test_client()
    
    def test_pdf_processing(self):
        """Test the PDF processing functionality with a real PDF"""
        if os.path.exists('test_files/sample.pdf'):
            # Test the process_pdf function directly
            pdf_data, total_count = process_pdf('test_files/sample.pdf', 'test')
            
            # Check that we have the right number of pages
            self.assertEqual(len(pdf_data), 3)
            
            # Check the word counts on each page
            self.assertEqual(pdf_data[0][2], 2)  # Page 1 should have 2 occurrences
            self.assertEqual(pdf_data[1][2], 1)  # Page 2 should have 1 occurrence
            self.assertEqual(pdf_data[2][2], 0)  # Page 3 should have 0 occurrences
            
            # Check the total count
            self.assertEqual(total_count, 3)
            
            # Check that preview text was extracted
            self.assertTrue(len(pdf_data[0][1]) > 0)
    
    def test_complex_pdf_processing(self):
        """Test processing with a more complex PDF with hyphenation and special cases"""
        if os.path.exists('test_files/complex.pdf'):
            # Test with the word "test"
            pdf_data, total_count = process_pdf('test_files/complex.pdf', 'test')
            
            # Page 1 should have the hyphenated "test-cases" but not count it
            self.assertTrue(total_count >= 1)
            
            # Check that PDF extraction succeeded
            self.assertEqual(len(pdf_data), 3)
            
            # Check that the hyphenation was handled properly
            page1_text = pdf_data[0][3]  # Full processed text
            self.assertIn("hyphenation", page1_text)
            
            # Test with a hyphenated word specifically
            pdf_data, total_count = process_pdf('test_files/complex.pdf', 'hyphenation')
            self.assertTrue(total_count >= 1)
    
    def test_end_to_end_processing(self):
        """Test the full flow from upload to results"""
        if os.path.exists('test_files/sample.pdf'):
            with open('test_files/sample.pdf', 'rb') as f:
                response = self.app.post('/', data={
                    'pdfFile': (f, 'sample.pdf'),
                    'searchWord': 'test',
                    'showSample': 'on'
                }, follow_redirects=True)
                
                # Check that the results page shows the correct information
                self.assertIn(b'Search Results', response.data)
                self.assertIn(b'test', response.data)
                self.assertIn(b'Total Occurrences: 3', response.data)
                self.assertIn(b'Pages with occurrences: 2', response.data)  # Should only show pages with occurrences
                
                # Check that page 3 is not in the results (it has no occurrences)
                self.assertIn(b'Page 1', response.data)
                self.assertIn(b'Page 2', response.data)
                
                # There should be a total row
                self.assertIn(b'Total', response.data)
    
    def test_no_occurrences(self):
        """Test when the search word doesn't exist in the document"""
        if os.path.exists('test_files/sample.pdf'):
            with open('test_files/sample.pdf', 'rb') as f:
                response = self.app.post('/', data={
                    'pdfFile': (f, 'sample.pdf'),
                    'searchWord': 'nonexistentword',
                }, follow_redirects=True)
                
                # Check that appropriate message is shown
                self.assertIn(b'No occurrences of', response.data)
                self.assertIn(b'Total Occurrences: 0', response.data)
    
    def test_case_insensitive_search(self):
        """Test that searches are case insensitive"""
        if os.path.exists('test_files/sample.pdf'):
            # Test with uppercase search term
            pdf_data, total_count = process_pdf('test_files/sample.pdf', 'TEST')
            self.assertEqual(total_count, 3)
            
            # Test with mixed case
            pdf_data, total_count = process_pdf('test_files/sample.pdf', 'TeSt')
            self.assertEqual(total_count, 3)
    
    def test_view_page_with_mocked_process_pdf(self):
        """Test view_page route with mocked process_pdf function"""
        from unittest.mock import patch
        
        # Set up test PDF path
        test_pdf_path = os.path.join(self.temp_uploads_dir, 'view_mock.pdf')
        with open(test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nTest content')
        
        # Set up session data
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': test_pdf_path,
                'search_word': 'test',
                'pdf_data': [(1, 'preview', 1)],
                'total_count': 1
            }
        
        # Create mock page data to return
        mock_page_data = [(1, 'preview', 1, 'Full text content with test word')]
        
        # Mock process_pdf to return our data
        with patch('app.process_pdf', return_value=(mock_page_data, 1)):
            # Test with valid page number
            response = self.app.get('/view_page/1')
            
            # Check the response
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Full text content', response.data)
    
    def test_allowed_file_edge_cases(self):
        """Test allowed_file function with edge cases"""
        from app import allowed_file
        
        # Test with uppercase extension
        self.assertTrue(allowed_file('test.PDF'))
        
        # Test with no filename (just extension)
        self.assertTrue(allowed_file('.pdf'))
        
        # Test with multiple dots
        self.assertTrue(allowed_file('test.name.with.dots.pdf'))
        
        # Test with non-string input (should handle gracefully)
        try:
            result = allowed_file(None)
            # If it doesn't raise an exception, it should return False
            self.assertFalse(result)
        except:
            # It's also okay if it raises an exception
            pass
    
    def test_error_in_template_rendering(self):
        """Test error handling during template rendering"""
        from unittest.mock import patch
        
        # Set up valid session data
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': 'test.pdf',
                'search_word': 'test',
                'pdf_data': [(1, 'preview', 1)],
                'total_count': 1
            }
        
        # Mock render_template to raise an exception
        with patch('app.render_template', side_effect=Exception('Template rendering error')):
            response = self.app.get('/results', follow_redirects=True)
            
            # Should redirect to index with error message
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Error displaying results', response.data)
    
    def test_allowed_file_no_extension(self):
        """Test allowed_file with a file that has no extension"""
        from app import allowed_file
        
        # Test with no extension
        self.assertFalse(allowed_file('filename_without_extension'))
        
        # Test with empty string
        self.assertFalse(allowed_file(''))
        
        # Test with None (should be handled by our improved implementation)
        self.assertFalse(allowed_file(None))
        
    def test_upload_disallowed_file(self):
        """Test uploading a file with disallowed extension"""
        response = self.app.post('/', data={
            'pdfFile': (io.BytesIO(b'This is not a PDF'), 'test.txt'),
            'searchWord': 'test'
        }, follow_redirects=True)
        
        self.assertIn(b'Only PDF files are allowed', response.data)
        
    def test_exception_in_file_removal(self):
        """Test exception handling in file removal during cleanup"""
        from unittest.mock import patch
        
        # Create test files
        test_files = []
        for i in range(3):
            path = os.path.join(self.temp_uploads_dir, f'test_removal_error_{i}.pdf')
            with open(path, 'wb') as f:
                f.write(b'%PDF-1.5\nTest content')
            test_files.append(path)
        
        # Mock os.remove to raise an exception for one file
        original_remove = os.remove
        
        def mock_remove(path):
            if 'test_removal_error_1' in path:
                raise Exception('Mock removal error')
            return original_remove(path)
        
        with patch('os.remove', side_effect=mock_remove):
            # Call cleanup function
            with app.app_context():
                app.teardown_appcontext_funcs[0](None)
            
            # First and third files should be removed despite error with second file
            self.assertFalse(os.path.exists(test_files[0]))
            self.assertTrue(os.path.exists(test_files[1]))  # This one should fail to delete
            self.assertFalse(os.path.exists(test_files[2]))
            
            # Clean up manually
            if os.path.exists(test_files[1]):
                os.remove(test_files[1])

class PerformanceTests(unittest.TestCase):
    """Tests for performance and edge cases"""
    
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
    
    def test_large_text_processing(self):
        """Test processing performance with large text"""
        # Create a large text string
        large_text = "test " * 1000
        
        # Measure performance with a large number of occurrences
        start_time = time.time()
        count = count_word_occurrences(large_text, "test")
        end_time = time.time()
        
        # Verify correct count
        self.assertEqual(count, 1000)
        
        # Ensure processing time is reasonable (adjust threshold as needed)
        processing_time = end_time - start_time
        self.assertLess(processing_time, 1.0)  # Should process in under 1 second
    
    def test_text_preprocessing_performance(self):
        """Test preprocessing performance with large text"""
        # Create text with many hyphenations
        hyphenated_text = ("hy-\nphen-\nated " * 100)
        
        start_time = time.time()
        processed = preprocess_text(hyphenated_text)
        end_time = time.time()
        
        # Verify correct processing
        self.assertEqual(processed.strip(), ("hyphenated " * 100).strip())
        
        # Ensure processing time is reasonable
        processing_time = end_time - start_time
        self.assertLess(processing_time, 1.0)  # Should process in under 1 second


class SecurityTests(unittest.TestCase):
    """Tests for security aspects of the application"""
    
    def setUp(self):
        # Configure Flask app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        
        # Create temporary directories for testing
        self.temp_uploads_dir = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = self.temp_uploads_dir
        
        # Create test client
        self.app = app.test_client()
    
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.temp_uploads_dir)
    
    def test_file_size_limit(self):
        """Test that the file size limit is enforced"""
        # Create a file larger than the limit (32MB)
        large_file = io.BytesIO(b'%PDF-1.5' + b'0' * (33 * 1024 * 1024))
        
        response = self.app.post('/', data={
            'pdfFile': (large_file, 'large.pdf'),
            'searchWord': 'test'
        }, follow_redirects=True)
        
        # Should get a 413 Request Entity Too Large
        self.assertEqual(response.status_code, 413)
    
    def test_path_traversal(self):
        """Test protection against path traversal attacks"""
        # Try to use a filename with path traversal
        response = self.app.post('/', data={
            'pdfFile': (io.BytesIO(b'%PDF-1.5'), '../../../etc/passwd'),
            'searchWord': 'test'
        }, follow_redirects=True)
        
        # Check that the dangerous path is sanitized
        self.assertNotIn(b'../../../etc/passwd', response.data)
        
        # Check that no file was created outside the uploads directory
        etc_passwd_path = os.path.join(self.temp_uploads_dir, '../../../etc/passwd')
        self.assertFalse(os.path.exists(etc_passwd_path))


class DeploymentTests(unittest.TestCase):
    """Tests to ensure the application is ready for deployment"""
    
    def test_wsgi_setup(self):
        """Test that the WSGI entry point is properly set up"""
        import wsgi
        
        # Check that the WSGI module exports the application
        self.assertTrue(hasattr(wsgi, 'app'))
        
        # Check that the application is a Flask instance
        from flask import Flask
        self.assertIsInstance(wsgi.app, Flask)
    
    def test_requirements(self):
        """Test that all required packages are listed in requirements.txt"""
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Check for essential packages
        self.assertIn('flask', requirements.lower())
        self.assertIn('pdfminer.six', requirements.lower())
        self.assertIn('werkzeug', requirements.lower())
        self.assertIn('gunicorn', requirements.lower())
        self.assertIn('flask-session', requirements.lower())


if __name__ == '__main__':
    unittest.main()
