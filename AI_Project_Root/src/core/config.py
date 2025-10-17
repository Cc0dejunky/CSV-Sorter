"""config.py

Central configuration for file paths, model parameters, and other settings.
"""
from pathlib import Path

# --- Project Paths ---
# Assumes the script is run from the project root.
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

MODELS_DIR = PROJECT_ROOT / "models"
TF_MODEL_DIR = MODELS_DIR / "tensorflow"
TORCH_MODEL_DIR = MODELS_DIR / "pytorch"
OPTIMIZER_MODEL_DIR = MODELS_DIR / "optimizer"

SRC_DIR = PROJECT_ROOT / "src"

# --- Default Training Parameters ---
class TrainingConfig:
    """Default training hyperparameters."""
    EPOCHS = 10
    BATCH_SIZE = 32
    LEARNING_RATE = 0.001

# Ensure model directories exist
TF_MODEL_DIR.mkdir(parents=True, exist_ok=True)
TORCH_MODEL_DIR.mkdir(parents=True, exist_ok=True)
OPTIMIZER_MODEL_DIR.mkdir(parents=True, exist_ok=True)