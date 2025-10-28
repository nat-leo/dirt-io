import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


# ----------------------------
# 1️⃣ Success case (mocked)
# ----------------------------
def test_soil_endpoint_success_mocked():
    mock_response = {
        "data": [
            ["399359807", "456385", "POLYGON ((-122.407560312536 37.4779244261786, ...))"]
        ]
    }

    with patch("main.requests.post") as mock_post:
        # Mock the SDA response
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status.return_value = None

        params = {"lon": -122.449871, "lat": 37.492633}
        response = client.get("/soil", params=params)
        assert response.status_code == 200

        resp = response.json()
        assert "data" in resp

        data = resp["data"]
        assert isinstance(data, list)
        assert data == mock_response["data"]

        # Validate each row
        for i, row in enumerate(data):
            assert isinstance(row, list)
            assert len(row) == 3
            assert isinstance(row[0], int) or isinstance(row[0], str)
            assert isinstance(row[1], int) or isinstance(row[1], str)
            assert isinstance(row[2], str)


# ----------------------------
# 2️⃣ No results case (mocked)
# ----------------------------
def test_soil_endpoint_no_results_mocked():
    mock_response = {"Table": []}

    with patch("main.requests.post") as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status.return_value = None

        params = {"lon": -10.0, "lat": -10.0}  # coordinates with no soil
        response = client.get("/soil", params=params)
        assert response.status_code == 200

        resp = response.json()
        assert "message" in resp
        assert resp["message"] == "No map unit polygons found for given coordinates"


# ----------------------------
# 3️⃣ Missing or invalid parameters
# ----------------------------
def test_soil_endpoint_missing_params():
    # Missing both lon and lat
    response = client.get("/soil")
    assert response.status_code == 422

    # Missing lat
    response = client.get("/soil", params={"lon": -122.449871})
    assert response.status_code == 422

    # Invalid types
    response = client.get("/soil", params={"lon": "abc", "lat": 37.49})
    assert response.status_code == 422
