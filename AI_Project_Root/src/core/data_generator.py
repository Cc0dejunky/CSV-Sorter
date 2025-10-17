
import json
import csv
import re
import os

def load_vocabulary(vocab_path):
    """Loads the vocabulary from a JSON file."""
    with open(vocab_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_title(title, vocabulary):
    """
    Applies the normalization rules to a single product title.
    """
    normalized_data = {
        "title": title,
        "brand": "Generic",
        "model": "Unknown",
        "category": "Uncategorized",
        "specs": [],
        "attributes": [],
        "tags": []
    }
    
    remaining_title = title.lower()

    # 1. Brand Lookup
    for brand, aliases in vocabulary['brands'].items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias.lower()) + r'\b', remaining_title):
                normalized_data['brand'] = brand
                # Remove found brand from title to help with model cleanup
                remaining_title = remaining_title.replace(alias.lower(), '')
                break
        if normalized_data['brand'] != "Generic":
            break

    # 2. Category Lookup
    for category, aliases in vocabulary['categories'].items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias.lower()) + r'\b', remaining_title):
                normalized_data['category'] = category
                break
        if normalized_data['category'] != "Uncategorized":
            break

    # 3. Specs Extraction
    found_specs = set()
    for spec_group in vocabulary['specs'].values():
        for spec, aliases in spec_group.items():
            for alias in aliases:
                if re.search(r'\b' + re.escape(alias.lower()) + r'\b', remaining_title):
                    found_specs.add(spec)
                    remaining_title = remaining_title.replace(alias.lower(), '')
    normalized_data['specs'] = sorted(list(found_specs))

    # 4. Attributes Extraction
    found_attributes = set()
    for attribute, aliases in vocabulary['attributes'].items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias.lower()) + r'\b', remaining_title):
                found_attributes.add(attribute)
                remaining_title = remaining_title.replace(alias.lower(), '')
    normalized_data['attributes'] = sorted(list(found_attributes))

    # 5. Model Cleanup
    # A simple approach: clean up, remove extra spaces, and take the longest remaining word/phrase
    # This is a basic heuristic and can be improved later.
    remaining_title = re.sub(r'[^a-z0-9\s-]', '', remaining_title).strip()
    # Remove common fluff words
    fluff = ['original', 'new', 'used', 'phone', 'pro', 'max', 'ultra', 'plus', 'lite']
    for word in fluff:
        remaining_title = re.sub(r'\b' + word + r'\b', '', remaining_title)
    
    # Find the most likely model name from the remaining parts
    potential_models = [part.strip() for part in remaining_title.split() if len(part.strip()) > 1]
    if potential_models:
        # A simple heuristic: the longest part is often the model name
        normalized_data['model'] = max(potential_models, key=len).upper()


    # 6. Tags Assembly
    tags = set(normalized_data['specs']) | set(normalized_data['attributes'])
    if normalized_data['category'] != "Uncategorized":
        tags.add(normalized_data['category'])
    normalized_data['tags'] = sorted(list(tags))

    return normalized_data

def generate_training_data(csv_path, vocab_path, output_path):
    """
    Reads a product CSV and a vocabulary JSON, normalizes the titles,
    and writes the output to a JSONL file.
    """
    vocabulary = load_vocabulary(vocab_path)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    processed_count = 0
    with open(csv_path, 'r', encoding='utf-8') as csv_file, \
         open(output_path, 'w', encoding='utf-8') as jsonl_file:
        
        reader = csv.DictReader(csv_file)
        for row in reader:
            title = row.get('Title')
            if not title:
                continue
            
            normalized_product = normalize_title(title, vocabulary)
            jsonl_file.write(json.dumps(normalized_product) + '\n')
            processed_count += 1
            
    return processed_count

if __name__ == '__main__':
    # This allows the script to be run directly
    # Assumes a project structure where this script is in 'core'
    # and the data is in 'ml/data'
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    product_csv_path = os.path.join(project_root, 'ml', 'data', 'product.csv')
    vocabulary_json_path = os.path.join(project_root, 'ml', 'data', 'vocabulary.json')
    output_jsonl_path = os.path.join(project_root, 'ml', 'data', 'training_data.jsonl')

    print("Starting data generation...")
    count = generate_training_data(product_csv_path, vocabulary_json_path, output_jsonl_path)
    print(f"Processing complete. Wrote {count} lines to {output_jsonl_path}")
