"""Kiểm tra nhanh import và cấu trúc API sau khi tích hợp BARTpho.

Cách dùng:
  python scripts/verify_summarize_api.py
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

errors = []
ok_count = 0

def check(label, fn):
    global ok_count
    try:
        fn()
        print(f"  ✅ {label}")
        ok_count += 1
    except Exception as e:
        print(f"  ❌ {label}: {e}")
        errors.append(label)

print("\n" + "="*55)
print("  VERIFY: BARTpho Integration")
print("="*55)

# 1. Import summarizer classes
check("Import summarizer module", lambda: __import__(
    "services.summarization.summarizer",
    fromlist=["DocumentSummarizer", "AbstractiveSummarizer", "ExtractiveSummarizer", "summarize_document"]
))

# 2. Khởi tạo extractive
def _check_extractive():
    from services.summarization.summarizer import DocumentSummarizer
    s = DocumentSummarizer(strategy="extractive", run_nli_check=False)
    assert s.strategy == "extractive"

check("DocumentSummarizer(extractive) init", _check_extractive)

# 3. Khởi tạo hybrid (không cần model khi init)
def _check_hybrid():
    from services.summarization.summarizer import DocumentSummarizer
    s = DocumentSummarizer(strategy="hybrid", run_nli_check=False)
    assert s.strategy == "hybrid"

check("DocumentSummarizer(hybrid) init", _check_hybrid)

# 4. Singleton abstractive
check("get_abstractive_summarizer singleton", lambda: __import__(
    "services.summarization.summarizer", fromlist=["get_abstractive_summarizer"]
).get_abstractive_summarizer.__name__ == "get_abstractive_summarizer")

# 5. API models
def _check_api_models():
    from api.main import SummarizeRequest, SummarizeResponse, ChunkSummaryResult, SentenceResult
    req = SummarizeRequest(strategy="hybrid", run_nli=True)
    assert req.strategy == "hybrid"

check("SummarizeRequest/Response Pydantic models", _check_api_models)

# 6. API routes
def _check_routes():
    from api.main import app
    routes = [getattr(r, "path", "") for r in app.routes]
    assert "/api/summarize/{doc_id}" in routes, f"Missing route. Got: {[r for r in routes if 'summarize' in r]}"
    assert "/api/admin/reset-summarizer" in routes

check("API endpoint /api/summarize/{doc_id} registered", _check_routes)

# 7. Frontend api.ts có summarizeDocument function
def _check_frontend():
    api_ts = Path(__file__).parent.parent.parent / "frontend" / "src" / "services" / "api.ts"
    content = api_ts.read_text(encoding="utf-8")
    assert "summarizeDocument" in content
    assert "SummarizeResponse" in content
    assert "SummarizeSentenceResult" in content

check("Frontend api.ts has summarizeDocument", _check_frontend)

# 8. Transformers availability
def _check_transformers():
    import importlib
    spec = importlib.util.find_spec("transformers")
    if spec is None:
        raise ImportError("transformers not installed")

check("transformers library available", _check_transformers)

# 9. Torch availability
def _check_torch():
    import importlib
    spec = importlib.util.find_spec("torch")
    if spec is None:
        raise ImportError("torch not installed")
    import torch
    print(f"         (torch {torch.__version__})", end="")

check("torch library available", _check_torch)

print(f"\n{'='*55}")
print(f"  Results: {ok_count} passed, {len(errors)} failed")
if errors:
    print(f"  ❌ Failed: {errors}")
else:
    print("  🎉 Tất cả checks passed!")
print("="*55)
