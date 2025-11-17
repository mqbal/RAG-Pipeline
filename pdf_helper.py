# general utilities
import re, time, os, glob, dotenv
dotenv.load_dotenv()

# extracting text from pdf
import pdfminer.high_level, pdfminer.layout, multiprocessing

# to suppress color gradient warnings from pdfminer.six since we only care about reading text
import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR) # only log errors, not warnings

# expose some useful global variables for project pathing
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))           # Repo root
CORPUS_PATH = os.path.join(PROJECT_ROOT, "Corpus")                  # Input directory
CHUNKS_OUTPUT_DIRECTORY = os.path.join(PROJECT_ROOT, "Chunked_txt") # Output directory for .txt files
TXT_OUTPUT_DIRECTORY = os.path.join(PROJECT_ROOT, "Processed_pdf")  # Output directory for .txt files

CHUNK_WORD_COUNT = int(os.environ.get("CHUNK_WORD_COUNT", 20))
OVERLAP = int(os.environ.get("OVERLAP", 10))
__THREAD_COUNT = int(os.environ.get("THREAD_COUNT", 4))

# Use regex to find repetitive whitespace and replace it with a singular space.
def normalize(s: str) -> str:
    """Collapse whitespace and trim."""
    return re.sub(r"\s+", " ", s).strip()

# Chunks the contents of 'text'
# TODO: Improve chunking to fit around paragraph and end of sentences, also filter out tables and garbage data.
def chunk_text(text: str, max_words: int, overlap: int):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+max_words]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        i += max_words - overlap # slides window
    return chunks

# helper function for multiprocessor pool
def extract_pdf(pdf_path):
    output_path = TXT_OUTPUT_DIRECTORY + "/" + os.path.basename(pdf_path).rstrip(".pdf") + ".txt"
    
    # Avoid extracting text if it already exists
    if not os.path.exists(output_path):
        try:
            # file size of "pdf_path" can be potentially huge, so stream data in to txt file
            with open(pdf_path, "rb") as infile, open(output_path, "x", encoding="utf-8") as outfile:
                pdfminer.high_level.extract_text_to_fp(infile, outfile, laparams=pdfminer.layout.LAParams(), output_type="text", codec="utf-8")
        except Exception as e:
            print(f"Failed to process {pdf_path}: {e}")

# Process Corpus pdf files into text files
def process_pdf_to_txt():
    print("  Starting PDF Extraction")
    pdf_files = glob.glob(os.path.join(CORPUS_PATH, "*.pdf"))
    time_start = time.time()
    pdf_files_sorted = sorted(pdf_files, key=os.path.getsize, reverse=True) # longest schedule first, greedy approximation
    with multiprocessing.Pool(processes=__THREAD_COUNT) as pool:
        pool.map(extract_pdf, pdf_files_sorted)
    print(f"    Extract Total: {time.time() - time_start}")

# Chunk processed text files into new text files with one chunking per line
def chunk_processed_txt():
    print("  Starting Text Chunking")
    txt_files = glob.glob(os.path.join(TXT_OUTPUT_DIRECTORY, "*.txt"))
    time_start = time.time()

    # for every text file in "Processed_pdf", chunk it of size determined by .env
    for txt_path in txt_files:
        output_path = CHUNKS_OUTPUT_DIRECTORY + "/" + os.path.basename(txt_path)

        if not os.path.exists(output_path):
            with open(txt_path, "r", encoding="utf-8") as r:
                text = r.read()
            
            text = normalize(text) # strips repetitive whitespace
            # chunk_text(text: str, max_words: int, overlap: int)
            chunked = chunk_text(text, CHUNK_WORD_COUNT, OVERLAP)
            with open(output_path, "x", encoding="utf-8") as f:
                for chunk in chunked:
                    f.write(chunk + "\n")
    print(f"    Chunk Total: {time.time() - time_start}")

if __name__ == "__main__":
    pdf_helper.process_pdf_to_txt()    # convert pdfs to txt files
    pdf_helper.chunk_processed_txt()   # create chunks from txt files