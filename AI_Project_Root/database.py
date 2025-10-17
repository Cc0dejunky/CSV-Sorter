import psycopg2

# --- Placeholders ---
DB_HOST = "your-db-host"
DB_NAME = "your-db-name"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"


def get_connection():
    """Establishes and returns a database connection."""
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def get_entire_vocabulary():
    """
    Fetches all entries from the standard_library table, ordered for display.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT raw_value, standard_value, attribute_type FROM standard_library ORDER BY attribute_type, raw_value"
                )
                return cursor.fetchall()
    except psycopg2.Error as e:
        # Return the error message to be displayed in the TUI
        return f"Database error: {e}"
