"""
Configuration Module for Tri Health Advisor
=============================================
Centralizes all paths, constants, and settings used across the project.
"""

import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH   = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH     = os.path.join(BASE_DIR, "artifacts", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "artifacts", "vectorizer.pkl")

# ── Model Training Settings ─────────────────────────────────────────────────
TEST_SIZE    = 0.20   # 20 % of data reserved for testing
RANDOM_STATE = 42     # Seed for reproducibility
MAX_FEATURES = 5000   # Top TF-IDF terms to keep
MAX_ITER     = 1000   # Logistic Regression max iterations

# ── Flask Settings ───────────────────────────────────────────────────────────
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
