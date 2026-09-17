"""Test script to empirically verify UC-08: Topic Dashboard (Dashboard Duyệt & Quản lý Văn bản theo Chủ đề)."""

import json
import urllib.request
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_URL = "http://localhost:8000"

def test_topics_summary_api():
    print("=== 1. Testing Topic Summary API (/api/topics/summary) ===", flush=True)
    url = f"{BASE_URL}/api/topics/summary"
    req = urllib.request.Request(url)
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        topics = data.get("topics", [])
        
        print(f"Status: {resp.status}", flush=True)
        print(f"Total topics returned: {len(topics)}", flush=True)
        assert len(topics) == 6, f"Expected 6 topic categories, got {len(topics)}"
        
        total_docs_all = 0
        total_pub_all = 0
        total_pending_all = 0
        
        for t in topics:
            code = t.get("code")
            name = t.get("name")
            icon = t.get("icon")
            total = t.get("total_documents", 0)
            pub = t.get("published_documents", 0)
            pending = t.get("pending_documents", 0)
            rate = t.get("completion_rate", 0.0)
            
            print(f"  [{icon}] {code}: {name} | Total={total} (Pub={pub}, Pend={pending}) | Rate={rate}%", flush=True)
            assert code in ["DAO_TAO", "TUYEN_SINH", "TAI_CHINH", "NHAN_SU", "CO_SO_VAT_CHAT", "KHAC"]
            assert total == pub + pending
            total_docs_all += total
            total_pub_all += pub
            total_pending_all += pending
            
        print(f"Overall System Metrics: Total Docs={total_docs_all}, Published={total_pub_all}, Pending={total_pending_all}", flush=True)
        assert total_docs_all > 0, "Database should contain documents"
        
    print("✅ Topic Summary API verified successfully!\n", flush=True)

def test_topic_filtering_documents():
    print("=== 2. Testing Topic Filtering in Documents API (/api/documents?chu_de=...) ===", flush=True)
    test_topics = ["DAO_TAO", "TUYEN_SINH", "KHAC"]
    
    for t_code in test_topics:
        url = f"{BASE_URL}/api/documents?chu_de={t_code}&limit=10"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            total = data.get("total", len(items))
            print(f"  - Topic [{t_code}]: {total} documents found", flush=True)
            for item in items[:2]:
                print(f"    * {item.get('so_hieu')} - {item.get('ten_van_ban')[:60]}... [Topic: {item.get('chu_de')}]", flush=True)
                assert item.get("chu_de") == t_code or (t_code == "KHAC" and item.get("chu_de") not in ["DAO_TAO", "TUYEN_SINH"])
                
    print("✅ Topic filtering verified successfully!\n", flush=True)

if __name__ == "__main__":
    try:
        test_topics_summary_api()
        test_topic_filtering_documents()
        print("ALL UC-08 VERIFICATION TESTS PASSED SUCCESSFULLY! 🎉", flush=True)
    except Exception as e:
        print(f"❌ Verification failed: {e}", flush=True)
        sys.exit(1)
