from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import get_db, Document
from retrieval.search import get_search_engine

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=settings.MAX_TOP_K)


class SearchResult(BaseModel):
    id: int
    arxiv_id: str
    title: str
    authors: Optional[str]
    abstract: str
    categories: Optional[str]
    published_date: Optional[str]
    pdf_url: Optional[str]
    score: float
    rank: int


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    latency_ms: float


@app.get("/")
async def root():
    return {"status": "healthy", "version": settings.API_VERSION}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, db: Session = Depends(get_db)):
    try:
        search_engine = get_search_engine()
        results, latency_ms = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            db=db,
            log_search=True
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            latency_ms=latency_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/documents/{arxiv_id}")
async def get_document(arxiv_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.arxiv_id == arxiv_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.to_dict()


@app.get("/stats")
async def get_stats():
    search_engine = get_search_engine()
    return search_engine.get_index_stats()


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    search_engine = get_search_engine()
    index_size = search_engine.faiss_index.size
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": settings.API_VERSION,
        "database": db_status,
        "index_size": index_size
    }
