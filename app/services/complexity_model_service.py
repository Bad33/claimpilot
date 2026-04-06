from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path("app/ml/artifacts/complexity_model.joblib")


class ComplexityModelService:
    _bundle = None

    @classmethod
    def _load_bundle(cls):
        if cls._bundle is None:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Model artifact not found at {MODEL_PATH}. Run training first."
                )
            cls._bundle = joblib.load(MODEL_PATH)
        return cls._bundle

    @classmethod
    def predict(cls, feature_dict: dict) -> dict:
        bundle = cls._load_bundle()
        model = bundle["model"]
        feature_columns = bundle["feature_columns"]
        model_version = bundle["model_version"]

        X = pd.DataFrame([feature_dict])[feature_columns]
        probabilities = model.predict_proba(X)[0]
        classes = model.classes_

        best_idx = probabilities.argmax()
        predicted_label = classes[best_idx]
        predicted_score = float(probabilities[best_idx])

        probability_map = {
            str(label): float(prob)
            for label, prob in zip(classes, probabilities)
        }

        return {
            "complexity_label": str(predicted_label),
            "complexity_score": predicted_score,
            "probabilities": probability_map,
            "model_version": model_version,
        }