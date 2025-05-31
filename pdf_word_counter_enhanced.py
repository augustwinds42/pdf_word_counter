import PyPDF2
import os
import re

def get_pdf_path():
    while True:
        path = input("Enter the path to the PDF file: ").strip()
        if os.path.isfile(path) and path.lower().endswith('.pdf'):
            return path
        print("Invalid file. Please enter a valid PDF file path.")

def get_search_word():
    word = input("Enter the word to search for: ").strip()
    return word

def preprocess_text(text):
    """
    Preprocess PDF text to handle common issues like hyphenation and line breaks
    """
    # Replace hyphens followed by line breaks (common in PDFs for word breaks)
    text = re.sub(r'-\s+', '', text)
    # Replace various types of whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
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
    # Data structure: list of tuples (page_number, all_words, word_count)
    pdf_data = []
    total_count = 0
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            page_number = i + 1
            raw_text = page.extract_text() or ""
            
            # Preprocess text to handle word breaks
            processed_text = preprocess_text(raw_text)
            
            # Get all words properly split
            all_words = re.findall(r'\b\w+\b', processed_text)
            
            # Count occurrences of the search word
            word_count = count_word_occurrences(processed_text, search_word)
            
            pdf_data.append((page_number, all_words, word_count))
            total_count += word_count
            
    return pdf_data, total_count

def display_results(pdf_data, search_word, total_count):
    print(f"\nResults for word: '{search_word}'\n")
    
    for page_number, all_words, word_count in pdf_data:
        preview = ' '.join(all_words[:7]) if all_words else "(No text on page)"
        print(f"Page {page_number}: {word_count} occurrence(s) | Preview: {preview}")
        
    print(f"\nTotal occurrences in document: {total_count}")
    
    # Add information about the word processing
    if total_count > 0:
        print("\nNote: Text has been preprocessed to handle hyphenation and word breaks.") 
        print("      Words that may appear split in the PDF are properly counted.")

def main():
    print("Enhanced PDF Word Counter\n------------------------")
    print("This program counts word occurrences in PDFs, handling hyphenation and word breaks.")
    
    pdf_path = get_pdf_path()
    search_word = get_search_word()
    
    print(f"\nProcessing PDF and searching for '{search_word}'...")
    pdf_data, total_count = process_pdf(pdf_path, search_word)
    display_results(pdf_data, search_word, total_count)
    
    # Optional: Demonstrate accessing the data structure
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
