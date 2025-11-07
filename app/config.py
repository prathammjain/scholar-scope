import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "scholarscope")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "scholar")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "scholar123")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIM: int = 384
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
    API_TITLE: str = "ScholarScope API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Retrieval-Augmented Research Copilot"
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 50
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
