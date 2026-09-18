"""Pruebas de notificaciones de pago duplicadas."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app


def test_identical_notifications_process_payment_once() -> None:
    # Cada prueba usa una aplicación nueva para mantener los datos aislados.
    with TestClient(create_app()) as client:
        created = client.post(
            "/trackings",
            json={
                "merchant_name": "Comercio QA sintético",
                "product_code": "POS-QA",
            },
        )
        assert created.status_code == 201, created.text
        tracking_id = created.json()["tracking_id"]

        initial = client.get(f"/qa/metrics/{tracking_id}")
        assert initial.status_code == 200, initial.text
        initial_stock = initial.json()["inventory_remaining"]

        notification = {
            "tracking_id": tracking_id,
            "idempotency_key": f"qa-{uuid4()}",
            "result": "APPROVED",
        }

        first = client.post("/payments/notifications", json=notification)
        second = client.post("/payments/notifications", json=notification)

        assert first.status_code == 200, first.text
        assert second.status_code == 200, second.text
        assert first.json() == {
            "tracking_id": tracking_id,
            "status": "PAID",
            "duplicate": False,
        }
        assert second.json() == {
            "tracking_id": tracking_id,
            "status": "PAID",
            "duplicate": True,
        }

        metrics = client.get(f"/qa/metrics/{tracking_id}")
        assert metrics.status_code == 200, metrics.text
        assert metrics.json() == {
            "tracking_id": tracking_id,
            "payment_operations": 1,
            "inventory_discounts": 1,
            "inventory_remaining": initial_stock - 1,
        }

        tracking = client.get(f"/trackings/{tracking_id}")
        assert tracking.status_code == 200, tracking.text
        assert tracking.json()["status"] == "PAID"


def test_key_cannot_be_reused_for_another_tracking() -> None:
    with TestClient(create_app()) as client:
        first = client.post(
            "/trackings",
            json={"merchant_name": "QA uno", "product_code": "POS-QA"},
        )
        second = client.post(
            "/trackings",
            json={"merchant_name": "QA dos", "product_code": "POS-QA"},
        )
        assert first.status_code == second.status_code == 201

        key = f"qa-{uuid4()}"

        accepted = client.post(
            "/payments/notifications",
            json={
                "tracking_id": first.json()["tracking_id"],
                "idempotency_key": key,
                "result": "APPROVED",
            },
        )
        rejected = client.post(
            "/payments/notifications",
            json={
                "tracking_id": second.json()["tracking_id"],
                "idempotency_key": key,
                "result": "APPROVED",
            },
        )

        assert accepted.status_code == 200
        assert rejected.status_code == 409

        second_tracking = client.get(
            f"/trackings/{second.json()['tracking_id']}"
        )
        assert second_tracking.status_code == 200
        assert second_tracking.json()["status"] == "CREATED"