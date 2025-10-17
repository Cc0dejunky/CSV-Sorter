
import os
import psycopg2
from psycopg2.extras import DictCursor

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("PG_HOST", "localhost"),
            database=os.environ.get("PG_DATABASE", "product_data"),
            user=os.environ.get("PG_USER", "postgres"),
            password=os.environ.get("PG_PASSWORD", "postgres"),
            port=os.environ.get("PG_PORT", "5432")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def get_all_products(limit=100):
    """Fetches all products from the database."""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id, shopify_product_id, title, vendor, product_type, handle FROM products ORDER BY updated_at DESC LIMIT %s", (limit,))
            products = cur.fetchall()
        return products
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("Testing PostgreSQL connection...")
    connection = get_db_connection()
    if connection:
        print("Connection successful!")
        print("\nFetching sample products:")
        sample_products = get_all_products(limit=5)
        if sample_products:
            for product in sample_products:
                print(f"- ID: {product['id']}, Title: {product['title']}")
        else:
            print("Could not fetch products. The table might be empty.")
        connection.close()
    else:
        print("Connection failed. Please check your database credentials and ensure the database is running.")
