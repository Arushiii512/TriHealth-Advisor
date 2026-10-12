"""Illustrative multi-criteria scoring for the TriHealth Advisor demo.

IMPORTANT: These are hard-coded demonstration values, not clinical evidence.
They must not be interpreted as rankings of medical systems or treatments.
"""
import math
CRITERIA = ("Speed", "Safety", "Cost", "Effectiveness")
SYSTEMS = ("Allopathy", "Ayurveda", "Homeopathy")

# Illustrative values solely to demonstrate a configurable weighted-sum algorithm.
# Cost is represented as an expense score, so lower cost values are treated as
# more affordable by inverting the value during aggregation.
ILLUSTRATIVE_SCORES = {
    "Allopathy": {"Speed": 9, "Safety": 4, "Cost": 8, "Effectiveness": 9},
    "Ayurveda": {"Speed": 5, "Safety": 9, "Cost": 4, "Effectiveness": 6},
    "Homeopathy": {"Speed": 3, "Safety": 10, "Cost": 2, "Effectiveness": 5},
}


def compute_weighted_score(scores: dict, weights: dict) -> float:
    """Return an illustrative weighted score on a 0-10 scale."""
    required_weights = [key.lower() for key in CRITERIA]

    if not isinstance(weights, dict):
        raise ValueError("Weights must be provided as a dictionary.")

    if any(key not in weights for key in required_weights):
        raise ValueError("A weight is required for every criterion.")

    validated_weights = {}

    for key in required_weights:
        try:
            weight = float(weights[key])
        except (TypeError, ValueError):
            raise ValueError(f"Invalid weight for {key}.")

        if not math.isfinite(weight) or not 0 <= weight <= 10:
            raise ValueError(f"Weight for {key} must be between 0 and 10.")

        validated_weights[key] = weight

    total_weight = sum(validated_weights.values())

    if total_weight <= 0:
        raise ValueError("At least one weight must be positive.")

    weighted_total = 0.0

    for criterion in CRITERIA:
        if criterion not in scores:
            raise ValueError(f"Missing score for {criterion}.")

        try:
            value = float(scores[criterion])
        except (TypeError, ValueError):
            raise ValueError(f"Invalid score for {criterion}.")

        if not math.isfinite(value) or not 1 <= value <= 10:
            raise ValueError(
                f"Score for {criterion} must be between 1 and 10."
            )

        criterion_score = 10 - value if criterion == "Cost" else value
        weighted_total += (
            validated_weights[criterion.lower()] * criterion_score
        )

    return round(weighted_total / total_weight, 2)



def compare_treatments(weights: dict) -> dict:
    """Compare demonstration scores; the top score is not a medical recommendation."""
    scores = {
        system: compute_weighted_score(criteria, weights)
        for system, criteria in ILLUSTRATIVE_SCORES.items()
    }
    return {
        "scores": scores,
        "criteria": ILLUSTRATIVE_SCORES,
        "top_scoring_example": max(scores, key=scores.get),
    }


def get_treatment_recommendation(symptom: str, weights: dict) -> dict:
    """Return compatibility-shaped results for the frontend without medical advice."""
    comparison = compare_treatments(weights)
    return {
        "predicted_symptom": symptom,
        "comparison_scores": comparison["scores"],
        "detailed_criteria": comparison["criteria"],
        "top_scoring_example": comparison["top_scoring_example"],
    }


if __name__ == "__main__":
    example_weights = {key: 5 for key in ("speed", "safety", "cost", "effectiveness")}
    print("Illustrative weighted scores (not clinical evidence):")
    for system, score in compare_treatments(example_weights)["scores"].items():
        print(f"{system}: {score:.2f}/10")