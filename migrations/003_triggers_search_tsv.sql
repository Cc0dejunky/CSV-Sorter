-- 003_triggers_search_tsv.sql
-- Optional: trigger to keep tsvector up-to-date

CREATE OR REPLACE FUNCTION products_search_vector_trigger() RETURNS trigger AS $$
begin
  new.storefront_tsv := to_tsvector('english', coalesce(new.title,'') || ' ' || coalesce(new.body_html,''));
  return new;
end
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS products_tsv_trigger ON products;
CREATE TRIGGER products_tsv_trigger
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW EXECUTE PROCEDURE products_search_vector_trigger();
