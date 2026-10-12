"""
Flask API — Tri Health Advisor
================================
Endpoints:
  POST /predict
    • Accepts JSON  { "text": "<user symptoms>" }
    • Returns JSON with:
        – predicted symptom category
        – treatment details from simulated DB
        – MCDA comparison scores
        – recommended treatment system

Run:
    python app.py
"""

import math
import os
import pickle

from flask import Flask, request, jsonify
from flask_cors import CORS

from config import MODEL_PATH, VECTORIZER_PATH, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from mcda import get_treatment_recommendation
from db_simulator import get_treatment_details

def validate_weights(weights):
    """Validate the four preference weights supplied by the client."""
    required = ("speed", "safety", "cost", "effectiveness")

    if not isinstance(weights, dict):
        return False, "weights must be a JSON object."

    for key in required:
        if key not in weights:
            return False, f"Missing weight: {key}."

        try:
            value = float(weights[key])
        except (TypeError, ValueError):
            return False, f"Weight '{key}' must be numeric."

        if not math.isfinite(value) or not 0 <= value <= 10:
            return False, f"Weight '{key}' must be between 0 and 10."

    if sum(float(weights[key]) for key in required) <= 0:
        return False, "At least one weight must be positive."

    return True, None

# ── Initialize Flask app ─────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)


# ── Load saved model & vectorizer ────────────────────────────────────────────
def load_artifacts():
    """Load the trained model and TF-IDF vectorizer from disk."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at '{MODEL_PATH}'. "
            "Run  train_model.py  first to create it."
        )
    if not os.path.exists(VECTORIZER_PATH):
        raise FileNotFoundError(
            f"Vectorizer file not found at '{VECTORIZER_PATH}'. "
            "Run  train_model.py  first to create it."
        )

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    print("[INFO] Model and vectorizer loaded successfully.")
    return model, vectorizer


# Load once at import time so every request reuses the same objects
model, vectorizer = load_artifacts()


# ── POST /predict ────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict the symptom category from user-supplied text and return
    a full advisory response.

    Request JSON
    -------------
    {
        "text": "I have a severe headache and nausea"
    }

    Response JSON
    --------------
    {
        "predicted_symptom": "Migraine",
        "treatment_details": { ... },
        "top_scoring_example": "Allopathy",
        "comparison_scores": { ... },
        "detailed_criteria": { ... }
    }
    """
    # ── 1. Validate input ────────────────────────────────────────────────
    data = request.get_json(silent=True)
    
    if not isinstance(data, dict) or "text" not in data:
        return jsonify({
            "error": "Invalid request. Send a JSON object with a 'text' string.",
            "example": {"text": "I have fever and chills"},
        }), 400

    if not isinstance(data["text"], str):
        return jsonify({"error": "'text' must be a string."}), 400

    user_text = data["text"].strip()
    if not user_text:
        return jsonify({"error": "'text' field must not be empty."}), 400
    if len(user_text) > 2000:
        return jsonify({"error": "'text' must be 2000 characters or fewer."}), 400


    # User preferences are weights, not clinical recommendations.
    prefs = data.get("weights", data.get("preferences", {}))

    valid, error = validate_weights(prefs)
    if not valid:
        return jsonify({"error": error}), 400

    weights = {key: float(prefs[key]) for key in
            ("speed", "safety", "cost", "effectiveness")}


    # ── 2. Predict symptom category ──────────────────────────────────────
    text_tfidf = vectorizer.transform([user_text])
    predicted_symptom = model.predict(text_tfidf)[0]

    # ── 3. Fetch treatment details from simulated DB ─────────────────────
    treatment_info = get_treatment_details(predicted_symptom)

    # ── 4. Run MCDA comparison ───────────────────────────────────────────
    mcda_result = get_treatment_recommendation(predicted_symptom, weights)

    # ── 5. Build final response ──────────────────────────────────────────
    response = {
        "predicted_symptom": predicted_symptom,
        "treatment_details": treatment_info["treatments"],
        "comparison_scores": mcda_result["comparison_scores"],
        "detailed_criteria": mcda_result["detailed_criteria"],
        "top_scoring_example": mcda_result["top_scoring_example"],
        "comparison_notice": (
            "Scores are illustrative software-demo values, not clinical evidence. "
            "This tool does not diagnose conditions or recommend treatment."
        ),
    }

    return jsonify(response), 200


# ── Health-check endpoint (optional) ─────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    """Simple root endpoint to verify the API is running."""
    return jsonify({
        "service": "Tri Health Advisor API",
        "status":  "running",
        "usage":   "POST /predict  with JSON { \"text\": \"<symptoms>\" }",
    })


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🏥  Tri Health Advisor API — Starting …")
    print(f"   Listening on http://{FLASK_HOST}:{FLASK_PORT}\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
