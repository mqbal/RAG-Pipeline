# Question Answer Machine
Answers user questions by fetching relevant text from a vector database to RAG a frontend LLM.

### Project Summary
This project provides a Command Line Interface (CLI) to interface with a PostgreSQL database to provide User Interaction with a predetermined corpus of PDF files. These PDF files are chosen by a Curator to be processed into vector embeddings. Then it uses these embeddings to prompt an LLM front-end to respond to user queries based on the embeddings given.

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

Code Excerpt:
```
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=transform_device)  # 384-dim
emb_matrix = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
```

## Create Vector Database
- We store the newly created embdeddings into a PostgreSQL pgvector database.
- We use these embeddings to build an HSNW index.

## Query the LLM
- We accept a question via command line and convert the string in to an embedding. We search our vectorDB index to find the top K most relevant text chunks. The default K is 5.
- Fetched embeddings areinjected in to the LLM prompt alongside the original user query.
- Instruct LLM to answer the user's question using these embeddings.

## Database Application
- Wraps the Ollama LLM in a full app with a basic CLI, supporting user sign up and log in.
- Implements CRUD operations on our relational database component.

# Directory Structure
├── RAG_Pipeline.sql          -- Defines the schema of both vector and relational database
├── Chunked_txt/              -- Directory of text chunks of each text file, speeds up vectorDB creation
├── Corpus/                   -- Directory of user's documents that the LLM will answer from
├── Processed_pdf/            -- Directory of plaintext files extracted from Corpus, skips redundant PDF extraction
├── README.md
├── answer_queries.py         -- Interacts with vector database to fetch relevant chunks
├── database_helper.py        -- Interacts with relational database for CRUD
├── main.py                   -- ENTRYPOINT: Defines a simple CLI menu for user's to navigate
├── pdf_helper.py             -- Helper function that processes PDFs in Corpus
└── requirements.txt          -- Necessary python imports

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
$ python main.py 
Loading SentenceTransformer model...

=== Login Selection Menu ===
1. Admin
2. Curator
3. EndUser
S. Sign Up as EndUser
X. Exit
===========================
Select an option: 3
Enter EndUser email: miqba4@uic.edu
Enter EndUser password:
Authenticating EndUser with email=miqba4@uic.edu...
Hello, Maaz you are successfully logged in as EndUser!

=== USER Menu ===
What would you like to know about? Answer with "X" or nothing to exit.
->Tell me about the future of Florida' waste management and environmental conservation efforts 
[(23428, 'strategic investments in waste management. By ensuring that Florida has the necessary infrastructure to support sustainable waste management, this study', 0.18808760678506742), (16660, 'strategic investments in waste management. By ensuring that Florida has the necessary infrastructure to support sustainable waste management, this study', 0.18808771478344655), (23425, 'it is a roadmap for the future of Florida’s waste and recycling infrastructure. The findings will inform state and local', 0.1998309254595909), (16657, 'it is a roadmap for the future of Florida’s waste and recycling infrastructure. The findings will inform state and local', 0.1998309254595909), (27396, "a vital component of Florida's waste management and recycling infrastructure. They support the state's sustainability goals by diverting large volumes", 0.2021973491369884)]

Top matches:
[1] score=0.188
strategic investments in waste management. By ensuring that Florida has the necessary infrastructure to support sustainable waste management, this study...
---
[2] score=0.188
strategic investments in waste management. By ensuring that Florida has the necessary infrastructure to support sustainable waste management, this study...
---
[3] score=0.200
it is a roadmap for the future of Florida’s waste and recycling infrastructure. The findings will inform state and local...
---
[4] score=0.200
it is a roadmap for the future of Florida’s waste and recycling infrastructure. The findings will inform state and local...
---
[5] score=0.202
a vital component of Florida's waste management and recycling infrastructure. They support the state's sustainability goals by diverting large volumes...
---


Thinking...


Based on the provided context, it appears that Florida is actively working to improve its waste management and recycling infrastructure to achieve sustainable development. Some potential trends or directions for the future of Florida's waste management and environmental conservation efforts could include:

1. Increased emphasis on circular economy principles: As Florida continues to develop its waste management infrastructure, there may be a greater focus on designing waste out of products and processes, reducing consumption, reusing materials whenever possible, and recycling as much as possible.

2. Expanded use of technology: With the advancement of technologies like artificial intelligence, blockchain, and the Internet of Things (IoT), it's likely that Florida will see more widespread adoption of innovative solutions to improve waste collection, processing, and disposal.

3. Greater emphasis on reducing waste generation: While recycling and proper disposal are essential, reducing waste at its source is also crucial for environmental conservation efforts in Florida. This could involve increasing education and outreach programs to encourage reduced consumption and single-use plastics reduction.

4. Collaboration between state, local governments, and private sector: The provided context highlights the importance of state and local government collaboration in informing future directions for Florida's waste management and recycling infrastructure. There may be increased partnerships with private companies, non-profit organizations, and community groups to leverage resources and expertise.

5. Integration of renewable energy and sustainable practices: As part of Florida's sustainability goals, there could be a greater focus on integrating renewable energy sources (e.g., solar, wind) into waste management facilities and infrastructure, as well as promoting sustainable practices throughout the state.

6. Improved public education and awareness: Effective waste management and environmental conservation require informed and engaged citizens. There may be increased efforts to educate Floridians about the importance of proper waste disposal, recycling, and sustainability, as well as encouraging community involvement in conservation initiatives.

These are just a few potential directions for the future of Florida's waste management and environmental conservation efforts.



What would you like to know about? Answer with "X" or nothing to exit.
->X
```