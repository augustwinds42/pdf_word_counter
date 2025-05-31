import os
import re
import uuid
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from io import StringIO
from flask_session import Session

app = Flask(__name__)
# Use a stronger secret key
app.secret_key = 'BH4Srt5K6t0WBEp1WyBrHV73VDOgCFXH'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Initialize Flask-Session
Session(app)

# Create uploads folder and session folder if they don't exist
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config['UPLOAD_FOLDER'])
os.makedirs(uploads_dir, exist_ok=True)

session_dir = app.config['SESSION_FILE_DIR']
os.makedirs(session_dir, exist_ok=True)

def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    try:
        if not filename:
            return False
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    except (AttributeError, IndexError):
        # Handle edge cases like None or other non-string inputs
        return False

def preprocess_text(text):
    """Clean up and normalize text from PDF"""
    # Remove hyphenation (common in PDFs for word breaks)
    text = re.sub(r'-\s*\n\s*', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Strip extra spaces
    text = text.strip()
    return text

def count_word_occurrences(text, search_word):
    """Count occurrences of a word in text, handling word boundaries properly"""
    # If search_word is empty, return 0
    if not search_word:
        return 0
        
    # Case insensitive search with word boundaries
    pattern = r'\b' + re.escape(search_word) + r'\b'
    matches = re.finditer(pattern, text, re.IGNORECASE)
    return sum(1 for _ in matches)

def extract_text_by_page(pdf_path):
    """Extract text from each page of the PDF separately"""
    try:
        # Use custom parameters for pdfminer to better handle text extraction
        laparams = LAParams(
            char_margin=1.0,
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=0.5,
            detect_vertical=True
        )
        
        pages_text = []
        resource_manager = PDFResourceManager()
        
        with open(pdf_path, 'rb') as file:
            for page_num, page in enumerate(PDFPage.get_pages(file)):
                output_string = StringIO()
                converter = TextConverter(resource_manager, output_string, laparams=laparams)
                interpreter = PDFPageInterpreter(resource_manager, converter)
                interpreter.process_page(page)
                
                page_text = output_string.getvalue()
                pages_text.append(page_text)
                
                converter.close()
                output_string.close()
                
        return pages_text
    except Exception as e:
        print(f"Error extracting text by page: {e}")
        # Return an empty list for graceful handling
        return []

def process_pdf(pdf_path, search_word):
    """Process the PDF and build our data structure"""
    # Data structure: list of tuples (page_number, preview_words, word_count)
    pdf_data = []
    total_count = 0
    
    # Handle case where file doesn't exist
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return pdf_data, total_count
    
    # Extract text from each page
    pages_text = extract_text_by_page(pdf_path)
    
    # If no pages were extracted, return empty results
    if not pages_text:
        return pdf_data, total_count
    
    for i, raw_text in enumerate(pages_text):
        page_number = i + 1
        
        # Preprocess the text to handle common PDF issues
        processed_text = preprocess_text(raw_text)
        
        # Get all words properly
        all_words = re.findall(r'\b\w+\b', processed_text)
        
        # Get preview text (first few words)
        preview = ' '.join(all_words[:7]) if all_words else "(No text on page)"
        
        # Count occurrences of the search word
        word_count = count_word_occurrences(processed_text, search_word)
        
        pdf_data.append((page_number, preview, word_count, processed_text))
        total_count += word_count
    
    return pdf_data, total_count

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'pdfFile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['pdfFile']
        search_word = request.form.get('searchWord', '').strip()
        
        # If user does not select file or word, redirect
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not search_word:
            flash('No search word provided')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Create a unique filename to avoid collisions
            unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            filepath = os.path.join(uploads_dir, unique_filename)
            
            print(f"Saving file to: {filepath}")
            try:
                file.save(filepath)
            except Exception as e:
                print(f"Error saving file: {e}")
                flash('Error saving the file. Please try again.')
                return redirect(request.url)
            
            if not os.path.exists(filepath):
                print(f"ERROR: File was not saved properly at {filepath}")
                flash('Error saving the file. Please try again.')
                return redirect(request.url)
            
            # Process the PDF
            try:
                print(f"Processing PDF: {filepath}")
                pdf_data, total_count = process_pdf(filepath, search_word)
                
                print(f"PDF processed. Total count: {total_count}, Pages: {len(pdf_data)}")
                
                # Get the show sample text preference
                show_sample = 'showSample' in request.form
                
                # Store results in session for the results page
                session['pdf_results'] = {
                    'filepath': filepath,
                    'search_word': search_word,
                    'pdf_data': [(page_num, preview, count) for page_num, preview, count, _ in pdf_data],
                    'total_count': total_count,
                    'show_sample': show_sample
                }
                
                # Ensure session is saved
                session.modified = True
                
                return redirect(url_for('results'))
            except Exception as e:
                import traceback
                print(f"Error processing PDF: {str(e)}")
                print(traceback.format_exc())
                flash(f'Error processing PDF: {str(e)}')
                return redirect(request.url)
        else:
            flash('Only PDF files are allowed')
            return redirect(request.url)
    
    return render_template('index.html')

@app.route('/results')
def results():
    # Get results from session
    results = session.get('pdf_results', None)
    print(f"Session keys: {list(session.keys())}")
    
    if not results:
        print("No pdf_results found in session")
        flash('No results to display. Please upload a PDF first.')
        return redirect(url_for('index'))
    
    try:
        # Check if required keys exist in the results dictionary
        required_keys = ['search_word', 'pdf_data', 'total_count']
        for key in required_keys:
            if key not in results:
                print(f"Missing required key in results: {key}")
                flash('Incomplete results data. Please try again.')
                return redirect(url_for('index'))
                
        print(f"Results found. Search word: {results['search_word']}, Total count: {results['total_count']}")
        
        # Filter to only show pages with occurrences
        pdf_data = results['pdf_data']
        print(f"PDF data entries: {len(pdf_data)}")
        
        # Make sure the data structure is correct
        pages_with_occurrences = []
        try:
            # Try to filter for pages with occurrences > 0
            for entry in pdf_data:
                if len(entry) != 3:
                    raise ValueError("Invalid data structure: entry should have 3 elements")
                page_num, preview, count = entry
                # Ensure count is an integer
                if not isinstance(count, int):
                    count = 0  # Handle non-integer count values gracefully
                if count > 0:
                    pages_with_occurrences.append((page_num, preview, count))
        except (ValueError, TypeError) as e:
            print(f"Error in data structure: {e}")
            flash('Error processing results. Please try again.')
            return redirect(url_for('index'))
            
        print(f"Pages with occurrences: {len(pages_with_occurrences)}")
        
        # If we have data but no occurrences, handle that case
        if len(pages_with_occurrences) == 0 and results['total_count'] == 0:
            print("No occurrences found in the document")
            
        return render_template(
            'results.html', 
            search_word=results['search_word'],
            pages=pages_with_occurrences,
            total_count=results['total_count'],
            pages_count=len(pages_with_occurrences),
            show_sample=results.get('show_sample', True)
        )
    except Exception as e:
        import traceback
        print(f"Error in results route: {str(e)}")
        print(traceback.format_exc())
        flash('Error displaying results. Please try again.')
        return redirect(url_for('index'))

@app.route('/view_page/<int:page_num>')
def view_page(page_num):
    results = session.get('pdf_results', None)
    if not results:
        flash('Session expired. Please upload the PDF again.')
        return redirect(url_for('index'))
    
    # We need to reload the PDF to get the full text content
    filepath = results['filepath']
    search_word = results['search_word']
    
    # Reprocess to get the full text content
    pdf_data, _ = process_pdf(filepath, search_word)
    
    # Validate page number
    if page_num < 1 or page_num > len(pdf_data):
        flash(f'Invalid page number: {page_num}')
        return redirect(url_for('results'))
    
    # Get the page data (zero-indexed)
    page_data = pdf_data[page_num - 1]
    
    return render_template(
        'page_view.html',
        page_num=page_num,
        search_word=search_word,
        word_count=page_data[2],
        full_text=page_data[3]
    )

@app.route('/new_search')
def new_search():
    # Clear the session data
    if 'pdf_results' in session:
        # Delete the uploaded file
        try:
            filepath = session['pdf_results']['filepath']
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        # Remove from session
        session.pop('pdf_results', None)
    
    return redirect(url_for('index'))

# Clean up temporary files when the app shuts down
@app.teardown_appcontext
def cleanup_temp_files(exception=None):
    """Clean up any temporary files in the upload folder"""
    upload_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_folder):
        try:
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        except Exception as e:
            print(f"Error cleaning up upload folder: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
