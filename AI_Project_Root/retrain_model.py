
import psycopg2
import joblib

# --- Placeholders ---
DB_HOST = "your-db-host"
DB_NAME = "your-db-name"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"
MODEL_PATH = "AI_Project_Root/models/normalization_model.joblib"

def fetch_standard_vocabulary():
    """
    Fetches the entire standard_vocabulary table from the database.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        cursor.execute(
            "SELECT raw_value, standard_value FROM standard_vocabulary"
        )
        vocabulary = cursor.fetchall()

        cursor.close()
        conn.close()

        return vocabulary

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []

def train_and_save_model(vocabulary):
    """
    Trains a simple model (hash map) and saves it to a file.
    """
    if not vocabulary:
        print("No vocabulary to train on.")
        return

    # Create a hash map (dictionary) from the vocabulary
    model = {raw_value.lower(): standard_value for raw_value, standard_value in vocabulary}

    # Save the model to a file
    try:
        joblib.dump(model, MODEL_PATH)
        print(f"Model saved to {MODEL_PATH}")
    except Exception as e:
        print(f"Error saving model: {e}")

if __name__ == "__main__":
    print("Starting model retraining process...")
    standard_vocabulary = fetch_standard_vocabulary()
    train_and_save_model(standard_vocabulary)
    print("Model retraining process finished.")

