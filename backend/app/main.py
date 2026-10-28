from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1 import analyze, deployment, monitoring
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.schemas.health import HealthResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
def on_startup():
    from app.core.database import engine, Base, SessionLocal
    from app.models.risk_rule import RiskRule
    from app.models.deployment_history import DeploymentHistory
    from app.models.notification import Notification
    
    Base.metadata.create_all(bind=engine)
    
    # Seed default risk rules
    db = SessionLocal()
    if db.query(RiskRule).count() == 0:
        default_rules = [
            RiskRule(rule_name="Replica Reduction", change_type="REPLICA_REDUCTION", score=20, reason_template="Replicas reduced from {old} to {new}"),
            RiskRule(rule_name="Memory Reduction", change_type="MEMORY_REDUCTION", score=20, reason_template="Memory limits/requests reduced from {old} to {new}"),
            RiskRule(rule_name="Missing Probe", change_type="REMOVED", path_keyword="probe", score=15, reason_template="Health probe removed at path: {path}"),
            RiskRule(rule_name="Missing Liveness", change_type="REMOVED", path_keyword="liveness", score=15, reason_template="Health probe removed at path: {path}"),
            RiskRule(rule_name="Missing Readiness", change_type="REMOVED", path_keyword="readiness", score=15, reason_template="Health probe removed at path: {path}"),
            RiskRule(rule_name="Security Context Modified", change_type="MODIFIED", path_keyword="securitycontext", score=10, reason_template="Modified security context at path: {path}"),
            RiskRule(rule_name="Privileged Escapation", change_type="MODIFIED", path_keyword="privileged", score=10, reason_template="Modified security context at path: {path}")
        ]
        db.add_all(default_rules)
        db.commit()
    db.close()


# Set CORS enabled origins
origins = [origin.strip() for origin in settings.FRONTEND_ORIGINS.split(",")] if hasattr(settings, "FRONTEND_ORIGINS") and settings.FRONTEND_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1", tags=["analyze"])
app.include_router(deployment.router, prefix="/api/v1/deployment", tags=["deployment"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])

from app.api.v1 import overview, history, cluster, notifications
app.include_router(overview.router, prefix="/api/v1/overview", tags=["overview"])
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])
app.include_router(cluster.router, prefix="/api/v1/cluster", tags=["cluster"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])

from fastapi.responses import JSONResponse, RedirectResponse

from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation Error", "message": str(exc.errors())},
    )

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Backend Service Error", "message": str(exc)},
    )

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint that also verifies database connection.
    """
    db_status = "offline"
    try:
        # Simple query to check db connection
        db.execute(text("SELECT 1"))
        db_status = "online"
        logger.info("Health check successful. Database is online.")
    except Exception as e:
        db_status = f"offline - {str(e)}"
        logger.warning(f"Health check failed to connect to database: {str(e)}")

    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        database=db_status
    )
