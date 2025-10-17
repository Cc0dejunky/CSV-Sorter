from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
import json
import psycopg2
import joblib
import os

# --- Pydantic Models for Data Validation ---


# Defines the structure for a single item in the bulk upload
class BulkProductItem(BaseModel):
    handle: str
    product_name: str
    raw_color: str | None = None  # Raw color value extracted from the CSV


# Defines the structure for the list of items sent from the TUI
class BulkProductData(BaseModel):
    products: list[BulkProductItem]


# --- Configuration & Globals ---

# FIX: Model path adjusted to look one directory up (../)
# because main.py is in 'desktop_app' and 'models' is typically in the root.
MODEL_PATH = "AI_Project_Root/models/normalization_model.joblib"

DB_HOST = "your-db-host"
DB_NAME = "your-db-name"
DB_USER = "your-db-user"
DB_PASSWORD = "your-db-password"

normalization_model = {}

# --- FastAPI App Instantiation ---
app = FastAPI()


# --- Health Check Endpoint ---
@app.get("/")
def read_root():
    """
    A simple GET endpoint to verify the server is running.
    """
    return {
        "status": "ok",
        "service": "Normalization Backend API",
        "model_loaded": bool(normalization_model),
    }


# --- Model Loading Logic (P-10) ---


def load_normalization_model():
    """
    Loads the normalization model from the .joblib file (P-10 logic).
    """
    global normalization_model
    try:
        # Use os.path.abspath to ensure the path is resolved correctly
        absolute_path = os.path.abspath(MODEL_PATH)
        normalization_model = joblib.load(absolute_path)
        print(f"INFO: Normalization model loaded successfully from {absolute_path}")
    except FileNotFoundError:
        print(
            f"WARN: Normalization model not found at {MODEL_PATH}. Using empty model."
        )
        normalization_model = {}
    except Exception as e:
        print(f"ERROR: Failed loading normalization model: {e}")
        normalization_model = {}


# Load the model at startup
load_normalization_model()

# --- Core Normalization Function (P-4) ---


def normalize_color(raw_color):
    """
    Normalizes a raw color string to a standard value using the loaded model.
    """
    if not raw_color:
        return None
    # Clean the input string by stripping whitespace
    cleaned_color = raw_color.strip()

    # Model returns the standard value if the raw_color (lowercase) is in the dictionary,
    # otherwise it returns the raw_color itself (the 'first guess').
    return normalization_model.get(cleaned_color.lower(), cleaned_color)


# --- Endpoints ---


@app.get("/get_products_for_review")
async def get_products_for_review():
    """
    Endpoint to get all products that need review (P-6 logic).
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, product_name, raw_value, ml_prediction FROM products WHERE needs_review = TRUE"
        )
        products = cursor.fetchall()

        cursor.close()
        conn.close()

        # Convert list of tuples to list of dictionaries
        product_list = [
            {
                "id": p[0],
                "product_name": p[1],
                "raw_value": p[2],
                "ml_prediction": p[3],
            }
            for p in products
        ]

        return product_list

    except psycopg2.Error as e:
        print(f"ERROR: Database error on getting products for review: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        print(f"ERROR: Internal error on getting products for review: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def reload_model():
    """
    Endpoint to trigger model reload after retraining (P-10).
    """
    load_normalization_model()
    return {"status": "success", "message": "Model reloaded."}


@app.post("/shopify_webhook")
async def shopify_webhook(request: Request):
    """
    Accepts Shopify webhook data, normalizes it, and inserts it into the database (P-4).
    """
    try:
        product_data = await request.json()

        shopify_id = product_data.get("id")
        product_name = product_data.get("title")
        tags = product_data.get("tags", "").split(", ")

        # Basic color extraction from tags
        raw_color = None
        for tag in tags:
            if tag.lower().startswith("color:"):
                raw_color = tag.split(":")[1].strip()
                break

        # P-4 Logic: Run the prediction
        ml_prediction = normalize_color(raw_color) if raw_color else None

        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # FIX: Changed INSERT to use raw_value and ml_prediction columns
        cursor.execute(
            """INSERT INTO products (shopify_id, product_name, raw_value, ml_prediction, needs_review)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (shopify_id) DO UPDATE SET
               product_name = EXCLUDED.product_name,
               raw_value = EXCLUDED.raw_value,
               ml_prediction = EXCLUDED.ml_prediction,
               needs_review = EXCLUDED.needs_review;""",
            (
                shopify_id,
                product_name,
                raw_color,
                ml_prediction,
                True,
            ),  # needs_review = True
        )

        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success", "message": f"Product {shopify_id} processed."}

    except psycopg2.Error as e:
        print(f"ERROR: Database error on webhook insert: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        print(f"ERROR: Internal error during webhook processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/bulk_stage_data")
async def bulk_stage_data(data: BulkProductData):
    """
    NEW ENDPOINT (P-11): Accepts a list of products from the TUI CSV upload,
    runs normalization, and stages them in the database for review.
    """
    staged_count = 0
    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()

        for item in data.products:
            raw_color = item.raw_color
            # P-4 Logic: Run the prediction for the raw color
            ml_prediction = normalize_color(raw_color) if raw_color else None

            # FIX: Changed INSERT to use raw_value and ml_prediction columns
            cursor.execute(
                """INSERT INTO products (shopify_id, product_name, raw_value, ml_prediction, needs_review)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (shopify_id) DO UPDATE SET
                   product_name = EXCLUDED.product_name,
                   raw_value = EXCLUDED.raw_value,
                   ml_prediction = EXCLUDED.ml_prediction,
                   needs_review = EXCLUDED.needs_review;""",
                (
                    item.shopify_id,
                    item.product_name,
                    raw_color,
                    ml_prediction,
                    True,
                ),  # needs_review = True
            )
            staged_count += 1

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "staged_count": staged_count,
            "message": f"{staged_count} products staged for review.",
        }

    except psycopg2.Error as e:
        print(f"ERROR: Database error on bulk staging: {e}")
        # Re-raise the error with the internal details for easier debugging
        raise HTTPException(
            status_code=500, detail=f"Database error during bulk insert: {e}"
        )
    except Exception as e:
        print(f"ERROR: Internal error during bulk staging: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/submit_feedback")
async def submit_feedback(request: Request):
    """
    Accepts feedback data and handles the P-7 logic.
    """
    try:
        feedback_data = await request.json()
        product_id = feedback_data.get("product_id")
        raw_value = feedback_data.get("raw_value")
        ml_prediction = feedback_data.get("ml_prediction")
        human_correction = feedback_data.get("human_correction")

        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # 1. Insert into training_feedback
        cursor.execute(
            """INSERT INTO training_feedback (product_id, raw_value, ml_prediction, human_correction)
               VALUES (%s, %s, %s, %s);""",
            (product_id, raw_value, ml_prediction, human_correction),
        )

        # 2. Mark the product as reviewed (P-7 logic) and update its final normalized value
        cursor.execute(
            "UPDATE products SET needs_review = FALSE, normalized_color = %s WHERE id = %s",
            (
                human_correction,
                product_id,
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        # P-7 requires a 201 status for the TUI to show success
        raise HTTPException(
            status_code=201,
            detail=f"Feedback for product {product_id} received and product marked reviewed.",
        )

    except psycopg2.Error as e:
        print(f"ERROR: Database error on feedback insert: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(f"ERROR: Internal error during feedback processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
