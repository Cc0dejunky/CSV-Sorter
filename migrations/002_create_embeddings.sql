-- 002_create_embeddings.sql
-- Table for storing embeddings and metadata used by AI for contextual retrieval

-- Assumes pgvector extension already enabled (see 001_create_schema.sql)

-- Adjust dimension (e.g. 1536 for OpenAI text-embedding-3-small / text-embedding-3-large dims differ)
CREATE TABLE IF NOT EXISTS product_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    embedding VECTOR(1536), -- change dimension to match your embedding model
    model TEXT,
    metadata JSONB, -- storage for text chunk id, source, score, shopify fields, etc
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Example index for approximate nearest neighbors using pgvector's ivfflat
-- Create an index only after you've populated the table and chosen appropriate "lists" value.
-- The index creation may require superuser permissions.
-- CREATE INDEX product_embeddings_embedding_ivfflat_idx ON product_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- For exact similarity (small dataset) you can use a sequential scan with similarity operator
-- We'll also create a materialized text search to help hybrid queries if needed
