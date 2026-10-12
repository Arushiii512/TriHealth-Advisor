"""Basic validation tests for the local Flask API."""
import unittest

from app import app
from mcda import compare_treatments


class ApiValidationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_missing_json_is_rejected(self):
        response = self.client.post("/predict", json=None)
        self.assertEqual(response.status_code, 400)

    def test_non_string_text_is_rejected(self):
        response = self.client.post("/predict", json={"text": 123})
        self.assertEqual(response.status_code, 400)

    def test_empty_text_is_rejected(self):
        response = self.client.post("/predict", json={"text": "   "})
        self.assertEqual(response.status_code, 400)

    def test_out_of_range_weight_is_rejected(self):
        response = self.client.post(
            "/predict", json={"text": "fever", "preferences": {"safety": 11}}
        )
        self.assertEqual(response.status_code, 400)

    def test_non_finite_weight_is_rejected(self):
        response = self.client.post(
            "/predict", json={"text": "fever", "preferences": {"safety": "NaN"}}
        )
        self.assertEqual(response.status_code, 400)

    def test_valid_request_has_frontend_fields(self):
        response = self.client.post(
            "/predict",
            json={"text": "I am experiencing high fever today", "preferences": {
                "speed": 5, "safety": 5, "cost": 5, "effectiveness": 5
            }},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("predicted_symptom", payload)
        self.assertIn("treatment_details", payload)
        self.assertIn("comparison_scores", payload)
        self.assertIn("detailed_criteria", payload)
        self.assertIn("top_scoring_example", payload)
        self.assertIn("comparison_notice", payload)

    def test_weights_change_demo_scores(self):
        speed_focused = compare_treatments({"speed": 10, "safety": 1, "cost": 1, "effectiveness": 1})
        safety_focused = compare_treatments({"speed": 1, "safety": 10, "cost": 1, "effectiveness": 1})
        self.assertNotEqual(speed_focused["scores"], safety_focused["scores"])


if __name__ == "__main__":
    unittest.main()
