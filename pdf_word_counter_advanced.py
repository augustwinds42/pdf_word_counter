import os
import re
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

def get_pdf_path():
    while True:
        path = input("Enter the path to the PDF file: ").strip()
        if os.path.isfile(path) and path.lower().endswith('.pdf'):
            return path
        print("Invalid file. Please enter a valid PDF file path.")

def get_search_word():
    word = input("Enter the word to search for: ").strip()
    return word

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using pdfminer.six with advanced layout parameters
    to better preserve word integrity
    """
    # Configure layout parameters for better text extraction
    laparams = LAParams(
        char_margin=1.0,      # Increase char margin to prevent splitting words
        line_margin=0.5,      # Adjust line margin for better line detection
        word_margin=0.1,      # Reduce word margin to keep words together
        boxes_flow=0.5,       # Adjust text flow detection
        detect_vertical=True  # Handle vertical text
    )
    
    try:
        # Extract text from the entire PDF
        full_text = extract_text(pdf_path, laparams=laparams)
        return full_text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_text_by_page(pdf_path):
    """
    Extract text from each page of the PDF separately
    """
    try:
        # Use custom parameters for pdfminer to better handle text extraction
        laparams = LAParams(
            char_margin=1.0,
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=0.5,
            detect_vertical=True
        )
        
        # Extract text page by page
        from pdfminer.pdfpage import PDFPage
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.converter import TextConverter
        from io import StringIO
        
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
        return []

def preprocess_text(text):
    """
    Clean up and normalize text from PDF
    """
    # Remove hyphenation (common in PDFs for word breaks)
    text = re.sub(r'-\s*\n\s*', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip extra spaces
    text = text.strip()
    
    return text

def count_word_occurrences(text, search_word):
    """
    Count occurrences of a word in text, handling word boundaries properly
    """
    # Case insensitive search with word boundaries
    pattern = r'\b' + re.escape(search_word) + r'\b'
    matches = re.finditer(pattern, text, re.IGNORECASE)
    return sum(1 for _ in matches)

def process_pdf(pdf_path, search_word):
    """
    Process the PDF and build our data structure
    """
    # Data structure: list of tuples (page_number, all_words, word_count)
    pdf_data = []
    total_count = 0
    
    # Extract text from each page
    pages_text = extract_text_by_page(pdf_path)
    
    for i, raw_text in enumerate(pages_text):
        page_number = i + 1
        
        # Preprocess the text to handle common PDF issues
        processed_text = preprocess_text(raw_text)
        
        # Get all words properly
        all_words = re.findall(r'\b\w+\b', processed_text)
        
        # Count occurrences of the search word
        word_count = count_word_occurrences(processed_text, search_word)
        
        pdf_data.append((page_number, all_words, word_count))
        total_count += word_count
    
    return pdf_data, total_count

def display_results(pdf_data, search_word, total_count):
    """
    Display the results of the search
    """
    print(f"\nResults for word: '{search_word}'\n")
    
    pages_with_occurrences = 0
    for page_number, all_words, word_count in pdf_data:
        if word_count > 0:
            preview = ' '.join(all_words[:7]) if all_words else "(No text on page)"
            print(f"Page {page_number}: {word_count} occurrence(s) | Preview: {preview}")
            pages_with_occurrences += 1
    
    if pages_with_occurrences == 0:
        print("No occurrences found in any page.")
    else:
        print(f"\nFound occurrences on {pages_with_occurrences} pages.")
    
    print(f"Total occurrences in document: {total_count}")

def main():
    print("Advanced PDF Word Counter\n------------------------")
    print("This program uses advanced PDF text extraction to maintain word integrity.")
    
    pdf_path = get_pdf_path()
    search_word = get_search_word()
    
    print(f"\nProcessing PDF and searching for '{search_word}'...")
    pdf_data, total_count = process_pdf(pdf_path, search_word)
    display_results(pdf_data, search_word, total_count)
    
    # Interactive exploration
    while True:
        choice = input("\nWould you like to see the full text of a specific page? (y/n): ").lower()
        if choice != 'y':
            break
            
        try:
            page_num = int(input("Enter page number: "))
            if 1 <= page_num <= len(pdf_data):
                page_data = pdf_data[page_num - 1]
                print(f"\nPage {page_data[0]} - Word count for '{search_word}': {page_data[2]}")
                print("\nFull text (after processing):")
                print(" ".join(page_data[1]))
            else:
                print(f"Page number must be between 1 and {len(pdf_data)}")
        except ValueError:
            print("Please enter a valid number")

if __name__ == "__main__":
    main()
