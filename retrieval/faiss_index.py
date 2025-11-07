import faiss
import numpy as np
import pickle
import os
from pathlib import Path
from typing import List, Tuple
from app.config import get_settings

settings = get_settings()


class FAISSIndex:
    def __init__(self, dimension: int = settings.EMBEDDING_DIM):
        self.dimension = dimension
        self.index = None
        self.id_map = []
        
    def create_index(self):
        self.index = faiss.IndexFlatIP(self.dimension)
        
    def add_embeddings(self, embeddings: np.ndarray, doc_ids: List[int]):
        if self.index is None:
            self.create_index()
        
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        self.id_map.extend(doc_ids)
        
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> Tuple[List[int], List[float]]:
        if self.index is None or self.index.ntotal == 0:
            return [], []
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        doc_ids = [self.id_map[idx] for idx in indices[0] if idx < len(self.id_map)]
        scores = distances[0].tolist()
        
        return doc_ids, scores
    
    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, f"{path}.index")
        
        with open(f"{path}.map", "wb") as f:
            pickle.dump(self.id_map, f)
    
    def load(self, path: str):
        if not os.path.exists(f"{path}.index"):
            raise FileNotFoundError(f"Index file not found: {path}.index")
        
        self.index = faiss.read_index(f"{path}.index")
        
        with open(f"{path}.map", "rb") as f:
            self.id_map = pickle.load(f)
    
    @property
    def size(self) -> int:
        return self.index.ntotal if self.index else 0


_faiss_index = None


def get_faiss_index() -> FAISSIndex:
    global _faiss_index
    if _faiss_index is None:
        _faiss_index = FAISSIndex()
        try:
            _faiss_index.load(settings.FAISS_INDEX_PATH)
        except FileNotFoundError:
            _faiss_index.create_index()
    return _faiss_index
