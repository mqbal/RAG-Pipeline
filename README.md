# Team Green Fall CS480 Final Project
Maaz, Andrew, and Elliot's implementation for the Fall 2025 CS480 Final Project.

### Project Summary
This project provides a Command Line Interface (CLI) to interface with a PostgreSQL database to provide User interaction with a predetermined corpus of PDF files. These PDF files chosen by a Curator to be processed into vector embeddings. Then it uses these embeddings to prompt an LLM front-end to respond to user queries based on the embeddings given.

## Main CLI
- Main Menu prompts the user to login in to their appropriate User Type, or to create a new EndUser. Login choices are Admin, Curator, and EndUser.
- The user will be prompted for their credentials to log into the database based on the User Type.
- Admins can do CRUD operations on Users.
- Curators can do CRUD operations on Documents.
- Users can only perform queries on the vector embeddings and are given a response from an LLM front-end.

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
- We store the newly created embdeddings into a PostgreSQL pgvector database.
- We use these embeddings to build an HSNW index.

## Query the LLM
- We accept a user query via command line and convert it in to an embedding. We then use our vectorDB index to find the top K most relevant results. We have chosen our default K to be 5, after some testing.
- We inject these fetched embeddings in to the LLM prompt alongside the original user query.
- Instruct LLM to answer the users query using these embeddings.

## Database Application
- Wrap the Ollama LLM in a full app with a basic CLI, supporting user sign up and log in.
- Implement CRUD operations on our relational database component.

# Project Checklist
| Project Step               | Status | Location          |
|----------------------------|:------:|-------------------|
| Document Preparation       |   <ul><li>- [x] </li></ul> | pdf_helper.py          |
| Vector Database Schema     |   <ul><li>- [x] </li></ul> | CS480_FinalProject.sql |
| Query Large Language Model |   <ul><li>- [x] </li></ul> | answer_queries.py      |
| Database Application       |   <ul><li>- [X] </li></ul  | database_helper.py     |

# Deliverables
1. Text Chunking
- pdf_helper.py line 65: chunk_processed_txt
- Run `python pdf_helper.py` to create chunks directly. Or run `python answer_queries.py` which will also call it.
2. Chunk to Embedding
- answer_queries.py starting at line 56
- After we build our list of chunks, we encode our list with an existing embedding model `all-MiniLM-L6-v2`.
- model.encode returns a tuple of (chunk count, embedding dimensions), we use the dimensions to build our FAISS index with cosine similarity approximation.
3. Vector Storage:
- answer_queries.py line 59: This is where we build our HNSW index.
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

Run `python main.py` in your terminal. Note that embedding performance is significantly better on machines with CUDA installed.


# Sample Program Run
```
What would you like to know about? Answer with "X" or nothing to exit.
->What is illinois doing to improve its waste management?

Top matches:
[1] score=0.642
Environmental Protection, 2015 Statewide Waste Characterization Study. http://www.ct.gov/deep/lib/deep/waste_management_and_disposal/Solid_Waste_Manageme nt_Plan/CMMS_Final_2015_MSW_Characterization_S...
---
[2] score=0.642
and Economic Opportunity/Illinois Recycling Association, Illinois Commodity/Waste Generation and Characterization Study, 2009. http://www.illinoisrecycles.org/pdffiles/ICWCGSReport052209.pdf • Georgia...
---
[3] score=0.638
Department of Commerce and Economic Opportunity, Illinois and Illinois Recycling Association. Illinois Commodity/Waste Generation and Characterization Study Update 2015. https://www.illinois.gov/dceo/...
---
[4] score=0.633
2013 Statewide Waste Characterization 42 Results 42 Table 3-3: Illinois 2008 Compared to 2015 Statewide Waste Characterization Results 44 Table...
---
[5] score=0.631
comparison with a 2008 statewide study. TABLE 3-3: ILLINOIS 2008 COMPARED TO 2015 STATEWIDE WASTE CHARACTERIZATION RESULTS 2008 26% 14.4%...
---



Thinking...



Based on the provided context, it appears that Illinois has been actively working to improve its waste management through various studies and initiatives.

One such initiative is the annual statewide waste characterization study, which provides valuable data on the types and amounts of waste generated in Illinois. The 2015 study, for example, found that Illinois residents generated approximately 22 million tons of municipal solid waste (MSW) in 2014, with a significant portion being recyclable materials.

The state has also been working to increase recycling rates through education and outreach efforts, as well as by implementing programs to encourage businesses and households to recycle more effectively. For example, the Illinois Recycling Association offers educational resources and technical assistance to help individuals and organizations implement effective recycling programs.

In addition, the state has been exploring innovative technologies and strategies for managing waste, such as anaerobic digestion and gasification, which can help reduce greenhouse gas emissions and minimize the environmental impacts of waste disposal.

Furthermore, the 2015 Statewide Waste Characterization Study suggests that Illinois is making progress in reducing its waste generation rates. For example, compared to the 2008 study, the 2015 study found that the state's MSW generation rate decreased by approximately 14% (from 26% to 12%).

Overall, it appears that Illinois is actively working to improve its waste management through a combination of education, outreach, and innovative technologies.



What would you like to know about? Answer with "X" or nothing to exit.
->X
```