import pytest
from fastapi.testclient import TestClient
from core.api import app
import os
import httpx # Still keep httpx for version check, though not directly used for client

print(f"DEBUG: httpx version: {httpx.__version__}")

os.environ["API_KEY"] = "your-secret-api-key"

def test_trading_journal_api(): 
    client = TestClient(app)
    
    # Create a trade
    trade_data = {
        "pair": "EURUSD",
        "bias": "long",
        "setup": "test setup",
        "entry": 1.1,
        "target": 1.2,
        "stop": 1.0,
        "rr": 2.0,
    }
    response = client.post("/api/trading/journal", json=trade_data, headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 200
    trade_id = response.json()["id"]

    # Get all trades
    response = client.get("/api/trading/journal", headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Get a single trade
    response = client.get(f"/api/trading/journal/{trade_id}", headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 200
    assert response.json()["pair"] == "EURUSD"

    # Update a trade
    updated_trade_data = {
        "pair": "GBPUSD",
        "bias": "short",
        "setup": "test setup updated",
        "entry": 1.3,
        "target": 1.2,
        "stop": 1.4,
        "rr": 1.0,
    }
    response = client.put(f"/api/trading/journal/{trade_id}", json=updated_trade_data, headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 200
    assert response.json()["pair"] == "GBPUSD"

    # Delete a trade
    response = client.delete(f"/api/trading/journal/{trade_id}", headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 200

    # Verify the trade is deleted
    response = client.get(f"/api/trading/journal/{trade_id}", headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 404

def test_validation_history_api(): 
    client = TestClient(app)
    
    # There is no way to create a validation via the API yet, so I will add one to the db directly
    from core.validation_history import db, Validation
    validation = Validation(id="test-validation", drawing="test-drawing", status="success", result={"details": "all good"})
    db[validation.id] = validation

    # Get all validations
    response = client.get("/api/cad/validations/recent", headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Get a single validation
    response = client.get("/api/cad/validations/test-validation", headers={"X-API-Key": "your-secret-api-key"})
    assert response.status_code == 200
    assert response.json()["drawing"] == "test-drawing"