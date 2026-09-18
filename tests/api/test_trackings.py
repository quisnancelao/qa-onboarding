from fastapi.testclient import TestClient

from app.main import create_app


def test_create_and_read_tracking() -> None:
    with TestClient(create_app()) as client:
        created = client.post(
            "/trackings",
            json={"merchant_name": "Comercio QA", "product_code": "POS-QA"},
        )
        assert created.status_code == 201
        body = created.json()
        assert body["tracking_id"].startswith("TRK-QA-")
        assert body["status"] == "CREATED"

        fetched = client.get(f"/trackings/{body['tracking_id']}")
        assert fetched.status_code == 200
        assert fetched.json() == body


def test_reject_missing_merchant_name() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/trackings", json={"product_code": "POS-QA"})
        assert response.status_code == 422
        assert any("merchant_name" in str(error["loc"]) for error in response.json()["detail"])


def test_unknown_tracking_returns_404() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/trackings/TRK-QA-NOT-FOUND")
        assert response.status_code == 404
        assert response.json() == {"detail": "Tracking not found"}
