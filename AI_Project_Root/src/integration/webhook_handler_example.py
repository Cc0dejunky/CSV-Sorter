"""webhook_handler_example.py

Small Flask example showing how to accept Shopify product webhooks, upsert a product using the DB function, and enqueue an embedding job (placeholder).

This is a sketch — adapt to your background worker (RQ, Celery, Bull, etc.).

"""
from flask import Flask, request, jsonify
import os
import json
import psycopg2

app = Flask(__name__)
DB_DSN = os.environ.get('DATABASE_URL')

@app.route('/webhook/product', methods=['POST'])
def product_webhook():
    payload = request.get_json()
    if not payload:
        return jsonify({'error':'no json'}), 400

    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    # Call the upsert function we defined in SQL
    cur.execute("SELECT upsert_product_from_shopify(%s)::text", (json.dumps(payload),))
    prod_uuid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # Enqueue embedding job — placeholder: write to a simple jobs table or push to your queue
    # Example: INSERT INTO embedding_jobs (product_id, status) VALUES (prod_uuid, 'pending')

    return jsonify({'status':'ok','product_id':prod_uuid}), 200

if __name__ == '__main__':
    app.run(port=5000)
