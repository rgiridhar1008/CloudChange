import os
import tempfile
from pathlib import Path
from pydantic_settings import BaseSettings

_tmp_db = (Path(tempfile.gettempdir()) / "cloudchange.db").resolve().as_posix()
_default_db = f"sqlite:///{_tmp_db}" if os.getenv("VERCEL") else "sqlite:///./cloudchange.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "CloudChange"
    API_V1_STR: str = "/api/v1"
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:5173,*"
    DATABASE_URL: str = _default_db
    LLM_API_KEY: str | None = None
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_PORT: str = "5432"

    # External Notifications (SMTP - optional)
    SMTP_SERVER: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    NOTIFICATION_EMAIL_TO: str | None = None
    NOTIFICATION_EMAIL_FROM: str | None = None
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self.DATABASE_URL

    class Config:
        case_sensitive = True

settings = Settings()
