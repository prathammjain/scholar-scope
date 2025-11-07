from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from app.config import get_settings

settings = get_settings()


class EmbeddingGenerator:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        
    def load_model(self):
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
    
    def generate(self, texts: Union[str, List[str]]) -> np.ndarray:
        self.load_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            show_progress_bar=len(texts) > 100,
            batch_size=32,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        return self.generate(query)[0]


_embedding_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
