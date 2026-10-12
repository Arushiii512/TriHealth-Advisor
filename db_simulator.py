
"""Educational lookup for symptom labels.

This module provides general educational information only.
It does not diagnose users or recommend treatments or medicines.
"""

SYSTEMS = ("Allopathy", "Ayurveda", "Homeopathy")

TREATMENT_DB = {
    label: {
        system: (
            f"No verified, symptom-specific information about {system} "
            f"is available for {label} in this demo. "
            "Please consult a qualified healthcare professional."
        )
        for system in SYSTEMS
    }
    for label in (
        "Fever", "Cold", "Migraine", "Indigestion", "Body Pain",
        "Fatigue", "Sore Throat", "Cough", "Nausea", "Allergy",
        "Headache", "Diarrhea", "Skin Rash", "Dizziness", "Chest Pain",
    )
}


def get_treatment_details(symptom: str) -> dict:
    """Return educational information for the predicted category."""
    details = TREATMENT_DB.get(symptom)

    if details is None:
        details = {
            system: "No information is available for this category."
            for system in SYSTEMS
        }

    return {
        "symptom": symptom,
        "treatments": dict(details),
    }
