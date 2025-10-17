"""integration.py
Integration helper that exposes simple functions the GUI can call:
- suggest_tags_for_product(product_row)
- train_from_csv(source_csv)
"""
from pathlib import Path
import subprocess
import os

HERE = Path(__file__).parent
DATA = HERE.parent / 'data'
MODELS = HERE.parent.parent / 'models' / 'optimizer'

def train_from_csv(source_csv):
    # run data generation then training
    cmd1 = ['python', str(HERE / 'generate_training_data.py'), '--source', str(source_csv)]
    subprocess.check_call(cmd1)
    cmd2 = ['python', str(HERE / 'train_model.py')]
    subprocess.check_call(cmd2)
    return True

# lazy import for prediction to avoid loading artifacts at module import time
def suggest_tags_for_product_text(text):
    from . import infer
    return infer.predict(text)

def suggest_tags_for_product_row(product):
    # product is a dict-like with title and body_html
    text = (product.get('title') or '') + '\n' + (product.get('body_html') or '')
    return suggest_tags_for_product_text(text)
