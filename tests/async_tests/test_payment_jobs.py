"""Pruebas del procesamiento de pagos en segundo plano."""

from time import monotonic, sleep
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app


def esperar_trabajo(client: TestClient, job_id: str) -> dict:
    limite = monotonic() + 3

    while monotonic() < limite:
        response = client.get(f"/qa/payment-jobs/{job_id}")
        assert response.status_code == 200, response.text

        job = response.json()
        if job["status"] in ("COMPLETED", "FAILED"):
            return job

        sleep(0.01)

    raise AssertionError(f"El trabajo {job_id} no terminó en 3 segundos")


def crear_tracking(client: TestClient) -> str:
    response = client.post(
        "/trackings",
        json={
            "merchant_name": "Comercio QA asíncrono",
            "product_code": "POS-QA",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["tracking_id"]


def test_reintento_procesa_pago_una_sola_vez() -> None:
    with TestClient(create_app()) as client:
        tracking_id = crear_tracking(client)

        response = client.post(
            "/qa/payment-jobs",
            json={
                "tracking_id": tracking_id,
                "idempotency_key": f"qa-{uuid4()}",
                "fail_first_attempt": True,
            },
        )
        assert response.status_code == 202, response.text

        job = esperar_trabajo(client, response.json()["job_id"])
        assert job["status"] == "COMPLETED"
        assert job["attempts"] == 2
        assert job["result"] == {
            "tracking_id": tracking_id,
            "status": "PAID",
            "duplicate": False,
        }

        metrics = client.get(f"/qa/metrics/{tracking_id}")
        assert metrics.status_code == 200
        assert metrics.json()["payment_operations"] == 1
        assert metrics.json()["inventory_discounts"] == 1
        assert client.get(f"/trackings/{tracking_id}").json()["status"] == "PAID"


def test_trabajos_duplicados_no_duplican_el_pago() -> None:
    with TestClient(create_app()) as client:
        tracking_id = crear_tracking(client)
        notification = {
            "tracking_id": tracking_id,
            "idempotency_key": f"qa-{uuid4()}",
        }

        first = client.post("/qa/payment-jobs", json=notification)
        second = client.post("/qa/payment-jobs", json=notification)
        assert first.status_code == second.status_code == 202

        first_job = esperar_trabajo(client, first.json()["job_id"])
        second_job = esperar_trabajo(client, second.json()["job_id"])

        assert first_job["status"] == second_job["status"] == "COMPLETED"
        assert sorted(
            [first_job["result"]["duplicate"], second_job["result"]["duplicate"]]
        ) == [False, True]

        metrics = client.get(f"/qa/metrics/{tracking_id}").json()
        assert metrics["payment_operations"] == 1
        assert metrics["inventory_discounts"] == 1


def test_consultar_trabajo_inexistente_devuelve_404() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/qa/payment-jobs/JOB-INEXISTENTE")
        assert response.status_code == 404