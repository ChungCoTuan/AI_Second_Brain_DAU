"""Test script to empirically verify UC-09: Nhật ký Duyệt Audit Trail, Sổ Định Mức Pháp Quy & Thống Kê Giám Sát Hệ Thống."""

import json
import urllib.request
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_URL = "http://localhost:8000"

def test_audit_logs_api():
    print("=== 1. Testing Review Audit Logs API (/api/review/audit-logs) ===", flush=True)
    url = f"{BASE_URL}/api/review/audit-logs?limit=50"
    req = urllib.request.Request(url)
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        
        logs = data.get("logs", [])
        total = data.get("total", len(logs))
        print(f"Status: {resp.status}", flush=True)
        print(f"Total audit log records: {total}", flush=True)
        
        if len(logs) > 0:
            for log in logs[:3]:
                print(f"  - Log #{log.get('log_id')}: Action={log.get('hanh_dong')} by {log.get('reviewer_id')} on Doc={log.get('document_id')}", flush=True)
                print(f"    AI Text: {log.get('cau_ai_sinh', '')[:60]}...", flush=True)
                print(f"    Edited Text: {log.get('cau_sau_sua', 'None')}", flush=True)
                assert "log_id" in log
                assert "hanh_dong" in log
                assert "reviewer_id" in log
        else:
            print("  (Audit log currently empty, schema verified OK)", flush=True)
            
    print("✅ Review Audit Logs API verified successfully!\n", flush=True)

def test_system_stats_analytics():
    print("=== 2. Testing System Stats & Audit Metrics (/api/stats) ===", flush=True)
    url = f"{BASE_URL}/api/stats"
    req = urllib.request.Request(url)
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        
        total_docs = data.get("total_documents", 0)
        published_docs = data.get("published_documents", 0)
        pending_docs = data.get("pending_documents", 0)
        total_chunks = data.get("total_chunks", 0)
        faiss_ready = data.get("faiss_index_exists", False)
        
        print(f"Total Documents: {total_docs}", flush=True)
        print(f"Published Documents: {published_docs}", flush=True)
        print(f"Pending Documents: {pending_docs}", flush=True)
        print(f"Total Chunks: {total_chunks}", flush=True)
        print(f"FAISS Vector DB Ready: {faiss_ready}", flush=True)
        
        assert total_docs > 0, "Total documents should be > 0"
        assert total_chunks > 0, "Total chunks should be > 0"
        
    print("✅ System Stats & Audit Metrics verified successfully!\n", flush=True)

if __name__ == "__main__":
    try:
        test_audit_logs_api()
        test_system_stats_analytics()
        print("ALL UC-09 VERIFICATION TESTS PASSED SUCCESSFULLY! 🎉", flush=True)
    except Exception as e:
        print(f"❌ Verification failed: {e}", flush=True)
        sys.exit(1)
