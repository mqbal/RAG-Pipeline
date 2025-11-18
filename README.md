# Team Green Fall CS480 Final Project
Maaz, Andrew, and Elliot's implementation for the Fall 2025 CS480 Final Project.

### Project Summary
This project reads PDF files from a predetermined document corpus, converts their text in to embeddings. Then it uses these embeddings to prompt an LLM front-end to respond to user 
queries, solely from the embedding given.

## Document Preparation
- First we chunk the raw text from each PDF with overlap (via pdfminer.six).
- After converting all the PDFs into chunks, we then use an exisiting embedder like SentenceTransformer to convert the chunks into embeddings.

EX from TA Demo:
```
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 384-dim
emb_matrix = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
```

## Create Vector Database
- Store embdeddings we have generated using SentenceTransformer into a FAISS vector database.
- Use embeddings to create a brute force index (options are HNSW, KD tree, clustering, etc). Need to use two indexes.

## Query the LLM
- Take a user question in command line and give it to the Ollama LLM endpoint.
- Use our vector database index to find top K most relevant vectors. We have chosen K to be 5, after some testing.
- Instruct LLM to answer the users query using these embeddings.

## Application Frontend
- Wrap the Ollama LLM in a full app with a basic GUI, supporting user sign up and log in.

# Project Checklist
| Project Step               | Status | File              |
|----------------------------|:------:|-------------------|
| Document Preparation       |   <ul><li>- [x] </li></ul> | pdf_helper.py     |
| Vector Database            |   <ul><li>- [x] </li></ul>| answer_queries.py |
| Query Large Language Model |   <ul><li>- [x] </li></ul> | answer_queries.py |
| Application Frontend       | <ul><li>- [ ] </li></ul>   |                   |

# Set Up Instructions
Project Set Up
1. `git clone repo`
2. `cd team-green`
3. `python3 -m venv ./venv`
4. `source ./venv/bin/activate`
5. `pip install -r requirements.txt`
   
Ollama Set Up:
1. `curl -fsSL https://ollama.com/install.sh | sh`
2. `ollama --version`
3. `ollama pull llama3`

Run `python answer_queries.py` in your terminal
