# general utiliies
import os, glob, dotenv, time
dotenv.load_dotenv()

FETCH_K = int(os.environ.get("FETCH_K", 5))

import pdf_helper   # helper module that processes initial Corpus

# for converting chunks in to embeddings, and then storing them
import numpy as np
from sentence_transformers import SentenceTransformer # for text -> vector embedding
import faiss # an example of a vector DB (currently stores in the memory)
import subprocess    # detect at runtime if we have cuda installed
# import torch
# print(torch.cuda.is_available())
# print(torch.version.cuda)
# exit()


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

import ollama

if __name__ == "__main__":
    check_files = glob.glob(os.path.join(pdf_helper.CHUNKS_OUTPUT_DIRECTORY, "*.txt"))
    if not check_files:
        print("Chunked Texts not Found, Regenerating...")
        pdf_helper.process_pdf_to_txt()    # convert pdfs to txt files
        pdf_helper.chunk_processed_txt()   # create chunks from txt files
        print("Chunked Text Files DONE")

    # "CHUNKS_OUTPUT_DIRECTORY" has .txt files where each line of a file is a chunk 
    chunk_files = glob.glob(os.path.join(pdf_helper.CHUNKS_OUTPUT_DIRECTORY, "*.txt"))

    print("Starting Embedding Generation")
    embed_start = time.time()

    chunks = []

    # read each line of each file in "CHUNKS_OUTPUT_DIRECTORY" and collect it into "chunks"
    for txt_path in chunk_files:
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:                # skip empty lines
                    chunks.append(line)
    
    # TA demo code for converting chunks to embeddings and storing them in FAISS
    # detect at runtime if user has cuda installed, if so, use it
    transform_device = "cuda" if has_cuda() else "cpu"
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=transform_device)
    emb_matrix = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    dim = emb_matrix.shape[1]

    # faiss IndexFlatIP exact search
    index_flat_ip = faiss.IndexFlatIP(dim)  # cosine works with normalized vectors using inner product
    index_flat_ip.add(emb_matrix)           # store embeddings

    # faiss HNSW approximate search
    # 16 is the number of neighbors in the resulting graph
    # May also use values of 32 or 64. Higher values are more accurate but require more memory
    index_hnsw = faiss.IndexHNSWFlat(dim, 16)
    index_hnsw.add(emb_matrix)                # store embeddings
    print(f"Embed Total: {time.time() - embed_start}")

    # turn query text in to an embedding, then search our index
    def search(query, k=FETCH_K):
        q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)

        # Search both indexes
        scores_flat_ip, idxs_flat_ip = index_flat_ip.search(q_emb, k)  # (1, k)
        scores_hnsw, idxs_hnsw = index_hnsw.search(q_emb, k)

        # Results will be merged into a dict of dicts to avoid duplicate results
        results = {}
        # IndexFlatIP results saved first
        for rank, (i, s) in enumerate(zip(idxs_flat_ip[0], scores_flat_ip[0]), start=1):
            results[i] = {"score": float(s), "chunk": chunks[i]}
        
        # HNSW results will append to the dict if the chunk is new, else update the result with the average of both scores
        for rank, (i, s) in enumerate(zip(idxs_hnsw[0], scores_hnsw[0]), start=1):
            if i not in results:
                results[i] = {"score": float(s), "chunk": chunks[i]}
            else:
                results[i]["score"] = (results[i]["score"] + s) / 2     # Averaging of flat and HNSW scores for duplicate results
        
        results_sorted = sorted(
            ({"index": i, "score": d["score"], "chunk": d["chunk"]} for i, d in results.items()),
            key=lambda x: x["score"],
            reverse=True
        )

        # Trim to exactly k unique results and assign ranks
        top_k = []
        for rank, item in enumerate(results_sorted[:k], start=1):
            top_k.append({"rank": rank, "score": item["score"], "chunk": item["chunk"]})

        return top_k


    query = input("What would you like to know about? Answer with \"X\" or nothing to exit.\n->")
    while query and query != "X":
        # TODO: sanitize user input to prevent injection

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
