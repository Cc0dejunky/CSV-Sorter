-- 006_create_unique_index_on_mv.sql
-- Create unique index required for CONCURRENTLY refresh of materialized view

-- NOTE: run only after materialized view created and populated
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS product_summary_mv_product_id_idx ON product_summary_mv (product_id);
