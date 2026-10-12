# TriHealth Advisor

TriHealth Advisor is an **educational machine-learning prototype** that classifies short symptom descriptions into labels from a small example dataset and demonstrates how user-selected weights affect a weighted-sum score calculation.

> **Health and safety notice:** This project is not a medical device, diagnostic tool, or source of treatment advice. Its predictions may be wrong. The comparison scores are hard-coded illustrative values, not clinical evidence and not validated rankings of medical systems. Do not use the output to make healthcare decisions or choose medicines. Contact a qualified healthcare professional for medical concerns; seek emergency care for severe or urgent symptoms.

## Features

- Text classification using TF-IDF features and Logistic Regression.
- Flask REST API with request validation.
- Interactive HTML/CSS/JavaScript interface.
- User-adjustable weights for speed, safety, cost, and effectiveness.
- Demonstration of weighted-sum scoring and a Chart.js comparison chart.
- Training evaluation with accuracy and per-label precision, recall, and F1-score.

## Tech stack

- Python, Flask, Flask-CORS
- pandas, scikit-learn
- HTML, CSS, vanilla JavaScript, Chart.js

## Project structure

```text
TriHealthAdvisor/
├── app.py                 # Flask API and prediction endpoint
├── config.py              # Paths and local server settings
├── dataset.csv            # Example labeled text dataset
├── db_simulator.py        # Neutral educational text lookup
├── mcda.py                # Illustrative weighted-sum calculation
├── train_model.py         # Data preparation, training, evaluation
├── artifacts/
│   ├── model.pkl
│   └── vectorizer.pkl
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── images/
├── tests/
└── requirements.txt
```

## Setup

Use Python 3.10 or newer if possible. From the project root:

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
# Windows PowerShell
.venv\\Scripts\\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Train and evaluate the model (this recreates the saved artifacts):

```bash
python train_model.py
```

Start the API:

```bash
python app.py
```

The API listens on `http://127.0.0.1:5000` by default. Open `frontend/index.html` in a browser to use the interface. The page calls the local API, so the Flask server must remain running. If the browser blocks local requests in your setup, serve the `frontend` directory using a local static-file server and keep the API running.

## API

`POST /predict`

Example request:

```json
{
  "text": "I have a fever and chills",
  "preferences": {
    "speed": 5,
    "safety": 8,
    "cost": 6,
    "effectiveness": 7
  }
}
```

The response contains the predicted dataset label, neutral demo descriptions, the illustrative criteria, the weighted scores, and a notice explaining the limitations. The API rejects missing/non-string/empty text, text longer than 2,000 characters, and preference values outside 1–10.

## How it works

1. `train_model.py` loads `dataset.csv`, removes missing/duplicate text-label rows, creates a stratified train/test split, fits TF-IDF on the training text, and trains Logistic Regression.
2. It prints accuracy and per-label precision, recall, and F1-score, then saves the model and vectorizer under `artifacts/`.
3. `app.py` validates the incoming request, transforms the text with the saved vectorizer, and predicts one of the dataset labels.
4. `db_simulator.py` returns neutral placeholder information; it does not provide medicine recommendations.
5. `mcda.py` applies user-selected weights to hard-coded illustrative values and returns a score for charting. These values are only for demonstrating an algorithm and do not establish clinical safety, effectiveness, or suitability.

## Limitations

- The dataset is small and appears to contain template-like examples. Test-set metrics do not establish real-world clinical accuracy.
- The model predicts dataset labels, not diagnoses, and may return incorrect labels for symptoms outside its training examples.
- The comparison criteria and scores are illustrative and have not been clinically validated.
- The treatment lookup intentionally does not recommend specific medicines or remedies.
- The saved `.pkl` files should only be loaded from trusted sources. Pickle files can execute code when loaded.

## Tests

Run:

```bash
python -m unittest discover -s tests -v
```

## License and dataset

Before redistributing the dataset or model artifacts, verify that you have permission to publish them. Add a license only after deciding what license applies to your code and confirming the dataset's terms.
