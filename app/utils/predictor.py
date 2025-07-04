# app/utils/predictor.py

import joblib

# Load the trained model from the model directory
import os
model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "model", "sensitive_data_classifier.pkl")
model = joblib.load(model_path)


def predict_sensitivity(text):
    """
    Predicts if the input text is sensitive.
    Returns 1 for sensitive, 0 for non-sensitive.
    """
    return model.predict([text])[0]
