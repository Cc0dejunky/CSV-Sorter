-- 005_upsert_helpers.sql
-- Helper function to upsert a product from a Shopify JSON payload (simple example)

CREATE OR REPLACE FUNCTION upsert_product_from_shopify(payload JSONB) RETURNS UUID AS $$
DECLARE
  shopify_id BIGINT;
  prod_uuid UUID;
BEGIN
  shopify_id := (payload->>'id')::BIGINT;

  INSERT INTO products (shopify_product_id, title, body_html, vendor, product_type, handle, tags, options, created_at, updated_at)
  VALUES (
    shopify_id,
    payload->>'title',
    payload->>'body_html',
    payload->>'vendor',
    payload->>'product_type',
    payload->>'handle',
    (SELECT array_agg(trim(value)) FROM jsonb_array_elements_text(coalesce(payload->'tags','[]'::jsonb)) as value),
    payload->'options',
    (payload->>'created_at')::timestamptz,
    (payload->>'updated_at')::timestamptz
  )
  ON CONFLICT (shopify_product_id) DO UPDATE SET
    title = EXCLUDED.title,
    body_html = EXCLUDED.body_html,
    vendor = EXCLUDED.vendor,
    product_type = EXCLUDED.product_type,
    handle = EXCLUDED.handle,
    tags = EXCLUDED.tags,
    options = EXCLUDED.options,
    updated_at = EXCLUDED.updated_at
  RETURNING id INTO prod_uuid;

  -- Upsert variants if provided
  IF payload ? 'variants' THEN
    WITH v AS (SELECT * FROM jsonb_to_recordset(payload->'variants')
      AS x(id BIGINT, sku TEXT, price TEXT, compare_at_price TEXT, inventory_quantity INT, option1 TEXT, option2 TEXT, option3 TEXT, created_at TEXT, updated_at TEXT))
    INSERT INTO variants (shopify_variant_id, product_id, sku, price, compare_at_price, inventory_quantity, option1, option2, option3, created_at, updated_at)
    SELECT id, prod_uuid, sku, (price::numeric), (compare_at_price::numeric), inventory_quantity, option1, option2, option3, (created_at::timestamptz), (updated_at::timestamptz)
    FROM v
    ON CONFLICT (shopify_variant_id) DO UPDATE SET
      sku = EXCLUDED.sku,
      price = EXCLUDED.price,
      compare_at_price = EXCLUDED.compare_at_price,
      inventory_quantity = EXCLUDED.inventory_quantity,
      option1 = EXCLUDED.option1,
      option2 = EXCLUDED.option2,
      option3 = EXCLUDED.option3,
      updated_at = EXCLUDED.updated_at;
  END IF;

  RETURN prod_uuid;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
-- SELECT upsert_product_from_shopify('<shopify product json>'::jsonb);
