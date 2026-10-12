"""
Model Training Pipeline — Tri Health Advisor
=============================================
Steps:
  1. Load a CSV dataset  (columns: "text", "label")
  2. Split into train / test sets  (80 / 20)
  3. TF-IDF feature extraction
  4. Train a Logistic Regression classifier
  5. Evaluate with accuracy score & classification report
  6. Save model + vectorizer with pickle

Run this script once to produce the artifacts used by the Flask API.
"""

import os
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

from config import (
    DATASET_PATH, MODEL_PATH, VECTORIZER_PATH,
    TEST_SIZE, RANDOM_STATE, MAX_FEATURES, MAX_ITER,
)


# ── Step 1: Load the dataset ────────────────────────────────────────────────
def load_dataset(path: str) -> pd.DataFrame:
    """Read the CSV and perform basic validation."""
    df = pd.read_csv(path)

    # Ensure required columns exist
    assert "text"  in df.columns, "CSV must contain a 'text' column."
    assert "label" in df.columns, "CSV must contain a 'label' column."

    # Drop any rows with missing text or label
    df = df.dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip()
    df = df[(df["text"] != "") & (df["label"] != "")]
    before = len(df)
    df = df.drop_duplicates(subset=["text", "label"])
    print(f"[INFO] Removed {before - len(df)} duplicate text/label rows")
    print(f"[INFO] Loaded {len(df)} rows from '{path}'")
    return df


# ── Step 2: Train / Test split ──────────────────────────────────────────────
def split_data(df: pd.DataFrame):
    """Split into 80 % training and 20 % testing."""
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["label"],
    )
    print(f"[INFO] Training samples: {len(X_train)}  |  Testing samples: {len(X_test)}")
    return X_train, X_test, y_train, y_test


# ── Step 3: TF-IDF vectorization ────────────────────────────────────────────
def build_tfidf(X_train, X_test):
    """Fit TF-IDF on training data; transform both sets."""
    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        stop_words="english",
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf  = vectorizer.transform(X_test)
    print(f"[INFO] TF-IDF matrix shape (train): {X_train_tfidf.shape}")
    return vectorizer, X_train_tfidf, X_test_tfidf


# ── Step 4: Train Logistic Regression ────────────────────────────────────────
def train_model(X_train_tfidf, y_train):
    """Train the classifier and return it."""
    model = LogisticRegression(max_iter=MAX_ITER, random_state=RANDOM_STATE)
    model.fit(X_train_tfidf, y_train)
    print("[INFO] Logistic Regression model trained successfully.")
    return model


# ── Step 5: Evaluate ────────────────────────────────────────────────────────
def evaluate_model(model, X_test_tfidf, y_test):
    """Print accuracy and a per-class classification report."""
    y_pred   = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n{'=' * 55}")
    print(f"  Test Accuracy : {accuracy:.4f}  ({accuracy * 100:.2f} %)")
    print(f"{'=' * 55}\n")
    print("Classification Report (per-label precision, recall, F1):")
    print(classification_report(y_test, y_pred, zero_division=0))
    return accuracy


# ── Step 6: Save artifacts with pickle ──────────────────────────────────────
def save_artifacts(model, vectorizer):
    """Persist model and vectorizer to disk."""
    # Create the artifacts directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"[INFO] Model saved to      : {MODEL_PATH}")
    print(f"[INFO] Vectorizer saved to : {VECTORIZER_PATH}")


# ── Main pipeline ────────────────────────────────────────────────────────────
def main():
    """Run the full training pipeline end-to-end."""
    print("\n🏥  Tri Health Advisor — Model Training Pipeline")
    print("=" * 55)

    # 1. Load
    df = load_dataset(DATASET_PATH)

    # 2. Split
    X_train, X_test, y_train, y_test = split_data(df)

    # 3. Vectorize
    vectorizer, X_train_tfidf, X_test_tfidf = build_tfidf(X_train, X_test)

    # 4. Train
    model = train_model(X_train_tfidf, y_train)

    # 5. Evaluate
    evaluate_model(model, X_test_tfidf, y_test)

    # 6. Save
    save_artifacts(model, vectorizer)

    print("\n✅  Training complete — artifacts are ready for the API.\n")


if __name__ == "__main__":
    main()
