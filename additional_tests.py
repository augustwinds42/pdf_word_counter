import os
import unittest
import tempfile
import io
import shutil
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from flask import render_template
from app import app, allowed_file, process_pdf, extract_text_by_page

# Rename the file to test_additional.py for better unittest discovery

class AdditionalCoverageTests(unittest.TestCase):
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
    
    def test_file_save_exception_handling(self):
        """Test handling of file save exceptions in the upload route"""
        # Create a mock file that will raise an exception when saved
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = "test.pdf"
        mock_file.save.side_effect = Exception("Mock save error")
        
        # Test the upload route with the mock file
        with app.test_request_context():
            response = self.app.post('/', data={
                'pdfFile': mock_file,
                'searchWord': 'test'
            }, follow_redirects=True)
            
            # Should redirect with flash message
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Error saving the file', response.data)
    
    def test_missing_filepath_in_process_pdf(self):
        """Test handling of non-existent files in process_pdf"""
        # Set up a non-existent filepath
        nonexistent_filepath = os.path.join(self.temp_uploads_dir, "nonexistent.pdf")
        
        # Process the non-existent file
        pdf_data, total_count = process_pdf(nonexistent_filepath, "test")
        
        # Should return empty results
        self.assertEqual(pdf_data, [])
        self.assertEqual(total_count, 0)
    
    def test_results_with_empty_pdf_data(self):
        """Test results route with empty pdf_data"""
        # Set up session with empty pdf_data
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': 'test.pdf',
                'search_word': 'test',
                'pdf_data': [],  # Empty data
                'total_count': 0
            }
        
        # Get results page
        response = self.app.get('/results')
        
        # Should show empty results message
        self.assertIn(b'No occurrences of', response.data)
    
    def test_exception_in_results_data_processing(self):
        """Test exception handling in results route when processing data"""
        # Set up session with invalid data structure
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': 'test.pdf',
                'search_word': 'test',
                'pdf_data': [1, 2, 3],  # Invalid data structure (not a tuple)
                'total_count': 0
            }
        
        # Get results page (should handle the exception)
        response = self.app.get('/results', follow_redirects=True)
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Error processing results', response.data)
    
    def test_view_page_complete_flow(self):
        """Test the complete flow of view_page route"""
        # Create a test PDF file
        test_pdf_path = os.path.join(self.temp_uploads_dir, "test_view.pdf")
        with open(test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nTest content')
        
        # Create a mock PDF processing result
        mock_pdf_data = [(1, "Preview text", 1, "Full text content with test word")]
        
        # Set up session
        with self.app.session_transaction() as sess:
            sess['pdf_results'] = {
                'filepath': test_pdf_path,
                'search_word': 'test',
                'pdf_data': [(1, "Preview text", 1)],
                'total_count': 1
            }
        
        # Mock the process_pdf function to return our mock data
        with patch('app.process_pdf', return_value=(mock_pdf_data, 1)):
            response = self.app.get('/view_page/1')
            
            # Check that the view page renders correctly
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Full text content', response.data)
    
    def test_file_deletion_error_handling(self):
        """Test error handling during file deletion in new_search route"""
        # Create a test file
        test_pdf_path = os.path.join(self.temp_uploads_dir, 'test_delete_error.pdf')
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
        
        # Mock os.remove to raise an exception
        with patch('os.remove', side_effect=Exception("Mock removal error")):
            # Call new_search route
            response = self.app.get('/new_search', follow_redirects=True)
            
            # Should still redirect to index despite the error
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Upload PDF', response.data)
    
    def test_error_in_template_rendering(self):
        """Test error handling during template rendering in results route"""
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
        """Test allowed_file function with edge cases to increase coverage"""
        # Test with None (should return False)
        self.assertFalse(allowed_file(None))
        
        # Test with non-string input
        self.assertFalse(allowed_file(123))
        
        # Test with empty string
        self.assertFalse(allowed_file(''))
        
        # Test with string that doesn't have a dot
        self.assertFalse(allowed_file('nodotext'))
    
    def test_upload_disallowed_file(self):
        """Test uploading file with disallowed extension"""
        response = self.app.post('/', data={
            'pdfFile': (io.BytesIO(b'Not a PDF'), 'test.txt'),
            'searchWord': 'test'
        }, follow_redirects=True)
        
        self.assertIn(b'Only PDF files are allowed', response.data)
    
    def test_exception_in_file_removal(self):
        """Test exception handling during file removal in cleanup_temp_files"""
        # Create test files
        test_pdf_path = os.path.join(self.temp_uploads_dir, 'test_removal.pdf')
        with open(test_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.5\nTest content')
        
        # Mock os.remove to raise an exception
        with patch('os.remove', side_effect=Exception("Mock removal error")):
            # Call cleanup function directly
            with app.app_context():
                app.teardown_appcontext_funcs[0](None)
            
            # Function should handle the exception
            # Check that file still exists (wasn't deleted due to exception)
            self.assertTrue(os.path.exists(test_pdf_path))

if __name__ == '__main__':
    unittest.main()
