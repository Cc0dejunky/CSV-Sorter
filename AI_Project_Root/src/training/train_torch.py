"""train_torch.py
Train a simple PyTorch MLP using TF-IDF features to predict product_type.
Saves model and vectorizer using joblib.
"""
import argparse
import pandas as pd
import joblib

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

from src.core import config

parser = argparse.ArgumentParser(description="Train a PyTorch product classifier.")
parser.add_argument('--data-path', type=str, default=config.PROCESSED_DATA_DIR / 'products_train.csv', help='Path to the training CSV file.')
parser.add_argument('--epochs', type=int, default=config.TrainingConfig.EPOCHS, help='Number of training epochs.')
parser.add_argument('--batch-size', type=int, default=config.TrainingConfig.BATCH_SIZE, help='Training batch size.')
parser.add_argument('--lr', type=float, default=config.TrainingConfig.LEARNING_RATE, help='Learning rate for the optimizer.')
args = parser.parse_args()

MODEL_DIR = config.TORCH_MODEL_DIR

print('Loading data...')
df = pd.read_csv(args.data_path)
texts = (df['title'].fillna('') + '\n' + df['body_html'].fillna('')).astype(str)
labels = df['product_type'].astype(str)

# TF-IDF
vectorizer = TfidfVectorizer(max_features=20000)
X = vectorizer.fit_transform(texts.values)

le = LabelEncoder()
y = le.fit_transform(labels)
num_classes = len(le.classes_)

# Simple PyTorch Dataset
class TfidfDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
    def __len__(self):
        return self.X.shape[0]
    def __getitem__(self, idx):
        return torch.tensor(self.X[idx].toarray(), dtype=torch.float32).squeeze(0), torch.tensor(self.y[idx], dtype=torch.long)

dataset = TfidfDataset(X, y)
loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

# Model
class MLP(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )
    def forward(self, x):
        return self.net(x)

model = MLP(X.shape[1], num_classes)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

print('Training...')
for epoch in range(args.epochs):
    total_loss = 0.0
    for xb, yb in loader:
        optimizer.zero_grad()
        out = model(xb)
        loss = criterion(out, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f'Epoch {epoch+1} loss {total_loss/len(loader):.4f}')

# Save model and vectorizer
torch.save(model.state_dict(), MODEL_DIR / 'model.pt')
joblib.dump(vectorizer, MODEL_DIR / 'tfidf.joblib')
joblib.dump(le, MODEL_DIR / 'label_encoder.joblib')
print('Saved PyTorch model to', MODEL_DIR)
