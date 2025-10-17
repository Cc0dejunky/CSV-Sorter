    v AI_Project_Root (folder)
        ○ Consolidate_feedback.py
            § **Does:** Consolidates human-provided corrections from the `training_feedback` table into the master `standard_vocabulary` table. This is a crucial step for improving the model over time.
            § **Trigger:** Executed as a scheduled or manual maintenance task to process batches of user feedback.
            § **Uses:** `psycopg2` for direct database interaction to read from one table and write to another.
        ○ CSV_Processor.py
            § **Does:** Reads a local CSV file, applies a pre-trained `joblib` model for color normalization, generates text embeddings for product names, and directly inserts the processed data into the `products` table.
            § **Trigger:** Designed to be run as a command-line script or imported by another process. It is invoked by calling its `process_csv_upload(file_path)` function.
            § **Uses:** `pandas.read_csv`, `joblib.load`, `psycopg2.connect`, `EmbeddingGenerator.generate_embedding`.
        ○ Enbedding_generator.py
            § It processes new products, generates text embeddings, and updates the PostgreSQL database.
        ○ Refactor_imports.py
            § This script refactors deprecated Python import statements across an entire project directory using regular expressions.
        ○ Retrain_model.py
            § **Does:** Fetches the complete, consolidated vocabulary from the `standard_vocabulary` table and creates a simple dictionary-based mapping model. It then saves this model to a file using `joblib`.
            § **Trigger:** Executed as a command-line script (`python AI_Project_Root/retrain_model.py`) after `consolidate_feedback.py` has been run. This creates the model file used by the FastAPI server and other components.
            § **Uses:** `psycopg2` to fetch data, `joblib.dump` to save the model.
    v Pycache.py (folder)
        ○ Data (folder)
            § Processed (folder)
                □ Optimizer_training.csv
                    ® Description
                □ Training-data.jsonl
                    ® Description
                □ Training-data.jsonl
                    ® Description
            § Raw (folder)
                □ Library.json
                    ® Description
                □ Product.csv
                    ® Description
                □ Vocabulary.db
                    ® Description
                □ Vocabulary.json
                    ® Description
        ○ Models (folder)
            § Pytorch (folder)
            § Tensorflow (folder)
        ○ SRC (folder)
            § _pycache
            § Core (folder)
                □ __init__.py
                □ Config.py
                    ® This script defines central project file paths, configuration directories, and default machine learning training hyperparameters.
                □ Database.manager.py
                    ® Initializes a structured SQLite database schema and imports vocabulary data and aliases from a JSON file.
                □ Data_generator.py
                    ® The code normalizes product titles from a CSV into structured attributes using dictionary-based vocabulary lookups for training data generation.
                □ Vector_db_manager.py
                    ® This script connects to a PostgreSQL database using environment variables and queries product data.
            § Data (folder)
                □ Generate_embeddings.py
                    ® The script generates product embeddings and inserts the resulting vectors into a Postgres database.
                □ Upsert_embedding_exampe.py
                    ® The script inserts a product's vector embedding into a PostgreSQL database table using psycopg2.
            § Integration (folder)
                □ Webhook_handler_example.py
                    ® A Flask application processes Shopify product webhooks and updates database records via PostgreSQL.
            § Optimizer
                □ Generate_training_data.py
                    ® The script processes product CSV data, extracting text and heuristic labels for machine learning training.
                □ Infer.py
                    ® This module loads saved machine learning models to predict and return corresponding labels for input text.
                □ Integration.py
                    ® The code acts as a backend integration layer for training models and predicting product tags via subprocesses and lazy inference.
                □ README.md
                □ Train_model.py
                    ® Trains and saves a OneVsRest Logistic Regression model for multilabel text classification using TF-IDF features.
            § Training
                □ Trainer.py
                    ® The script trains and optimizes a multi-label text classification model using TF-IDF and OneVsRest.
                □ Train_tf.py
                    ® The code trains and saves a TensorFlow Keras model to classify product types based on combined title and body text.
                □ Train_torch.py
                    ® Trains and saves a PyTorch product classifier model using TF-IDF features extracted from text data.
    v Main.py(root file)
        ○ **Does:** Provides the central API for the entire application. It handles incoming data (webhooks, bulk uploads), applies the ML model for normalization, serves products for review, and accepts human feedback.
        ○ **Trigger:** Run as a web server using `uvicorn`. Its endpoints are called by the `review_tui.py` application and external services like Shopify webhooks.
        ○ **Uses:** `fastapi` to define endpoints (`/get_products_for_review`, `/submit_feedback`, `/bulk_stage_data`, `/reload_model`), `psycopg2` for all database operations, and `joblib.load` to use the normalization model.
    v CSV_Processor.py(root file)
        ○ Reads CSV data, applies normalization and embeddings, then inserts the processed records into a PostgreSQL database.
    v Database.py(root file)
        ○ This code initializes an SQLite database and provides full CRUD functions for product data, variants, and controlled vocabulary.
    v Extract_shopify_data.py(root file)
        ○ Extracts Shopify product data, converts it to a DataFrame, and loads it into PostgreSQL.
    v Generate_flowchart.py(root file)
            ○ **Does:** A utility script that takes a Python file as an argument and generates a visual flowchart of its code in an HTML file.
            § **Trigger:** Executed manually from the command line (`python generate_flowchart.py <filename.py>`) to aid in documentation and understanding code flow.
            § **Uses:** The `py2flowchart` library to perform the conversion.
