import os
import sys
import json
import argparse
from pathlib import Path

# Thêm thư mục gốc vào PYTHONPATH
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ROOT_DIR))

from backend.db.session import SessionLocal
from backend.services.retrieval.chatbot import DAUChatbot
from backend.services.retrieval.rag_chain import query_with_citation
from backend.services.nli.nli_checker import NLIChecker

import numpy as np
from rouge_score import rouge_scorer
import bert_score

def load_testset(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_evaluation(testset_path: str):
    print(f"Loading testset from {testset_path}...")
    testset = load_testset(testset_path)
    
    db = SessionLocal()
    nli_checker = NLIChecker()
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=False)
    
    results = []
    
    print(f"\nEvaluating {len(testset)} queries...\n")
    
    for i, item in enumerate(testset):
        query = item['query']
        reference = item['reference']
        
        print(f"[{i+1}/{len(testset)}] Query: {query}")
        
        # 1. Generate answer via RAG
        rag_response = query_with_citation(query, run_nli_check=False)
        generated_answer = rag_response.get('answer') or rag_response.get('message', '')
        citations = rag_response.get('citations', [])
        
        # Build context from citations' content if available, else use a placeholder
        context = " ".join([c.get('noi_dung', '') for c in citations])
        
        # 2. Compute ROUGE
        rouge_scores = scorer.score(reference, generated_answer)
        r1 = rouge_scores['rouge1'].fmeasure
        r2 = rouge_scores['rouge2'].fmeasure
        rl = rouge_scores['rougeL'].fmeasure
        
        # 3. Compute BERTScore
        # We use mBERT for Vietnamese support
        P, R, F1 = bert_score.score([generated_answer], [reference], lang="vi", verbose=False)
        bert_f1 = F1.item()
        
        # 4. Compute Faithfulness (NLI)
        if context.strip():
            nli_result = nli_checker.check(premise=context, hypothesis=generated_answer)
            faithfulness = nli_result.get('diem_faithfulness', 0.0)
        else:
            # If no context, check against reference or assign 0
            nli_result = nli_checker.check(premise=reference, hypothesis=generated_answer)
            faithfulness = nli_result.get('diem_faithfulness', 0.0)
            
        results.append({
            "query": query,
            "rouge1": r1,
            "rouge2": r2,
            "rougeL": rl,
            "bertscore_f1": bert_f1,
            "faithfulness": faithfulness
        })
        
        print(f"   -> ROUGE-1: {r1:.4f} | ROUGE-L: {rl:.4f}")
        print(f"   -> BERTScore F1: {bert_f1:.4f}")
        print(f"   -> Faithfulness: {faithfulness:.4f}\n")
        
    db.close()
    
    # Calculate averages
    avg_r1 = np.mean([r['rouge1'] for r in results])
    avg_r2 = np.mean([r['rouge2'] for r in results])
    avg_rl = np.mean([r['rougeL'] for r in results])
    avg_bert = np.mean([r['bertscore_f1'] for r in results])
    avg_faith = np.mean([r['faithfulness'] for r in results])
    
    print("="*50)
    print(" 📊 THỐNG KÊ ĐÁNH GIÁ (AVERAGE SCORES)")
    print("="*50)
    print(f"  ROUGE-1      : {avg_r1:.4f}")
    print(f"  ROUGE-2      : {avg_r2:.4f}")
    print(f"  ROUGE-L      : {avg_rl:.4f}")
    print(f"  BERTScore F1 : {avg_bert:.4f}")
    print(f"  Faithfulness : {avg_faith:.4f}")
    print("="*50)
    
    # Save results
    out_file = Path(testset_path).parent / "evaluation_results.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({
            "averages": {
                "rouge1": avg_r1,
                "rouge2": avg_r2,
                "rougeL": avg_rl,
                "bertscore_f1": avg_bert,
                "faithfulness": avg_faith
            },
            "details": results
        }, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu kết quả chi tiết tại {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Đánh giá ROUGE, BERTScore và Faithfulness cho RAG")
    parser.add_argument("--testset", type=str, default="../data/testset/rag_testset.json", help="Đường dẫn đến file testset JSON")
    args = parser.parse_args()
    
    testset_path = (BACKEND_DIR / args.testset).resolve()
    if not testset_path.exists():
        print(f"❌ Lỗi: Không tìm thấy testset tại {testset_path}")
        sys.exit(1)
        
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
        
    run_evaluation(str(testset_path))
