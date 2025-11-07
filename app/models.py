from sqlalchemy import Column, Integer, String, Text, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import get_settings

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(Text)
    abstract = Column(Text, nullable=False)
    categories = Column(String(200))
    published_date = Column(DateTime)
    pdf_url = Column(String(500))
    embedding_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "categories": self.categories,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "pdf_url": self.pdf_url,
            "embedding_id": self.embedding_id,
        }


class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    top_k = Column(Integer)
    latency_ms = Column(Float)
    num_results = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
