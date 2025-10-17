-- 001_create_schema.sql
-- PostgreSQL schema for Shopify product data and AI context

-- Requires: PostgreSQL 14+ and pgvector extension (for embeddings)

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Products
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shopify_product_id BIGINT UNIQUE,
    title TEXT NOT NULL,
    body_html TEXT,
    vendor TEXT,
    product_type TEXT,
    handle TEXT,
    status TEXT,
    tags TEXT[],
    options JSONB,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    storefront_tsv tsvector -- computed tsvector for full-text search
);

-- Variants
CREATE TABLE IF NOT EXISTS variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shopify_variant_id BIGINT UNIQUE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    sku TEXT,
    price NUMERIC(12,2),
    compare_at_price NUMERIC(12,2),
    inventory_quantity INT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Images
CREATE TABLE IF NOT EXISTS images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    variant_id UUID REFERENCES variants(id) ON DELETE SET NULL,
    src TEXT,
    alt TEXT,
    position INT
);

-- Collections
CREATE TABLE IF NOT EXISTS collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shopify_collection_id BIGINT UNIQUE,
    title TEXT,
    handle TEXT,
    body_html TEXT
);

CREATE TABLE IF NOT EXISTS product_collections (
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, collection_id)
);

-- Metafields (flexible key-value store for Shopify metafields)
CREATE TABLE IF NOT EXISTS metafields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type TEXT NOT NULL, -- e.g. 'product', 'variant'
    resource_id BIGINT NOT NULL,
    namespace TEXT,
    key TEXT,
    value TEXT,
    value_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Sync logs to track Shopify pulls/pushes
CREATE TABLE IF NOT EXISTS sync_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operation TEXT NOT NULL, -- import, update, delete
    resource_type TEXT,
    resource_id BIGINT,
    succeeded BOOLEAN DEFAULT FALSE,
    message TEXT,
    ts TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Full-text index: keep a computed column or an index on expression
CREATE INDEX IF NOT EXISTS products_storefront_tsv_idx ON products USING GIN ( (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(body_html,''))) );

-- Useful lookup indexes
CREATE INDEX IF NOT EXISTS products_shopify_id_idx ON products (shopify_product_id);
CREATE INDEX IF NOT EXISTS variants_shopify_id_idx ON variants (shopify_variant_id);

-- NOTE: Embeddings table (separate file) will include vector type and vector indexes
