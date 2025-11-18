# Team Green Fall CS480 Final Project
Maaz, Andrew, and Elliot's implementation for the Fall 2025 CS480 Final Project.

### Project Summary
This project reads PDF files from a predetermined corpus and converts the text in to embeddings. Then it uses these embeddings to prompt an LLM front-end to respond to user 
queries based on the embeddings given.

## Document Preparation
- First we convert pdf files in to txt files (via pdfminer.six).
- Then we chunk the large, raw text in to fixed sized chunks.
- After converting all the PDFs into chunks, we then use an exisiting embedding model from HuggingFace to convert chunks to embeddings.

EX from TA Demo:
```
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 384-dim
emb_matrix = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
```

## Create Vector Database
- We store the newly created embdeddings into a FAISS vector database, in memory.
- We use these embeddings to build a flat index, as well as an HSNW index.

## Query the LLM
- We accept a user query via command line and convert it in to an embedding. We then use our vectorDB index to find the top K most relevant chunks. We have chosen our default K to be 5, after some testing.
- We inject these fetched embeddings in to the LLM prompt alongside the original user query.
- Instruct LLM to answer the users query using these embeddings.

## Database Application
- Wrap the Ollama LLM in a full app with a basic GUI, supporting user sign up and log in.
- Implement CRUD operations on our relational database component.

# Project Checklist
| Project Step               | Status | Location          |
|----------------------------|:------:|-------------------|
| Document Preparation       |   <ul><li>- [x] </li></ul> | pdf_helper.py     |
| Vector Database            |   <ul><li>- [x] </li></ul>| answer_queries.py |
| Query Large Language Model |   <ul><li>- [x] </li></ul> | answer_queries.py |
| Database Application       | <ul><li>- [ ] </li></ul>   |                   |

# Deliverables
1. Text Chunking
- pdf_helper.py line 65: chunk_processed_txt
- Run `python pdf_helper.py` to create chunks directly. Or run `python answer_queries.py` which will also call it.
2. Chunk to Embedding
- answer_queries.py starting at line 56
- After we build our list of chunks, we encode our list with an existing embedding model `all-MiniLM-L6-v2`.
- model.encode returns a tuple of (chunk count, embedding dimensions), we use the dimensions to build our FAISS index with cosine similarity approximation.
3. Vector Storage:
- answer_queries.py line 59: This is where we build our flat index.
- This index is used in `search` starting on line 64 in answer_queries.py to fetch the top K nearest neighbors to the query embedding.

# Set Up Instructions
Project Set Up
1. `git clone git@github.com:UIC-CS480-Fall2025/team-green.git` via SSH
2. `cd team-green`
3. `python3 -m venv ./venv`
4. `source ./venv/bin/activate`
5. `pip install -r requirements.txt`
   
Ollama Set Up:
1. `curl -fsSL https://ollama.com/install.sh | sh`
2. `ollama --version`
3. `ollama pull llama3`

Run `python answer_queries.py` in your terminal. Note that embedding performance is significantly better on machines with CUDA installed.
