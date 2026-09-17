"""Quick test script — không cần LangChain/torch."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ── Test 1: Summarization (extractive) ───────────────────────────────────────
print("\n" + "="*60)
print("  TEST 1: Summarization (Extractive)")
print("="*60)

from services.summarization.summarizer import DocumentSummarizer

chunks = []
with open("data/processed/chunks.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 5:
            break
        c = json.loads(line.strip())
        if c:
            chunks.append(c)

print(f"Loaded {len(chunks)} test chunks")
summarizer = DocumentSummarizer(strategy="extractive", run_nli_check=False)

for chunk in chunks[:3]:
    r = summarizer.summarize_chunk(chunk)
    chunk_id = r["chunk_id"]
    status = r["trang_thai_xuat_ban"]
    n_sent = len(r["sentences"])
    print(f"\n[{chunk_id}] {status} | {n_sent} sentences")
    for s in r["sentences"][:1]:
        print(f"  -> {s['sentence'][:120]}...")

print("\n✅ Summarization OK!")

# ── Test 2: Report Suggestion ─────────────────────────────────────────────────
print("\n" + "="*60)
print("  TEST 2: Report Suggestion")
print("="*60)

from services.report_suggestion.report_chain import suggest_report

# Load first doc
with open("data/processed/documents.jsonl", "r", encoding="utf-8") as f:
    first_doc = json.loads(f.readline().strip())

doc_id = first_doc["doc_id"]
doc_chunks = []
with open("data/processed/chunks.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line.strip())
        if c.get("doc_id") == doc_id:
            doc_chunks.append(c)
            if len(doc_chunks) >= 5:
                break

print(f"Van ban: {first_doc.get('ten_van_ban', doc_id)}")
result = suggest_report(doc_metadata=first_doc, chunks=doc_chunks)

print(f"Loai bao cao: {result['loai_bao_cao']}")
print(f"Template: {result.get('template_id', 'Tu dung tu van ban')}")
print(f"Source: {result['source']}")
print("De muc:")
for dm in result["de_muc"][:6]:
    print(f"  {dm}")
print(f"Can cu: {result['can_cu_phap_ly'][0][:80]}")
print("\n✅ Report Suggestion OK!")

# ── Test 3: Document Tree (rule-based only) ───────────────────────────────────
print("\n" + "="*60)
print("  TEST 3: Document Tree (rule-based relations)")
print("="*60)

from services.document_tree.related_docs import DocumentTree

tree = DocumentTree(
    index_path="data/vector_db/faiss_index",
    relations_path="data/processed/document_relations.jsonl",
)

result = tree.find_related(
    doc_id=doc_id,
    doc_content=doc_chunks[0]["content"][:300] if doc_chunks else "",
    include_semantic=False,  # Khong can FAISS index
)

print(f"Van ban: {doc_id}")
print(f"Quan he tuong minh: {len(result['explicit_relations'])} ket qua")
for rel in result["explicit_relations"][:5]:
    print(f"  [{rel['loai_quan_he']}] -> {rel['doc_id_related']}: {rel['mo_ta'][:60]}")

if not result["explicit_relations"]:
    print("  (Khong co quan he tuong minh cho van ban nay)")

print("\n✅ Document Tree (rule-based) OK!")
print("\n" + "="*60)
print("  TAT CA TESTS PASSED! (Khong can LangChain/torch)")
print("="*60)
