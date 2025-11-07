#!/usr/bin/env python3
import json
import time
import argparse
from typing import List, Dict
import numpy as np
from app.models import SessionLocal
from retrieval.search import get_search_engine


def calculate_recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    if not relevant:
        return 0.0
    retrieved_k = set(retrieved[:k])
    relevant_set = set(relevant)
    return len(retrieved_k & relevant_set) / len(relevant_set)


def evaluate_retrieval(eval_data: List[Dict], k_values: List[int] = [1, 5, 10]):
    search_engine = get_search_engine()
    db = SessionLocal()
    
    results = {
        "queries_evaluated": len(eval_data),
        "recall": {k: [] for k in k_values},
        "latencies": []
    }
    
    print(f"Evaluating on {len(eval_data)} queries...")
    
    for item in eval_data:
        query = item["query"]
        relevant_docs = item["relevant_docs"]
        
        start_time = time.time()
        search_results, latency = search_engine.search(
            query=query,
            top_k=max(k_values),
            db=db,
            log_search=False
        )
        latency_ms = (time.time() - start_time) * 1000
        results["latencies"].append(latency_ms)
        
        retrieved_ids = [r["arxiv_id"] for r in search_results]
        
        for k in k_values:
            recall = calculate_recall_at_k(retrieved_ids, relevant_docs, k)
            results["recall"][k].append(recall)
    
    db.close()
    
    aggregated = {
        "total_queries": results["queries_evaluated"],
        "avg_latency_ms": np.mean(results["latencies"]),
        "recall": {k: np.mean(results["recall"][k]) for k in k_values}
    }
    
    return aggregated


def print_results(results: Dict):
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(f"Total Queries: {results['total_queries']}")
    print(f"Avg Latency: {results['avg_latency_ms']:.2f}ms")
    print("\nRecall@K:")
    for k, value in results['recall'].items():
        print(f"  R@{k}: {value:.4f}")
    print("="*50)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="data/eval_queries.json")
    args = parser.parse_args()
    
    with open(args.dataset, 'r') as f:
        eval_data = json.load(f)
    
    results = evaluate_retrieval(eval_data)
    print_results(results)


if __name__ == "__main__":
    main()
