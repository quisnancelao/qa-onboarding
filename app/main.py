"""API mínima y aislada para demostrar pruebas de seguimiento."""

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class TrackingRequest(BaseModel):
    merchant_name: str = Field(min_length=1)
    product_code: str = Field(min_length=1)


def create_app() -> FastAPI:
    app = FastAPI(title="Onboarding QA - simulador")
    trackings: dict[str, dict[str, str]] = {}

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

    return app


app = create_app()
