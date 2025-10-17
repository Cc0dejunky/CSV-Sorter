
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pandas as pd
import psycopg2
import joblib
from AI_Project_Root.embedding_generator import EmbeddingGenerator

# --- Placeholders ---
DB_HOST = "your-db-host"
DB_NAME = "your-db-name"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"
MODEL_PATH = "../AI_Project_Root/models/normalization_model.joblib"

def load_normalization_model():
    """
    Loads the normalization model from the .joblib file.
    """
    try:
        normalization_model = joblib.load(MODEL_PATH)
        print("Normalization model loaded successfully.")
        return normalization_model
    except FileNotFoundError:
        print("Normalization model not found. Using empty model.")
        return {}
    except Exception as e:
        print(f"Error loading normalization model: {e}")
        return {}

def process_csv_upload(file_path):
    """
    Processes a CSV file, generates predictions and embeddings, and inserts into the database.
    """
    normalization_model = load_normalization_model()
    embedding_generator = EmbeddingGenerator()

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        for index, row in df.iterrows():
            product_name = row["product_name"]
            raw_color = row.get("color") # Assuming a 'color' column in the CSV

            # Generate ML prediction
            ml_prediction = normalization_model.get(raw_color.lower(), raw_color) if raw_color else None

            # Generate embedding
            embedding = embedding_generator.generate_embedding(product_name)

            # Insert into database
            cursor.execute(
                """INSERT INTO products (product_name, normalized_color, embedding, needs_review)
                   VALUES (%s, %s, %s, %s);""",
                (product_name, ml_prediction, embedding, True)
            )

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Successfully processed and inserted {len(df)} products from {file_path}")

    except (psycopg2.Error, pd.errors.EmptyDataError, KeyError) as e:
        print(f"Error processing CSV file: {e}")

