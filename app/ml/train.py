from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

MODEL_PATH = Path("app/ml/artifacts/complexity_model.joblib")
TRAINING_DATA_PATH = Path("data/training/synthetic_claims.csv")

FEATURE_COLUMNS = [
    "amount",
    "claim_type_auto",
    "claim_type_property",
    "doc_count",
    "text_length",
    "missing_fields",
    "has_police",
    "has_fire",
    "has_injury",
    "has_legal",
    "has_pending",
]


def train_and_save_model() -> None:
    df = pd.read_csv(TRAINING_DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df["complexity_label"]

    model = LogisticRegression(
        max_iter=1000,
        multi_class="auto",
        random_state=42,
    )
    model.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_columns": FEATURE_COLUMNS,
            "model_version": "complexity-logreg-v1",
        },
        MODEL_PATH,
    )
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save_model()