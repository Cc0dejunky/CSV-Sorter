import psycopg2

# --- Placeholders ---
DB_HOST = "your-db-host"
DB_NAME = "your-db-name"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"


def fetch_new_feedback():
    """
    Fetches new feedback from the training_feedback table.
    """
    try:
        with psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cursor:
                # Fetch approved feedback that hasn't been processed yet.
                # This assumes you have added a boolean 'processed' column
                # to your 'training_feedback' table.
                cursor.execute(
                    "SELECT id, raw_value, human_correction, ml_prediction FROM training_feedback WHERE human_correction IS NOT NULL AND (processed IS NULL OR processed = false)"
                )
                feedback = cursor.fetchall()

        return feedback

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return []


def consolidate_feedback(feedback):
    """
    Consolidates the new feedback into the standard_library table.
    """
    if not feedback:
        print("No new feedback to consolidate.")
        return

    try:
        with psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        ) as conn:  # The connection will be committed on a successful block exit
            with conn.cursor() as cursor:
                processed_ids = []
                for feedback_id, raw_value, human_correction, ml_prediction in feedback:
                    # For simplicity, we'll assume the attribute_type is 'color'.
                    # In a real application, you might need to determine this dynamically.
                    attribute_type = "color"

                    # Insert or update the standard_library table
                    cursor.execute(
                        """INSERT INTO standard_library (raw_value, standard_value, attribute_type)
                           VALUES (%s, %s, %s)
                           ON CONFLICT (raw_value, attribute_type) DO UPDATE SET
                           standard_value = EXCLUDED.standard_value;""",
                        (raw_value, human_correction, attribute_type),
                    )
                    processed_ids.append(feedback_id)

                # Mark the feedback entries as processed
                if processed_ids:
                    cursor.execute(
                        "UPDATE training_feedback SET processed = true WHERE id = ANY(%s)",
                        (processed_ids,),
                    )
        print(f"Successfully consolidated {len(feedback)} feedback entries.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    print("Starting feedback consolidation process...")
    new_feedback = fetch_new_feedback()
    consolidate_feedback(new_feedback)
    print("Feedback consolidation process finished.")
