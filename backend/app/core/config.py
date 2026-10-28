from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CloudChange"
    API_V1_STR: str = "/api/v1"
    FRONTEND_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    DATABASE_URL: str = "sqlite:///./cloudchange.db"
    LLM_API_KEY: str | None = None
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self.DATABASE_URL

    class Config:
        case_sensitive = True

settings = Settings()
