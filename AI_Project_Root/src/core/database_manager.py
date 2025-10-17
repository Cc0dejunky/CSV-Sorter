import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'app_data.db')
VOCAB_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ml', 'data', 'vocabulary.json')

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    """Creates the database tables from scratch."""
    conn = get_connection()
    cursor = conn.cursor()

    # Drop tables if they exist to ensure a clean slate
    cursor.execute("DROP TABLE IF EXISTS brands")
    cursor.execute("DROP TABLE IF EXISTS categories")
    cursor.execute("DROP TABLE IF EXISTS specs")
    cursor.execute("DROP TABLE IF EXISTS attributes")
    cursor.execute("DROP TABLE IF EXISTS aliases")

    # Create tables
    

    cursor.execute("""
    CREATE TABLE brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        parent_id INTEGER,
        FOREIGN KEY (parent_id) REFERENCES categories (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        spec_group TEXT NOT NULL,
        UNIQUE(name, spec_group)
    )
    """)

    cursor.execute("""
    CREATE TABLE attributes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        entity_type TEXT NOT NULL, -- 'brand', 'category', 'spec', 'attribute'
        entity_id INTEGER NOT NULL,
        UNIQUE(name, entity_type, entity_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database tables created successfully.")

def import_vocabulary_from_json():
    """Imports data from vocabulary.json into the SQLite database."""
    if not os.path.exists(VOCAB_JSON_PATH):
        print(f"Error: {VOCAB_JSON_PATH} not found.")
        return

    with open(VOCAB_JSON_PATH, 'r', encoding='utf-8') as f:
        vocab = json.load(f)

    conn = get_connection()
    cursor = conn.cursor()

    # Import Brands
    for brand, aliases in vocab.get('brands', {}).items():
        cursor.execute("INSERT INTO brands (name) VALUES (?)", (brand,))
        brand_id = cursor.lastrowid
        for alias in aliases:
            cursor.execute("INSERT INTO aliases (name, entity_type, entity_id) VALUES (?, ?, ?)", (alias, 'brand', brand_id))

    # Import Categories (assumes no hierarchy in the JSON for now)
    for category, aliases in vocab.get('categories', {}).items():
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
        category_id = cursor.lastrowid
        for alias in aliases:
            cursor.execute("INSERT INTO aliases (name, entity_type, entity_id) VALUES (?, ?, ?)", (alias, 'category', category_id))

    # Import Specs
    for group, specs in vocab.get('specs', {}).items():
        for spec, aliases in specs.items():
            cursor.execute("INSERT INTO specs (name, spec_group) VALUES (?, ?)", (spec, group))
            spec_id = cursor.lastrowid
            for alias in aliases:
                cursor.execute("INSERT INTO aliases (name, entity_type, entity_id) VALUES (?, ?, ?)", (alias, 'spec', spec_id))

    # Import Attributes
    for attribute, aliases in vocab.get('attributes', {}).items():
        cursor.execute("INSERT INTO attributes (name) VALUES (?)", (attribute,))
        attribute_id = cursor.lastrowid
        for alias in aliases:
            cursor.execute("INSERT INTO aliases (name, entity_type, entity_id) VALUES (?, ?, ?)", (alias, 'attribute', attribute_id))

    conn.commit()
    conn.close()
    print("Successfully imported vocabulary from JSON to SQLite database.")

def get_entities(entity_type: str):
    """Fetches all items for a given entity type (e.g., 'brands')."""
    conn = get_connection()
    cursor = conn.cursor()
    
    table_name = entity_type # e.g., 'brands', 'categories'
    
    # Basic validation to prevent SQL injection, though we control the input.
    if table_name not in ['brands', 'categories', 'specs', 'attributes']:
        return []

    cursor.execute(f"SELECT * FROM {table_name} ORDER BY name")
    entities = cursor.fetchall()
    
    results = []
    for entity in entities:
        entity_dict = dict(entity)
        cursor.execute("SELECT name FROM aliases WHERE entity_type = ? AND entity_id = ?", (table_name.rstrip('s'), entity['id']))
        aliases = [row['name'] for row in cursor.fetchall()]
        entity_dict['aliases'] = aliases
        results.append(entity_dict)

    conn.close()
    return results

if __name__ == '__main__':
    print("Setting up the database...")
    create_database()
    import_vocabulary_from_json()
    print("Database setup complete.")