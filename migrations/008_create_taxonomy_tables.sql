-- 008_create_taxonomy_tables.sql
-- PostgreSQL schema for Shopify's product taxonomy attributes and values.

-- Attributes table to store the main attribute definitions.
CREATE TABLE IF NOT EXISTS taxonomy_attributes (
    id TEXT PRIMARY KEY, -- e.g., 'gid://shopify/TaxonomyAttribute/2649'
    name TEXT NOT NULL,
    handle TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Values table to store the possible values for each attribute.
CREATE TABLE IF NOT EXISTS taxonomy_values (
    id TEXT PRIMARY KEY, -- e.g., 'gid://shopify/TaxonomyValue/16300'
    attribute_id TEXT REFERENCES taxonomy_attributes(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    handle TEXT NOT NULL UNIQUE
);

-- Mapping table to link simple keywords to structured attribute handles.
CREATE TABLE IF NOT EXISTS keyword_to_attribute_map (
    keyword TEXT PRIMARY KEY,
    attribute_handle TEXT REFERENCES taxonomy_attributes(handle) ON DELETE CASCADE
);

-- Index for faster lookups on attribute handles
CREATE INDEX IF NOT EXISTS idx_taxonomy_attributes_handle ON taxonomy_attributes(handle);
CREATE INDEX IF NOT EXISTS idx_taxonomy_values_attribute_id ON taxonomy_values(attribute_id);
