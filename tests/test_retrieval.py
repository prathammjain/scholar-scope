import pytest
import numpy as np
from retrieval.faiss_index import FAISSIndex
from ingestion.embeddings import EmbeddingGenerator


class TestFAISSIndex:
    def test_create_index(self):
        index = FAISSIndex(dimension=384)
        index.create_index()
        assert index.index is not None
        assert index.size == 0
    
    def test_add_embeddings(self):
        index = FAISSIndex(dimension=384)
        index.create_index()
        
        embeddings = np.random.rand(10, 384).astype('float32')
        doc_ids = list(range(10))
        
        index.add_embeddings(embeddings, doc_ids)
        assert index.size == 10
        assert len(index.id_map) == 10
    
    def test_search(self):
        index = FAISSIndex(dimension=384)
        index.create_index()
        
        embeddings = np.random.rand(100, 384).astype('float32')
        doc_ids = list(range(100))
        index.add_embeddings(embeddings, doc_ids)
        
        query = np.random.rand(384).astype('float32')
        results, scores = index.search(query, top_k=5)
        
        assert len(results) == 5
        assert len(scores) == 5


class TestEmbeddingGenerator:
    def test_generate_single_text(self):
        gen = EmbeddingGenerator()
        embedding = gen.generate("test text")
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[1] == 384
    
    def test_generate_batch(self):
        gen = EmbeddingGenerator()
        texts = ["text one", "text two", "text three"]
        embeddings = gen.generate(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (3, 384)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
