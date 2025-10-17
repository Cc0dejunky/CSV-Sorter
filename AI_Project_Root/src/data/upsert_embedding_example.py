"""upsert_embedding_example.py
Simple example showing how to upsert an embedding for a product into product_embeddings table.
"""
import os
import json
import psycopg2

DB_DSN = os.environ.get('DATABASE_URL')

def upsert_embedding(product_id, embedding, model='text-embedding-3-small'):
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    # For simplicity, we just insert. In production consider deleting existing embeddings for the same model/source.
    cur.execute("INSERT INTO product_embeddings (product_id, embedding, model, metadata) VALUES (%s, %s, %s, %s)",
                (product_id, embedding, model, json.dumps({'source':'manual'})))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    print('Call upsert_embedding(product_id, embedding) from your worker.')
