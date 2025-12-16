-- Note: DEFAULT CURRENT_TIMESTAMP means that it picks current time if no timestamp is provided.
-- If a timestamp is provided, In app, don't allow this.
 
CREATE SCHEMA CS480_FinalProject;
SET search_path TO CS480_FinalProject;
CREATE EXTENSION IF NOT EXISTS vector;
-- User Role has fixed options
CREATE TYPE user_role AS ENUM ('EndUser', 'Admin', 'Curator');

-- Users table (Users Entity)
CREATE TABLE Users (
    user_id     SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    role        user_role NOT NULL, -- Must be one of 'EndUser', 'Admin', or 'Curator'. Could check all three for a match but this is easier.
    username    VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(100) NOT NULL
);

-- EndUser table
CREATE TABLE EndUser (
    end_id INT PRIMARY KEY,
    latest_activity TIMESTAMP,  -- Could be NULL if no queries made yet
    FOREIGN KEY (end_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Admin table
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY,
    FOREIGN KEY (admin_id) REFERENCES Users(user_id)
);

-- Curator table 
CREATE TABLE Curator (
    curator_id INT PRIMARY KEY,
    FOREIGN KEY (curator_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Document table (Document Entity)
CREATE TABLE Document (
    doc_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(200) NOT NULL,
    source VARCHAR(200) NOT NULL,
    added_by INT NOT NULL,
    time_added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- When did it get added
    processed BOOLEAN,  -- Did it go through the Vector Pipeline, unsure if that corresponds to being queried.
    FOREIGN KEY (added_by) REFERENCES Curator(curator_id)
);

-- Adds table (One to Many Relationship between Curator and Document)
-- This table is technically not neccessary, as it offers no extra data.
CREATE TABLE Adds (
    curator_id INT NOT NULL,
    doc_id INT NOT NULL,
    PRIMARY KEY (curator_id, doc_id),
    FOREIGN KEY (curator_id) REFERENCES Curator(curator_id),
    FOREIGN KEY (doc_id) REFERENCES Document(doc_id)
);

-- QueryLog table (QueryLog entity)
CREATE TABLE QueryLog (
    log_id SERIAL PRIMARY KEY,
    query_text VARCHAR(1000), -- Unsure on lenght, but probably will be pretty long
    issuer_id INT NOT NULL,
    time_queried TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- When was the query made
    FOREIGN KEY (issuer_id) REFERENCES EndUser(end_id) ON DELETE CASCADE -- When the EndUser that made the query is deleted, delete all the logs they made too
);

-- Makes_Query table (One to Many Relationship between EndUser and QueryLog)
-- one EndUser can make many queries, this table is technically not necessary
CREATE TABLE Makes_Query (
    end_id INT NOT NULL,
    log_id INT NOT NULL,
    PRIMARY KEY (end_id, log_id),
    FOREIGN KEY (end_id) REFERENCES EndUser(end_id),
    FOREIGN KEY (log_id) REFERENCES QueryLog(log_id)
);

-- Queried_Docs table (Many to Many Relationship between QueryLog and Document)
-- One QueryLog will fetch many Documents, One Document can be fetched by many Queries
CREATE TABLE Queried_Docs (
    log_id INT NOT NULL,
    doc_id INT NOT NULL,
    PRIMARY KEY (log_id, doc_id),
    FOREIGN KEY (log_id) REFERENCES QueryLog(log_id) ON DELETE CASCADE, -- When the log that fetched the doc is deleted, delete all the queried_docs they made too
    FOREIGN KEY (doc_id) REFERENCES Document(doc_id)
);

CREATE TABLE Embeddings (
    embed_id SERIAL PRIMARY KEY,
    source_doc_id INT NOT NULL,
    chunk TEXT,
    embedding cs480_finalproject.vector(384),
    FOREIGN KEY (source_doc_id) REFERENCES Document(doc_id) ON DELETE CASCADE -- if source doc deleted, remove any embeddings that came from it too
);