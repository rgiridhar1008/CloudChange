import pytest
from app.core.database import Base, engine, SessionLocal
from app.models.risk_rule import RiskRule
from app.modules.risk_analysis.engine import DEFAULT_RULES_DATA

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(RiskRule).count() == 0:
            for r_data in DEFAULT_RULES_DATA:
                db.add(RiskRule(**r_data))
            db.commit()
    finally:
        db.close()

