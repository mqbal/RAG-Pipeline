This is Team Green (Maaz, Andrew, Elliot)'s implementation for the Fall 2025 CS480 Final Project.

This project reads PDF files from a predetermined document corpus, converts their text in to embeddings. Then it uses these embeddings to prompt an LLM front-end to respond to user 
queries, solely from the embedding given.

Part A: Document Ingestion
1. Chunk each PDF in to chunks with overlap (via pdfminer.six)
2. Convert chunk in to embedding. Use exisiting embedder like SentenceTransformer.

EX from TA Demo:
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 384-dim
emb_matrix = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)

Part B: Make VectorDB
3. Store embdeddings from step 2 in a vector database: FAISS, Lucene, pgvector are some choices. Pgvector is probably good because we are using PostgreSQL for our Relational Database System.
4. Use embeddings to create a brute force index (options are HNSW, KD tree, clustering, etc). Need to use two indexes.

Part C: Answer machine
5. Take a user question in command line and give it to an LLM with Ollama.
6. Use our vectorDB index to find top K most relevant vectors. Instruct LLM to answer using these embeddings.

Part D: Database Application
7. Wrap Part C in a full app with a GUI. Support user sign up and log in.

