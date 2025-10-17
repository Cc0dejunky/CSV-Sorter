-- 004_materialized_views.sql
-- Create a materialized view for fast frontend-style reads (product summary)

CREATE MATERIALIZED VIEW IF NOT EXISTS product_summary_mv AS
SELECT
  p.id as product_id,
  p.shopify_product_id,
  p.title,
  p.handle,
  p.vendor,
  p.product_type,
  p.tags,
  p.updated_at,
  -- best variant (lowest price) - simplified example
  (SELECT jsonb_build_object('id', v.id, 'sku', v.sku, 'price', v.price, 'inventory_quantity', v.inventory_quantity)
   FROM variants v WHERE v.product_id = p.id ORDER BY v.price NULLS LAST LIMIT 1) as best_variant,
  -- top image
  (SELECT jsonb_build_object('src', img.src, 'alt', img.alt) FROM images img WHERE img.product_id = p.id ORDER BY img.position NULLS LAST LIMIT 1) as top_image
FROM products p;

-- Convenience function to refresh the materialized view
CREATE OR REPLACE FUNCTION refresh_product_summary_mv() RETURNS void LANGUAGE sql AS $$
REFRESH MATERIALIZED VIEW CONCURRENTLY product_summary_mv;
$$;

-- Note: REFRESH MATERIALIZED VIEW CONCURRENTLY requires the view to have a unique index. If needed, create a unique index on product_id:
-- CREATE UNIQUE INDEX ON product_summary_mv (product_id);

-- Optionally set up a scheduled job (cron, pg_cron) to periodically refresh.
