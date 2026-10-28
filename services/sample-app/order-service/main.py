import logging
import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("order-service")

app = FastAPI(title="Order Service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8002")

class OrderRequest(BaseModel):
    user_id: int
    item: str
    amount: float

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "service": "order-service"}

@app.post("/orders")
async def create_order(request: OrderRequest):
    logger.info(f"Creating order for user {request.user_id}, item {request.item}")
    
    # 1. Verify user exists
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Calling user service at {USER_SERVICE_URL}/users/{request.user_id}")
            user_response = await client.get(f"{USER_SERVICE_URL}/users/{request.user_id}")
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid user")
        except httpx.RequestError as exc:
            logger.error(f"Error contacting user service: {exc}")
            raise HTTPException(status_code=503, detail="User service unavailable")

    # 2. Process payment
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"Calling payment service at {PAYMENT_SERVICE_URL}/pay")
            payment_payload = {"order_id": 999, "amount": request.amount}
            payment_response = await client.post(f"{PAYMENT_SERVICE_URL}/pay", json=payment_payload)
            if payment_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Payment failed")
        except httpx.RequestError as exc:
            logger.error(f"Error contacting payment service: {exc}")
            raise HTTPException(status_code=503, detail="Payment service unavailable")

    return {"status": "success", "order_id": 999, "message": "Order placed successfully"}
