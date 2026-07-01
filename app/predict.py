import joblib, numpy as np

bundle = joblib.load("ml/artifacts/model.joblib")
model = bundle["model"]
SYMPTOMS = bundle["symptoms"]
IMPORTANCE = bundle["importance"]
THRESHOLD = 0.40

def predict(active_symptoms):
    x = np.array([[1 if s in active_symptoms else 0 for s in SYMPTOMS]])
    probs = model.predict_proba(x)[0]
    top = int(probs.argmax())
    disease = str(model.classes_[top])
    confidence = float(probs[top])
    reasons = sorted(active_symptoms, key=lambda s: IMPORTANCE.get(s, 0), reverse=True)[:3]
    if confidence < THRESHOLD:
        return {"low_confidence": True,
                "message": "Not confident enough to suggest a condition. Please consult a general physician.",
                "confidence": round(confidence, 3), "top_symptoms": reasons}
    return {"low_confidence": False, "disease": disease,
            "confidence": round(confidence, 3), "top_symptoms": reasons}