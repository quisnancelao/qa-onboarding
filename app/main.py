"""API mínima y aislada para demostrar pruebas de seguimiento."""

from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class TrackingRequest(BaseModel):
    merchant_name: str = Field(min_length=1)
    product_code: str = Field(min_length=1)


class PaymentNotification(BaseModel):
    tracking_id: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    result: str = Field(pattern="^APPROVED$")


def create_app() -> FastAPI:
    app = FastAPI(title="Onboarding QA - simulador")
    trackings: dict[str, dict[str, str]] = {}
    inventory = {"POS-QA": 5}
    processed: dict[str, dict[str, str]] = {}
    payment_operations = 0
    inventory_discounts = 0
    payment_lock = Lock()

    @app.post("/trackings", status_code=201)
    def create_tracking(payload: TrackingRequest) -> dict[str, str]:
        tracking = {
            "tracking_id": f"TRK-QA-{uuid4().hex[:12]}",
            "merchant_name": payload.merchant_name,
            "product_code": payload.product_code,
            "status": "CREATED",
        }
        trackings[tracking["tracking_id"]] = tracking
        return tracking

    @app.get("/trackings/{tracking_id}")
    def get_tracking(tracking_id: str) -> dict[str, str]:
        tracking = trackings.get(tracking_id)
        if tracking is None:
            raise HTTPException(status_code=404, detail="Tracking not found")
        return tracking

    @app.post("/payments/notifications")
    def confirm_payment(payload: PaymentNotification) -> dict[str, object]:
        nonlocal payment_operations, inventory_discounts

        with payment_lock:
            existing = processed.get(payload.idempotency_key)

            if existing is not None:
                if (
                    existing["tracking_id"] != payload.tracking_id
                    or existing["result"] != payload.result
                ):
                    raise HTTPException(
                        status_code=409,
                        detail="Idempotency key already used for another operation",
                    )
                return {
                    "tracking_id": payload.tracking_id,
                    "status": "PAID",
                    "duplicate": True,
                }

            tracking = trackings.get(payload.tracking_id)
            if tracking is None:
                raise HTTPException(status_code=404, detail="Tracking not found")

            code = tracking["product_code"]
            if inventory.get(code, 0) < 1:
                raise HTTPException(status_code=409, detail="Product unavailable")

            if tracking["status"] != "CREATED":
                raise HTTPException(status_code=409, detail="Tracking already processed")

            inventory[code] -= 1
            inventory_discounts += 1
            payment_operations += 1
            tracking["status"] = "PAID"
            processed[payload.idempotency_key] = {
                "tracking_id": payload.tracking_id,
                "result": payload.result,
            }

            return {
                "tracking_id": payload.tracking_id,
                "status": "PAID",
                "duplicate": False,
            }

    @app.get("/qa/metrics/{tracking_id}")
    def transaction_metrics(tracking_id: str) -> dict[str, object]:
        tracking = trackings.get(tracking_id)
        if tracking is None:
            raise HTTPException(status_code=404, detail="Tracking not found")

        return {
            "tracking_id": tracking_id,
            "payment_operations": payment_operations,
            "inventory_discounts": inventory_discounts,
            "inventory_remaining": inventory.get(tracking["product_code"], 0),
        }

    return app


app = create_app()