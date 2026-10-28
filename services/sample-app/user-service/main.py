import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("user-service")

app = FastAPI(title="User Service")

class User(BaseModel):
    id: int
    name: str
    status: str

# Mock database
USERS = {
    1: User(id=1, name="Alice", status="active"),
    2: User(id=2, name="Bob", status="inactive")
}

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "service": "user-service"}

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    logger.info(f"Fetching user {user_id}")
    if user_id not in USERS:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    return USERS[user_id]
