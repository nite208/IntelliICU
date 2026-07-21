"""
Load IntelliICU Production Model
"""

from pathlib import Path

import joblib

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "ml_models"
    / "intelliicu_final_model.pkl"
)

MODEL = joblib.load(MODEL_PATH)