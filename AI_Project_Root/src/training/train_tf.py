"""train_tf.py
Train a simple Keras model to predict product_type from title+body_html.
Saves the model and the text vectorization layer.
"""
import argparse
import pandas as pd
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import json

from src.core import config

parser = argparse.ArgumentParser(description="Train a TensorFlow product classifier.")
parser.add_argument('--data-path', type=str, default=config.PROCESSED_DATA_DIR / 'products_train.csv', help='Path to the training CSV file.')
parser.add_argument('--epochs', type=int, default=config.TrainingConfig.EPOCHS, help='Number of training epochs.')
parser.add_argument('--batch-size', type=int, default=config.TrainingConfig.BATCH_SIZE, help='Training batch size.')
parser.add_argument('--lr', type=float, default=config.TrainingConfig.LEARNING_RATE, help='Learning rate for the optimizer.')
args = parser.parse_args()

MODEL_DIR = config.TF_MODEL_DIR

print('Loading data...')
df = pd.read_csv(args.data_path)
# simple text = title + body
texts = (df['title'].fillna('') + '\n' + df['body_html'].fillna('')).astype(str)
labels = df['product_type'].astype(str)

# Label encoding
label_to_idx = {l: i for i, l in enumerate(sorted(labels.unique()))}
idx_to_label = {i: l for l, i in label_to_idx.items()}
y = np.array([label_to_idx[l] for l in labels])
num_classes = len(label_to_idx)

# Text vectorization
max_tokens = 20000
sequence_length = 256
vectorize_layer = layers.TextVectorization(max_tokens=max_tokens, output_mode='int', output_sequence_length=sequence_length)
vectorize_layer.adapt(texts.values)

# Build model
vocab_size = min(max_tokens, len(vectorize_layer.get_vocabulary()))
embedding_dim = 128
inputs = keras.Input(shape=(1,), dtype='string')
x = vectorize_layer(inputs)
x = layers.Embedding(vocab_size, embedding_dim)(x)
x = layers.GlobalAveragePooling1D()(x)
x = layers.Dense(128, activation='relu')(x)
outputs = layers.Dense(num_classes, activation='softmax')(x)
model = keras.Model(inputs, outputs)

optimizer = keras.optimizers.Adam(learning_rate=args.lr)
model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print('Training...')
model.fit(texts.values, y, epochs=args.epochs, batch_size=args.batch_size, validation_split=0.1)

# Save
model.save(MODEL_DIR / 'product_type_model')
# Save label map
with open(MODEL_DIR / 'label_map.json', 'w', encoding='utf-8') as f:
    json.dump({'label_to_idx': label_to_idx, 'idx_to_label': idx_to_label}, f)

print('Saved TF model to', MODEL_DIR)
