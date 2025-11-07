import arxiv
import argparse
from typing import List
from sqlalchemy.orm import Session
from tqdm import tqdm
import numpy as np

from app.models import Document, SessionLocal, create_tables
from retrieval.faiss_index import get_faiss_index
from ingestion.embeddings import get_embedding_generator
from app.config import get_settings

settings = get_settings()


def fetch_arxiv_papers(category: str = "cs.AI", max_results: int = 100):
    print(f"Fetching papers from arXiv (category: {category}, max: {max_results})...")
    
    query = f"cat:{category}"
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    for result in tqdm(client.results(search), total=max_results, desc="Fetching"):
        paper = {
            "arxiv_id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": ", ".join([author.name for author in result.authors]),
            "abstract": result.summary,
            "categories": ", ".join(result.categories),
            "published_date": result.published,
            "pdf_url": result.pdf_url
        }
        papers.append(paper)
    
    print(f"✓ Fetched {len(papers)} papers")
    return papers


def ingest_papers(papers: List[dict], db: Session):
    print(f"\nIngesting {len(papers)} papers...")
    
    faiss_index = get_faiss_index()
    embedding_gen = get_embedding_generator()
    
    texts = [f"{paper['title']}. {paper['abstract']}" for paper in papers]
    
    print("Generating embeddings...")
    all_embeddings = embedding_gen.generate(texts)
    
    print("Storing in database and FAISS index...")
    new_docs = []
    
    for i, (paper, embedding) in enumerate(tqdm(zip(papers, all_embeddings), total=len(papers))):
        existing = db.query(Document).filter(Document.arxiv_id == paper["arxiv_id"]).first()
        if existing:
            continue
        
        doc = Document(
            arxiv_id=paper["arxiv_id"],
            title=paper["title"],
            authors=paper["authors"],
            abstract=paper["abstract"],
            categories=paper["categories"],
            published_date=paper["published_date"],
            pdf_url=paper["pdf_url"],
            embedding_id=faiss_index.size + len(new_docs)
        )
        db.add(doc)
        new_docs.append((doc, embedding))
    
    db.commit()
    
    if new_docs:
        embeddings_array = np.array([emb for _, emb in new_docs])
        doc_ids = [doc.embedding_id for doc, _ in new_docs]
        faiss_index.add_embeddings(embeddings_array, doc_ids)
        
        print("Saving FAISS index...")
        faiss_index.save(settings.FAISS_INDEX_PATH)
    
    print(f"✓ Successfully ingested {len(new_docs)} new papers")
    print(f"✓ Total documents in index: {faiss_index.size}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, default="cs.AI")
    parser.add_argument("--max-papers", type=int, default=100)
    
    args = parser.parse_args()
    
    print("Initializing database...")
    create_tables()
    
    papers = fetch_arxiv_papers(category=args.category, max_results=args.max_papers)
    
    if not papers:
        print("No papers fetched. Exiting.")
        return
    
    db = SessionLocal()
    try:
        ingest_papers(papers, db)
    finally:
        db.close()
    
    print("\n✅ Ingestion complete!")


if __name__ == "__main__":
    main()
