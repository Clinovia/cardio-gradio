# test_api.py
import pytest
from fastapi.testclient import TestClient
from app.api.routes import router
from fastapi import FastAPI

# Create a test FastAPI app and include the router
app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "healthy" in data["message"].lower()


def test_predict_success(monkeypatch):
    # Mock the run_cardio_inference function to return predictable values
    def mock_inference(data):
        return 75.0, "high"

    monkeypatch.setattr("app.services.inference.run_cardio_inference", mock_inference)

    payload = {
        "age": 60,
        "gender": "male",
        "systolic_bp": 145,
        "diastolic_bp": 95,
        "cholesterol": 220,
        "smoking_status": "current",
        "diabetes": True,
        "heart_rate": 88,
        "bmi": 28.4,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] == 75.0
    assert data["risk_category"] == "high"
    assert "75.0%" in data["explanation"]


def test_predict_failure(monkeypatch):
    # Mock inference to raise an error
    def mock_inference(data):
        raise ValueError("Mock failure")

    monkeypatch.setattr("app.services.inference.run_cardio_inference", mock_inference)

    payload = {
        "age": 50,
        "gender": "female",
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "cholesterol": 180,
        "smoking_status": "never",
        "diabetes": False,
        "heart_rate": 72,
        "bmi": 23.0,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 500
    data = response.json()
    assert "Mock failure" in data["detail"]
