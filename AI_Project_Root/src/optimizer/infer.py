"""infer.py
Load optimizer model artifacts and provide predict(text) -> list(labels).
"""
from pathlib import Path
import joblib

HERE = Path(__file__).parent
MODEL_DIR = HERE.parent.parent / 'models' / 'optimizer'
VEC = joblib.load(MODEL_DIR / 'tfidf_vectorizer.joblib')
CLF = joblib.load(MODEL_DIR / 'clf.joblib')
MLB = joblib.load(MODEL_DIR / 'mlb.joblib')

def predict(text):
    x = VEC.transform([text])
    preds = CLF.predict(x)
    labels = MLB.inverse_transform(preds)
    return labels[0] if labels else []

if __name__ == '__main__':
    examples = [
        'apple iphone 14 pro 256GB',
        'sandisk usb flash drive 64GB usb-c',
    ]
    for e in examples:
        print(e, '->', predict(e))
