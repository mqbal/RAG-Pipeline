import pdfminer # pip install pdfminer.six
import os
import glob

def process_pdfs():
    project_root = os.path.abspath(os.path.dirname(__file__))  # Repo root
    data_corpus = os.path.join(project_root, "Corpus")

    pdf_files = glob.glob(os.path.join(data_corpus, "*.pdf"))

    for pdf_path in pdf_files:
        try:
            text = pdfminer.high_level.extract_text(pdf_path)
            # TODO: Chunk the text and have overlap
            print(f"--- Text from {os.path.basename(pdf_path)} ---")
            print(text[:500])  # Print first 500 characters for brevity
            print("\n")
        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")