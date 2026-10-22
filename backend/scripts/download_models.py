"""Tải trước các mô hình cục bộ vào HF cache.

Chạy trong backend/ với venv đã kích hoạt:
    export HF_HOME="$PWD/data/models"
    python scripts/download_models.py

Tùy chọn --verify để load thử từng mô hình (tuần tự, giải phóng RAM sau mỗi mô hình).
"""

from __future__ import annotations

import argparse
import gc
import os
import sys

# Đọc .env để dùng đúng HF_HOME như ứng dụng (import này cũng set os.environ).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings  # noqa: E402

MODELS = [
    ("summarization", "VietAI/vit5-base-vietnews-summarization"),
    ("qa", "timpal0l/mdeberta-v3-base-squad2"),
    ("nli", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"),
    ("embedding", "sentence-transformers/paraphrase-MiniLM-L3-v2"),
]


def download_all() -> None:
    from huggingface_hub import snapshot_download

    for label, repo_id in MODELS:
        print(f"[{label}] Đang tải {repo_id}...", flush=True)
        path = snapshot_download(repo_id=repo_id)
        print(f"[{label}] Xong: {path}", flush=True)


def verify_all() -> None:
    """Load từng mô hình một, sau đó giải phóng để tránh OOM trên máy ít RAM."""
    from transformers import (
        AutoModelForQuestionAnswering,
        AutoModelForSeq2SeqLM,
        AutoModelForSequenceClassification,
        AutoTokenizer,
    )

    checks = [
        ("summarization", AutoTokenizer, AutoModelForSeq2SeqLM),
        ("qa", AutoTokenizer, AutoModelForQuestionAnswering),
        ("nli", AutoTokenizer, AutoModelForSequenceClassification),
    ]
    for label, tokenizer_cls, model_cls in checks:
        repo_id = dict(MODELS)[label]
        print(f"[{label}] Load thử {repo_id}...", flush=True)
        tokenizer_cls.from_pretrained(repo_id)
        model_cls.from_pretrained(repo_id)
        gc.collect()
        print(f"[{label}] OK", flush=True)

    from sentence_transformers import SentenceTransformer

    repo_id = dict(MODELS)["embedding"]
    print(f"[embedding] Load thử {repo_id}...", flush=True)
    SentenceTransformer(repo_id)
    gc.collect()
    print("[embedding] OK", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Tải trước mô hình cục bộ")
    parser.add_argument("--verify", action="store_true", help="Load thử từng mô hình sau khi tải")
    args = parser.parse_args()

    print(f"HF cache: {os.environ.get('HF_HOME', '(mặc định ~/.cache/huggingface)')}")
    try:
        download_all()
        if args.verify:
            verify_all()
    except Exception as exc:  # noqa: BLE001 - CLI cần thông báo ngắn gọn
        print(f"Lỗi tải/kiểm tra mô hình: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
