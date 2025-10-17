
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Table to store final normalized data and embeddings
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    shopify_id BIGINT UNIQUE,
    product_name TEXT NOT NULL,
    normalized_color TEXT,
    category_id INT,
    embedding vector(1536) -- Assuming embedding dimension is 1536
);

-- Table to store confirmed attribute mappings
CREATE TABLE standard_vocabulary (
    id SERIAL PRIMARY KEY,
    raw_value TEXT NOT NULL,
    standard_value TEXT NOT NULL,
    attribute_type TEXT NOT NULL,
    UNIQUE(raw_value, attribute_type)
);

-- Table to log human corrections for training
CREATE TABLE training_feedback (
    id SERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id),
    raw_value TEXT,
    ml_prediction TEXT,
    human_correction TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
