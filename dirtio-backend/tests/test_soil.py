from fastapi.testclient import TestClient
import os
import importlib
import pytest
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from soil import app


client = TestClient(app)

# you need to run `pytest -s` to see this output. It will always succeed.
def test_routes():
    print("\nRegistered routes:")
    for route in app.routes:
        print(f"{route.path} -- {route.name}")

def test_invalid_range_lat_lon():
    """
    Calls with invalid lat/lon should fail quickly and not hit the Database,
    returning 422 Unprocessable Entity (FastAPI validation error).
    """
    response = client.get("/soil", params={"lon": -200.0, "lat": 37.49})
    assert response.status_code == 422

    response = client.get("/soil", params={"lon": -122.44, "lat": 100.0})
    assert response.status_code == 422


def test_invalid_type_lat_lon():
    """
    Calls with invalid lat/lon types should fail quickly and not hit the Database,
    returning 422 Unprocessable Entity (FastAPI validation error).
    """
    response = client.get("/soil", params={"lon": "abc", "lat": 37.49})
    assert response.status_code == 422

    response = client.get("/soil", params={"lon": -122.44, "lat": "cde"})
    assert response.status_code == 422
