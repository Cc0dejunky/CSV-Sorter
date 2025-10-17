Optimizer ML integration

Files added:
- src/data/generate_training_data.py  (create training CSV from product CSV)
- src/optimizer/train_model.py        (train TF-IDF + OneVsRest LR)
- src/optimizer/infer.py              (load artifacts and predict)
- src/optimizer/integration.py        (GUI-facing helpers)

Workflow
1) Provide source CSV (Shopify export) and run training:
   python -m src.data.generate_training_data --source path/to/Products.csv
   python -m src.optimizer.train_model
2) Trained artifacts will be in `models/optimizer/`.
3) Use `integration.suggest_tags_for_product_row(product)` from the Streamlit GUI to get suggestions.

Notes
- Training uses scikit-learn and joblib. Install via pip if needed.
