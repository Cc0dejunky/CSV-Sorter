"""trainer.py
Trainer backend used by Streamlit UI to run quick TF-IDF + OneVsRest training and return metrics.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score
import joblib
import csv
from pathlib import Path
import numpy as np
import json
from datetime import datetime

MODEL_DIR = Path(__file__).parent.parent / 'ml' / 'models' / 'optimizer'
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_data(csv_path):
    texts = []
    labels = []
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            texts.append(r['text'])
            labels.append([lbl for lbl in r['labels'].split('|') if lbl])
    return texts, labels


def train_quick(csv_path, ngram=(1,2), max_features=20000, test_size=0.2, random_state=42):
    texts, labels = load_data(csv_path)
    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(labels)
    X_train_text, X_test_text, y_train, y_test = train_test_split(texts, Y, test_size=test_size, random_state=random_state)

    vec = TfidfVectorizer(ngram_range=ngram, max_features=max_features)
    X_train = vec.fit_transform(X_train_text)
    X_test = vec.transform(X_test_text)

    clf = OneVsRestClassifier(LogisticRegression(max_iter=1000))
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    metrics = {
        'f1_macro': float(f1_score(y_test, y_pred, average='macro', zero_division=0)),
        'precision_macro': float(precision_score(y_test, y_pred, average='macro', zero_division=0)),
        'recall_macro': float(recall_score(y_test, y_pred, average='macro', zero_division=0)),
    }

    # sample predictions
    samples = []
    for i in range(min(5, len(X_test_text))):
        preds = mlb.inverse_transform(y_pred[i:i+1])
        samples.append({'text': X_test_text[i], 'preds': preds[0] if preds else []})

    # top features per label (coef-based)
    top_features = {}
    try:
        if hasattr(clf, 'estimators_'):
            feature_names = vec.get_feature_names_out()
            for i, class_label in enumerate(mlb.classes_):
                # for OneVsRestClassifier the estimator order matches classes_
                coef = clf.estimators_[i].coef_.ravel()
                top_idx = np.argsort(coef)[-10:][::-1]
                top_features[class_label] = [feature_names[j] for j in top_idx]
    except Exception:
        top_features = {}

    # Save artifacts
    joblib.dump(vec, MODEL_DIR / 'tfidf_vectorizer.joblib')
    joblib.dump(clf, MODEL_DIR / 'clf.joblib')
    joblib.dump(mlb, MODEL_DIR / 'mlb.joblib')

    # Persist last run metadata (settings + metrics + timestamp)
    try:
        settings = {
            'ngram_min': int(ngram[0]),
            'ngram_max': int(ngram[1]),
            'max_features': int(max_features),
            'test_size': float(test_size),
            'random_state': int(random_state)
        }
    except Exception:
        settings = {}

    last_run = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'settings': settings,
        'metrics': metrics
    }
    try:
        with open(MODEL_DIR / 'last_run.json', 'w', encoding='utf-8') as fh:
            json.dump(last_run, fh, indent=2)
    except Exception:
        pass

    return metrics, samples, top_features


def auto_suggest(csv_path, ngram_options=None, max_features_options=None, test_size_options=None, random_state=42):
    """Run a small grid search over the provided options and return the best settings.

    This will retrain a final model with the best settings and save artifacts.
    """
    if ngram_options is None:
        ngram_options = [(1, 1), (1, 2)]
    if max_features_options is None:
        max_features_options = [5000, 20000]
    if test_size_options is None:
        test_size_options = [0.2]

    best = None
    best_score = -1.0
    results = []
    for ngram in ngram_options:
        for mf in max_features_options:
            for ts in test_size_options:
                try:
                    metrics, _, _ = train_quick(csv_path, ngram=ngram, max_features=mf, test_size=ts, random_state=random_state)
                except Exception as e:
                    # skip failing combos
                    results.append({'ngram': ngram, 'max_features': mf, 'test_size': ts, 'error': str(e)})
                    continue
                score = metrics.get('f1_macro', 0.0)
                results.append({'ngram': ngram, 'max_features': mf, 'test_size': ts, 'metrics': metrics})
                if score > best_score:
                    best_score = score
                    best = {'ngram': ngram, 'max_features': mf, 'test_size': ts, 'metrics': metrics}

    # retrain final model with best settings and save artifacts
    if best is not None:
        # train_quick already saves artifacts on each run; ensure last_run.json reflects best
        try:
            # train once more to ensure artifacts and last_run are set with chosen settings
            train_quick(csv_path, ngram=best['ngram'], max_features=best['max_features'], test_size=best['test_size'], random_state=random_state)
        except Exception:
            pass

    return {'best': best, 'grid': results}
