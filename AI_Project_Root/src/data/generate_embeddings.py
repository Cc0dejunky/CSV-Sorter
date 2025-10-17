"""generate_embeddings.py

Simple script to read products (title + body_html), call an embedding provider, and insert embeddings into `product_embeddings`.

Usage:
  Set environment variables: DATABASE_URL (Postgres DSN), OPENAI_API_KEY (if using OpenAI), EMBEDDING_MODEL (optional)
  python generate_embeddings.py

This script is intentionally provider-agnostic. It includes an OpenAI example but you can replace the `get_embedding` function.
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Optional: install openai package and uncomment the import if using OpenAI
# import openai

DB_DSN = os.environ.get('DATABASE_URL')  # e.g. postgresql://user:pass@localhost:5432/dbname
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')
EMBEDDING_DIM = int(os.environ.get('EMBEDDING_DIM', '1536'))

# Replace this with your embedding provider call
def get_embedding(text: str):
    """Return a list[float] embedding for the given text. """
    # Example using OpenAI's REST API (pseudo-code):
    # headers = { 'Authorization': f'Bearer {OPENAI_API_KEY}', 'Content-Type': 'application/json' }
    # payload = { 'model': EMBEDDING_MODEL, 'input': text }
    # r = requests.post('https://api.openai.com/v1/embeddings', headers=headers, json=payload)
    # return r.json()['data'][0]['embedding']
    raise NotImplementedError('Hook up your embedding provider in get_embedding()')


def main():
    if not DB_DSN:
        print('Please set DATABASE_URL')
        return

    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Find products without any embeddings
    cur.execute("""
    SELECT p.id, p.title, p.body_html
    FROM products p
    LEFT JOIN product_embeddings pe ON pe.product_id = p.id
    WHERE pe.id IS NULL
    LIMIT 100
    """)
    rows = cur.fetchall()

    for row in rows:
        product_id = row['id']
        text = (row['title'] or '') + '\n' + (row['body_html'] or '')
        # TODO: chunk long text here
        try:
            emb = get_embedding(text)
        except NotImplementedError as e:
            print(e)
            print('No embedding provider configured; stopping.')
            break

        # Validate embedding length
        if len(emb) != EMBEDDING_DIM:
            print(f'Warning: embedding dim {len(emb)} != expected {EMBEDDING_DIM}')

        # Insert embedding
        cur.execute(
            "INSERT INTO product_embeddings (product_id, embedding, model, metadata) VALUES (%s, %s, %s, %s)",
            (product_id, emb, EMBEDDING_MODEL, json.dumps({'source': 'auto', 'product_id': str(product_id)}))
        )
        conn.commit()
        print(f'Inserted embedding for product {product_id}')

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
