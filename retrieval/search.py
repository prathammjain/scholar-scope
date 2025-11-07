from typing import List, Dict, Any
import time
from sqlalchemy.orm import Session
from app.models import Document, SearchLog
from retrieval.faiss_index import get_faiss_index
from ingestion.embeddings import get_embedding_generator


class SemanticSearchEngine:
    def __init__(self):
        self.faiss_index = get_faiss_index()
        self.embedding_generator = get_embedding_generator()
    
    def search(self, query: str, top_k: int = 5, db: Session = None, log_search: bool = True):
        start_time = time.time()
        
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        doc_ids, scores = self.faiss_index.search(query_embedding, top_k)
        
        results = []
        
        if db:
            documents = db.query(Document).filter(Document.embedding_id.in_(doc_ids)).all()
            doc_map = {doc.embedding_id: doc for doc in documents}
            
            for doc_id, score in zip(doc_ids, scores):
                if doc_id in doc_map:
                    doc = doc_map[doc_id]
                    results.append({
                        **doc.to_dict(),
                        "score": float(score),
                        "rank": len(results) + 1
                    })
        
        latency_ms = (time.time() - start_time) * 1000
        
        if log_search and db:
            search_log = SearchLog(
                query=query,
                top_k=top_k,
                latency_ms=latency_ms,
                num_results=len(results)
            )
            db.add(search_log)
            db.commit()
        
        return results, latency_ms
    
    def get_index_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": self.faiss_index.size,
            "embedding_dimension": self.faiss_index.dimension,
            "model_name": self.embedding_generator.model_name
        }


_search_engine = None


def get_search_engine() -> SemanticSearchEngine:
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearchEngine()
    return _search_engine
