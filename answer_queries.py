# general utiliies
import os, glob, dotenv, time
import psycopg2
from pgvector.psycopg2 import register_vector
import pdf_helper   # helper module that processes initial Corpus
from sentence_transformers import SentenceTransformer # for text -> vector embedding
import subprocess    # detect at runtime if we have cuda installed
import ollama

dotenv.load_dotenv()

FETCH_K = int(os.environ.get("FETCH_K", 5))

conn = psycopg2.connect(database="postgres",
        host="localhost",
        user="postgres",
        password="postgres",
        port="5432",
        options="-c search_path=cs480_finalproject,public")
register_vector(conn)

chunks = []           # list[str]
dimension = None      # embedding dimension

# use CLI function to figure out if the computer has CUDA installed
def has_cuda():
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

print("Loading SentenceTransformer model...")

# detect at runtime if user has cuda installed, if so, use it
transform_device = "cuda" if has_cuda() else "cpu"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=transform_device)


def embed_and_index_chunks():
    global chunks, model, dimension

    print("Embedding chunks...")
    start = time.time()
    embed_chunks = [tup[0] for tup in chunks]
    embeddings = model.encode(
        embed_chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    dimension = embeddings.shape[1]

    print(f"Model loaded. Embedding dimension = {dimension}")
    
    # Insert embeddings into psql database
    # TODO: make sure table format matches
    cur = conn.cursor()
    for (chunk_text, doc_id), embedding in zip(chunks, embeddings):
        insert_query = """
        INSERT INTO cs480_finalproject.embeddings (source_doc_id, chunk, embedding)
        VALUES (%s, %s, %s)
        """
        cur.execute(insert_query, (doc_id, chunk_text, embedding.tolist()))
    conn.commit()

    # Create an HNSW index for searching
    create = """CREATE INDEX IF NOT EXISTS hnsw_index ON cs480_finalproject.embeddings USING hnsw (embedding cs480_finalproject.vector_cosine_ops);"""
    cur.execute(create)
    conn.commit()
    cur.close()

    print(f"Embedding & indexing complete. Took {time.time() - start:.2f} seconds")

# this should run after every time that 
def update_all_chunks():
    global chunks

    chunks = []

    with conn.cursor() as cur:
        # Get all documents and their IDs from the DB
        cur.execute("""
            SELECT doc_id, source
            FROM cs480_finalproject.document;
        """)
        docs = cur.fetchall()

    if not docs:
        print("No documents found in the database.")
        return

    for doc_id, source in docs:
        # each source pdf should have had its text extracted and chunked, find the path for that chunked file
        base_name = os.path.splitext(os.path.basename(source))[0]   # remove .pdf
        txt_path = os.path.join(pdf_helper.CHUNKS_OUTPUT_DIRECTORY, base_name + ".txt")

        # for some reason, it wasn't already extracted and chunked, do it now
        if not os.path.exists(txt_path):
            print(f"Chunked text not found for {source} — regenerating.")
            pdf_helper.process_pdf_to_txt()       # regenerate corpus
            pdf_helper.chunk_processed_txt()      # re-chunk
            # after regeneration, check again
            if not os.path.exists(txt_path):
                print(f"Still missing chunks for {source}, skipping.")
                continue

        # Load chunks from the file
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    chunks.append((line, doc_id))

    print(f"Loaded {len(chunks)} chunks.")

# OUTDATED
# def update_all_chunks():
#     global chunks

#     check_files = glob.glob(os.path.join(pdf_helper.CHUNKS_OUTPUT_DIRECTORY, "*.txt"))
#     if not check_files:
#         print("Chunked texts not found — regenerating.")
#         pdf_helper.process_pdf_to_txt()
#         pdf_helper.chunk_processed_txt()
#         print("Chunking complete.")

#     chunk_files = glob.glob(os.path.join(pdf_helper.CHUNKS_OUTPUT_DIRECTORY, "*.txt"))

#     chunks = []
#     for txt_path in chunk_files:
#         base_name = os.path.basename(txt_path)              # removes the prefix path
#         name_without_ext = os.path.splitext(base_name)[0]   # remove the .txt
#         name_without_ext += ".pdf"                          # replace with .pdf
        
#         with conn.cursor() as cur:
#             doc_id_query = """
#                 SELECT doc_id
#                 FROM cs480_finalproject.document
#                 WHERE source = %s;
#             """

#             cur.execute(doc_id_query, (name_without_ext,))
#             result = cur.fetchone()
#             assert(result is not None)
#             doc_id = result[0]
            
#         with open(txt_path, "r", encoding="utf-8") as f:
#             for line in f:
#                 line = line.strip()
#                 if line:
#                     chunks.append((line, doc_id))

#     print(f"Loaded {len(chunks)} chunks.")

def init_rag():
    """
    Call this once in any external script.
    """
    update_all_chunks()
    embed_and_index_chunks()

    print("RAG system initialized.")

# take a pdf, extract it, chunk it, embed it, and add it index (last portion handled internally by HNSW)
def add_document_to_index(pdf_path):
    # pdf_path is a source that should already exist in the DB Document table
    with conn.cursor() as cur:
        doc_id_query = """
            SELECT doc_id
            FROM cs480_finalproject.document
            WHERE source = %s;
        """
        cur.execute(doc_id_query, (pdf_path,))
        result = cur.fetchone()
        new_doc_id = result[0]   # guaranteed to exist

    global model
    _ = pdf_helper.extract_pdf(pdf_path)

    # extract out the text from the pdf and chunk it
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    chunked_path = pdf_helper.CHUNKS_OUTPUT_DIRECTORY + "/" + base_name + ".txt"
    txt_path = pdf_helper.TXT_OUTPUT_DIRECTORY + "/" + base_name + ".txt"
    with open(txt_path, "r", encoding="utf-8") as r:
        text = r.read()
    
        text = pdf_helper.normalize(text) # strips repetitive whitespace
    
    # write the chunks to a Chunked_txt directory
    chunked = pdf_helper.chunk_text(text, pdf_helper.CHUNK_WORD_COUNT, pdf_helper.OVERLAP)
    with open(chunked_path, "x", encoding="utf-8") as f:
        for chunk in chunked:
            f.write(chunk + "\n")
    
    embeddings = model.encode(
        chunked,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    cur = conn.cursor()
    for chunk_text, embedding in zip(chunked, embeddings):
        insert_query = """
        INSERT INTO cs480_finalproject.embeddings (source_doc_id, chunk, embedding)
        VALUES (%s, %s, %s)
        """
        cur.execute(insert_query, (new_doc_id, chunk_text, embedding.tolist()))
    
    # after processing, set "processed" to true
    process_doc_query = """
        UPDATE cs480_finalproject.document
        SET processed = TRUE
        WHERE source = %s
        RETURNING doc_id;
    """
    cur.execute(process_doc_query, (pdf_path,))
    
    conn.commit()


# turn query text in to an embedding, then search our index
def search(query, k=FETCH_K):
    global model

    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
    
    # Search nearest neighbors
    cur = conn.cursor()
    # TODO: check query
    search_query = """SELECT embed_id, chunk, embedding <=> %s::cs480_finalproject.vector AS distance
        FROM cs480_finalproject.embeddings
        ORDER BY distance
        LIMIT %s;
        """
    cur.execute(search_query, (q_emb.tolist(), k))

    results = cur.fetchall()
    print(results)
    cur.close()

    top_k = []
    # make ranking start at 1 instead of 0
    for rank, item in enumerate(results[:k], start=1):
        top_k.append({
            "rank": rank,
            "score": item[2],
            "chunk": item[1]
        })

    return top_k

def queryDB(enduser_id):
    query = input("What would you like to know about? Answer with \"X\" or nothing to exit.\n->")
    while query and query != "X":
        # intentional query made, log it
        with conn.cursor() as cur:
            querylog_insert = """INSERT INTO QueryLog (query_text, issuer_id)
            VALUES (%s, %s)
            """
            cur.execute(querylog_insert, (query, enduser_id))
            conn.commit()

        hits = search(query, k=FETCH_K)

        print("\nTop matches:")
        for h in hits:
            print(f"[{h['rank']}] score={h['score']:.3f}\n{h['chunk'][:200]}...\n---")
        print("\n\n")

        print("Thinking...")    
        # Construct a RAG-style prompt by injecting the retrieved hits
        context = "\n".join([hit['chunk'] for hit in hits])
        prompt = f"Answer the following question grounded on, but not absolutely limited to, the provided context.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        # Query the local Ollama endpoint
        response = ollama.chat(
            model="llama3",   # replace with the model you have locally
            messages=[
                {"role": "system", "content": "You are a domain expert assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        print("\n\n")
        print(response["message"]["content"])
        print("\n\n")
        query = input("What would you like to know about? Answer with \"X\" or nothing to exit.\n->")
    print("Returning to role selection...")

if __name__ == "__main__":
    init_rag()
    queryDB()
