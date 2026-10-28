import logging
import os
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("payment-service")

app = FastAPI(title="Payment Service")

class PaymentRequest(BaseModel):
    order_id: int
    amount: float

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    # Mock database check
    db_host = os.getenv("DB_HOST", "postgres")
    logger.info(f"Checking connection to DB at {db_host}...")
    return {"status": "ok", "service": "payment-service", "db_connected": True}

@app.post("/pay")
def process_payment(request: PaymentRequest):
    logger.info(f"Processing payment for order {request.order_id}, amount: {request.amount}")
    return {"status": "success", "transaction_id": f"txn_{request.order_id}"}
