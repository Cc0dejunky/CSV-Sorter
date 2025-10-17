"""generate_training_data.py
Adapted from your Shopif Product Optimizer project. Produces a CSV with 'text' and 'labels' columns.
Usage:
  Set SOURCE_CSV to the path of your products CSV or pass via command-line.
  python ml/optimizer/generate_training_data.py --source path/to/Products.csv
"""
from pathlib import Path
import csv
import re
import json
import sys
import argparse

HERE = Path(__file__).parent
OUT = HERE.parent / 'data' / 'optimizer_training.csv'
OUT.parent.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--source', help='Source products CSV', default=None)
args = parser.parse_args()

# Allow env var or CLI
src_candidate = args.source
if not src_candidate:
    import os
    src_candidate = os.environ.get('SOURCE_PRODUCTS_CSV')

if not src_candidate:
    print('Provide --source or set SOURCE_PRODUCTS_CSV environment variable')
    raise SystemExit(1)

SRC = Path(src_candidate)
if not SRC.exists():
    print('Source CSV not found:', SRC)
    raise SystemExit(1)

STORAGE_RE = re.compile(r"(\d+(?:\.\d+)?\s*(?:gb|tb))", re.IGNORECASE)
MP_RE = re.compile(r"(\d+)\s?mp", re.IGNORECASE)

def strip_html(s: str) -> str:
    return re.sub(r'<[^>]+>', ' ', s or '')

rows = []
with open(SRC, newline='', encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    seen = set()
    for row in reader:
        handle = (row.get('Handle') or '').strip()
        if not handle:
            continue
        if handle in seen:
            continue
        seen.add(handle)
        title = (row.get('Title') or '').strip()
        body = (row.get('Body (HTML)') or '')
        text = f"{handle} {title} {strip_html(body)}".strip()

        labels = set()
        # heuristics
        for m in STORAGE_RE.findall(title + ' ' + body):
            labels.add(m.replace(' ', '').upper())
        for m in MP_RE.findall(title + ' ' + body):
            labels.add(f"{m}MP")

        # fallback: use vendor/product_type if present
        if row.get('Vendor'):
            labels.add(row.get('Vendor').strip())
        if row.get('Type'):
            labels.add(row.get('Type').strip())

        if labels:
            rows.append({'text': text, 'labels': '|'.join(sorted(labels))})

if not rows:
    print('No labeled rows generated from', SRC)
    raise SystemExit(1)

with open(OUT, 'w', newline='', encoding='utf-8') as out:
    writer = csv.DictWriter(out, fieldnames=['text','labels'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f'Wrote {len(rows)} rows to {OUT}')
