import PyPDF2
import os

def get_pdf_path():
    while True:
        path = input("Enter the path to the PDF file: ").strip()
        if os.path.isfile(path) and path.lower().endswith('.pdf'):
            return path
        print("Invalid file. Please enter a valid PDF file path.")

def get_search_word():
    word = input("Enter the word to search for: ").strip()
    return word

def count_word_in_pdf(pdf_path, search_word, preview_words=7):
    counts = []
    previews = []
    total = 0
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            count = text.lower().count(search_word.lower())
            counts.append(count)
            # Get the first few words as a preview
            words = text.strip().split()
            preview = ' '.join(words[:preview_words])
            previews.append(preview)
            total += count
    return counts, previews, total

def main():
    print("PDF Word Counter\n------------------")
    pdf_path = get_pdf_path()
    search_word = get_search_word()
    counts, previews, total = count_word_in_pdf(pdf_path, search_word)
    print(f"\nResults for word: '{search_word}'\n")
    for i, (count, preview) in enumerate(zip(counts, previews), 1):
        print(f"Page {i}: {count} occurrence(s) | Preview: {preview}")
    print(f"\nTotal occurrences in document: {total}")

if __name__ == "__main__":
    main()
