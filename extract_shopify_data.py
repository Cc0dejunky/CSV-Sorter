
import requests
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# --- Placeholders ---
SHOPIFY_API_URL = "https://your-shop-name.myshopify.com/admin/api/2023-10/products.json"
SHOPIFY_ACCESS_TOKEN = "your-shopify-access-token"
DB_HOST = "your-db-host"
DB_NAME = "your-db-name"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"

def fetch_shopify_products():
    """
    Fetches product data from the Shopify API.
    """
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(SHOPIFY_API_URL, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json().get("products", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Shopify data: {e}")
        return None

def structure_product_data(products):
    """
    Structures the raw product data into a pandas DataFrame.
    """
    if not products:
        return pd.DataFrame()

    product_list = []
    for product in products:
        product_list.append({
            "shopify_id": product.get("id"),
            "product_name": product.get("title"),
            "body_html": product.get("body_html"),
            "tags": product.get("tags")
        })
    
    return pd.DataFrame(product_list)

def insert_into_products_table(df):
    """
    Inserts the product data into the 'products' table in the database.
    """
    if df.empty:
        print("No product data to insert.")
        return

    # --- Database Connection (Placeholder) ---
    # Replace with your actual database connection logic
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Prepare data for insertion
        # Note: This example assumes the DataFrame columns match the table columns.
        # You might need to adjust the column names and order.
        # We are only inserting a subset of the columns for this example.
        data_to_insert = [
            (row['shopify_id'], row['product_name'])
            for index, row in df.iterrows()
        ]
        
        # Using execute_values for efficient bulk insertion
        execute_values(
            cursor,
            "INSERT INTO products (shopify_id, product_name) VALUES %s ON CONFLICT (shopify_id) DO NOTHING",
            data_to_insert
        )

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Successfully inserted/updated {len(data_to_insert)} products.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    print("Fetching product data from Shopify...")
    raw_products = fetch_shopify_products()

    if raw_products:
        print("Structuring product data...")
        product_df = structure_product_data(raw_products)
        print("Sample of extracted data:")
        print(product_df.head())

        # --- Placeholder for database insertion ---
        # print("\nInserting data into the database...")
        # insert_into_products_table(product_df)

