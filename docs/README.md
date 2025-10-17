Product Normalization System - Execution Flow

This file describes the primary scripts in the order they execute during a successful CSV Upload operation (Menu Option [2]), followed by related system services and model training components.

1. CSV Upload & Normalization Sequence (Order of Execution)

This sequence runs immediately after a user uploads a valid CSV file.

1.1 Ingestion & Orchestration

CSV_Processor.py (Root File)

Description: Reads the CSV, validates mandatory headers, orchestrates the entire normalization pipeline (Steps 1 & 2), calls the embedding generation subprocess, and manages insertion into the database.

1.2 Feature Generation (Subprocess)

Embedding_generator.py (Subprocess)

Description: Processes cleaned product text features from CSV_Processor.py, generates sophisticated numerical text embeddings (Step 3), and updates the PostgreSQL database records with these new features.

1.3 Data Persistence & Management (Core Dependency)

Database.py (Core Dependency)

Description: Initializes the database and provides the necessary CRUD (Create, Read, Update, Delete) functions used by CSV_Processor.py (Step 4) to save the normalized data and by the TUI to commit changes (Step 6).

2. Decision and Feedback Loop (Conditional Execution)

This script is only executed if the user selects [2] Give Feedback (Discard) (Step 7).

Consolidate_feedback.py

Description: This script takes user input (feedback on normalized data errors), processes it, and consolidates the feedback into a standard vocabulary table within the database. This feedback is later used to improve model performance during retraining.

3. System Services & Training Components

These files manage the overall application, API, and model maintenance.

3.1 Main Application Services

Main.py

Description: Acts as the primary TUI and/or FastAPI service, managing product data, applying ML color normalization, and handling overall user interaction and flow control.

Extract_shopify_data.py

Description: Executes the alternative data ingestion path (Menu Option [1] - Review Products), extracting product data directly from the Shopify API, converting it to a DataFrame, and loading it into PostgreSQL for normalization.

3.2 Model Maintenance

Retrain_model.py

Description: Fetches the improved standard vocabulary created via feedback from the database and saves the new mapping as a joblib normalization model. (Executed via Menu Option [3]).

Train_model.py / Trainer.py / Train_tf.py / Train_torch.py

Description: Scripts responsible for training and optimizing various machine learning models (Logistic Regression, TensorFlow Keras, PyTorch) for tasks like multi-label classification and product type classification, typically using TF-IDF features.