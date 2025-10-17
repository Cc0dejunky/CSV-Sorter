"""train_model.py
Train a TF-IDF + OneVsRest LogisticRegression multilabel classifier.
Saves artifacts to ml/models/optimizer/
"""
from pathlib import Path
import joblib
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer

HERE = Path(__file__).parent
DATA = HERE.parent / 'data' / 'optimizer_training.csv'
MODEL_DIR = HERE.parent.parent / 'models' / 'optimizer'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

texts = []
labels = []
with open(DATA, newline='', encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        texts.append(r['text'])
        labels.append([lbl for lbl in r['labels'].split('|') if lbl])

mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(labels)
vec = TfidfVectorizer(ngram_range=(1,2), max_features=20000)
X = vec.fit_transform(texts)

clf = OneVsRestClassifier(LogisticRegression(max_iter=1000))
clf.fit(X, Y)

joblib.dump(vec, MODEL_DIR / 'tfidf_vectorizer.joblib')
joblib.dump(clf, MODEL_DIR / 'clf.joblib')
joblib.dump(mlb, MODEL_DIR / 'mlb.joblib')
print('Trained model saved to', MODEL_DIR)
