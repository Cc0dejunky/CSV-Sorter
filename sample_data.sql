-- sample_data.sql
-- Insert a tiny sample product and a placeholder embedding (NULL for embedding until you generate one)

INSERT INTO products (shopify_product_id, title, body_html, vendor, product_type, handle, tags, options, created_at, updated_at)
VALUES (1234567890, 'Acme Red T-Shirt', '<p>Soft, breathable cotton tee. Available in sizes S-XL.</p>', 'Acme', 'Apparel', 'acme-red-t-shirt', ARRAY['red','t-shirt'], '{"size":["S","M","L","XL"]}'::jsonb, now(), now())
RETURNING id;

-- After you get the product id from the insertion, insert a sample embedding (replace \'<UUID>\')
-- INSERT INTO product_embeddings (product_id, embedding, model, metadata) VALUES ('<UUID>', '[0.0, ...]'::vector, 'openai-text-embedding-3-small', '{"source":"shopify_product:1234567890"}');
