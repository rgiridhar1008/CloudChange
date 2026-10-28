import logging
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("api-gateway")

app = FastAPI(title="API Gateway")

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003")

class CheckoutRequest(BaseModel):
    user_id: int
    item: str
    amount: float

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "service": "api-gateway"}

@app.post("/api/checkout")
async def checkout(request: CheckoutRequest):
    logger.info(f"Received checkout request for user {request.user_id}, item {request.item}")
    
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Forwarding to order service at {ORDER_SERVICE_URL}/orders")
            payload = {"user_id": request.user_id, "item": request.item, "amount": request.amount}
            order_response = await client.post(f"{ORDER_SERVICE_URL}/orders", json=payload)
            if order_response.status_code != 200:
                raise HTTPException(status_code=order_response.status_code, detail="Checkout failed at order service")
            return order_response.json()
        except httpx.RequestError as exc:
            logger.error(f"Error contacting order service: {exc}")
            raise HTTPException(status_code=503, detail="Order service unavailable")
