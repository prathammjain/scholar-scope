import pypdf
import io
from typing import List, Dict
import numpy as np
from ingestion.embeddings import get_embedding_generator


class PDFProcessor:
    def __init__(self):
        self.embedding_gen = get_embedding_generator()
    
    def extract_text_from_pdf(self, pdf_file) -> List[Dict]:
        """Extract text from PDF, split into chunks."""
        pdf_reader = pypdf.PdfReader(pdf_file)
        
        chunks = []
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            
            # Split into paragraphs (simple chunking)
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
            
            for para_idx, para in enumerate(paragraphs):
                chunks.append({
                    "text": para,
                    "page": page_num + 1,
                    "chunk_id": f"p{page_num + 1}_c{para_idx}"
                })
        
        return chunks
    
    def create_embeddings(self, chunks: List[Dict]) -> tuple:
        """Create embeddings for all chunks."""
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_gen.generate(texts)
        return embeddings, chunks
    
    def search_chunks(self, query: str, embeddings: np.ndarray, chunks: List[Dict], top_k: int = 3):
        """Search for relevant chunks using cosine similarity."""
        query_embedding = self.embedding_gen.generate_query_embedding(query)
        
        # Normalize embeddings
        import faiss
        embeddings_norm = embeddings.astype('float32')
        query_norm = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(embeddings_norm)
        faiss.normalize_L2(query_norm)
        
        # Compute similarities
        similarities = np.dot(embeddings_norm, query_norm.T).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                **chunks[idx],
                "score": float(similarities[idx])
            })
        
        return results


def get_pdf_processor():
    return PDFProcessor()
