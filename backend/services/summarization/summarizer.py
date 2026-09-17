"""Summarization Service — DAU Second Brain (SVC-03, WF-03, EPIC-3).

Tóm tắt văn bản pháp quy có trích dẫn (Grounded Summarization).
Mỗi câu tóm tắt được gắn chunk_id nguồn để phục vụ citation.

Chiến lược (theo thứ tự ưu tiên):
  1. Hybrid (khuyến nghị, mặc định mới):
       - Bước 1: TextRank chọn câu/đoạn quan trọng nhất làm ngữ cảnh
       - Bước 2: BARTpho/ViT5 sinh bản tóm tắt abstractive từ ngữ cảnh đó
       - Bước 3: NLI check từng câu sinh ra → route theo WF-03
       - Fallback tự động: nếu model không load được → extractive
  2. Abstractive (BARTpho/ViT5): Sinh câu mới, bắt buộc NLI check
  3. Extractive (TextRank): Chọn câu gốc, không hallucinate

Luồng WF-03:
  chunk → [TextRank select] → [BARTpho/ViT5 summarize] → [NLI 3-label check]
  → route(entailment/contradiction/neutral) → publish hoặc pending_review

Cách dùng:
  from services.summarization.summarizer import summarize_document
  # Hybrid (BARTpho + NLI check):
  result = summarize_document(doc_id="08_2024_TT_BGDDT", chunks=[...], strategy="hybrid")
  # Extractive an toàn:
  result = summarize_document(doc_id="08_2024_TT_BGDDT", chunks=[...], strategy="extractive")
"""

from __future__ import annotations

import logging
import re
import sys
import threading
from collections import Counter
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

logger = logging.getLogger(__name__)

# ─── Hằng số cấu hình ────────────────────────────────────────────────────────

# BARTpho syllable-level — tốt nhất cho văn bản pháp quy tiếng Việt (vinai org, model công khai)
BARTPHO_SYLLABLE_MODEL = "vinai/bartpho-syllable-base"  # Nhẹ hơn, public
# BARTpho word-level — nhanh hơn
BARTPHO_WORD_MODEL = "vinai/bartpho-word-base"          # Nhẹ hơn, public
# ViT5 — alternative seq2seq tiếng Việt
VIT5_MODEL = "VietAI/vit5-base"
# Fallback đa ngôn ngữ nếu cả 3 model trận không tải được
MULTILINGUAL_FALLBACK_MODEL = "csebuetnlp/mT5_multilingual_XLSum"  # Public, hỗ trợ tiếng Việt

DEFAULT_ABSTRACTIVE_MODEL = BARTPHO_SYLLABLE_MODEL

# Ngưỡng TextRank: chọn tối đa N câu quan trọng nhất làm ngữ cảnh cho BARTpho
TEXTRANK_TOP_N_CONTEXT = 5
# Độ dài tối đa input cho BARTpho (tokens xấp xỉ bằng ký tự / 4)
MAX_INPUT_CHARS = 1024
# Độ dài tóm tắt sinh ra
MAX_SUMMARY_LENGTH = 256
MIN_SUMMARY_LENGTH = 40


# ─── Extractive Summarizer (TextRank-style, không cần LLM) ───────────────────

class ExtractiveSummarizer:
    """
    Trích xuất các câu quan trọng nhất từ chunk bằng phương pháp
    dựa trên tần suất từ khóa (TextRank simplified).

    An toàn hoàn toàn: không sinh câu mới → không thể hallucinate.
    Mỗi câu output chính là câu gốc trong văn bản.
    """

    def __init__(self, top_n_sentences: int = 3):
        self.top_n_sentences = top_n_sentences

        # Từ dừng tiếng Việt cơ bản
        self.stop_words = {
            "và", "của", "trong", "để", "với", "là", "có", "được",
            "các", "một", "này", "đó", "theo", "tại", "từ", "đến",
            "cho", "về", "khi", "hoặc", "nếu", "cũng", "đã", "sẽ",
            "không", "thì", "mà", "nhưng", "vì", "nên", "như", "do",
        }

    def _tokenize(self, text: str) -> list[str]:
        words = re.findall(r'\b[\wÀ-ỹ]+\b', text.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 1]

    def _score_sentences(self, sentences: list[str]) -> list[tuple[float, str]]:
        """Tính điểm cho mỗi câu dựa trên tần suất từ khóa."""
        all_words = []
        for s in sentences:
            all_words.extend(self._tokenize(s))

        word_freq = Counter(all_words)
        max_freq = max(word_freq.values()) if word_freq else 1

        # Normalize
        word_scores = {w: freq / max_freq for w, freq in word_freq.items()}

        scored = []
        for sent in sentences:
            words = self._tokenize(sent)
            if not words:
                continue
            score = sum(word_scores.get(w, 0) for w in words) / len(words)
            scored.append((score, sent))

        return sorted(scored, reverse=True)

    def get_top_context(self, content: str, top_n: int = TEXTRANK_TOP_N_CONTEXT) -> str:
        """
        Chọn top-N câu quan trọng nhất làm ngữ cảnh cho BARTpho.
        Giữ thứ tự xuất hiện gốc (không xáo trộn).
        """
        sentences = [
            s.strip()
            for s in re.split(r'[.!?;]\s+', content)
            if len(s.strip()) > 20
        ]
        if not sentences:
            return content[:MAX_INPUT_CHARS]

        scored = self._score_sentences(sentences)
        top_set = {sent for _, sent in scored[:top_n]}

        # Giữ thứ tự gốc
        ordered = [s for s in sentences if s in top_set]
        return ". ".join(ordered) if ordered else content[:MAX_INPUT_CHARS]

    def summarize(self, content: str, chunk_id: str) -> list[dict]:
        """
        Trả về danh sách dict câu tóm tắt, mỗi câu kèm chunk_id nguồn.

        Returns:
            list[dict]: mỗi dict có: sentence, chunk_id, method="extractive"
        """
        # Tách câu
        sentences = [
            s.strip()
            for s in re.split(r'[.!?;]\s+', content)
            if len(s.strip()) > 30
        ]

        if not sentences:
            return []

        scored = self._score_sentences(sentences)
        top_sentences = [sent for _, sent in scored[:self.top_n_sentences]]

        # Giữ thứ tự xuất hiện gốc
        ordered = [s for s in sentences if s in set(top_sentences)]

        return [
            {
                "sentence": s,
                "chunk_id": chunk_id,
                "method": "extractive",
                "nhan_nli": "entailment",  # Extractive luôn là entailment
                "diem_faithfulness": 1.0,
                "publish_action": "AUTO_PUBLISH",
            }
            for s in ordered
        ]


# ─── Abstractive Summarizer (BARTpho/ViT5) ───────────────────────────────────

class AbstractiveSummarizer:
    """
    Tóm tắt trừu tượng dùng BARTpho (syllable/word) hoặc ViT5.

    Pipeline theo WF-03:
      1. TextRank chọn câu quan trọng làm ngữ cảnh (giảm hallucination)
      2. BARTpho sinh bản tóm tắt mới
      3. Tách thành từng câu (để caller NLI-check từng câu)

    Lazy load model — chỉ tải khi lần đầu gọi summarize().
    Thread-safe với double-checked locking.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_ABSTRACTIVE_MODEL,
        device: int = -1,       # -1 = CPU, 0 = GPU đầu tiên
        max_length: int = MAX_SUMMARY_LENGTH,
        min_length: int = MIN_SUMMARY_LENGTH,
        use_textrank_context: bool = True,
        num_beams: int = 4,
    ):
        self.model_name = model_name
        self.device = device
        self.max_length = max_length
        self.min_length = min_length
        self.use_textrank_context = use_textrank_context
        self.num_beams = num_beams
        self._pipeline = None
        self._load_lock = threading.Lock()
        self._textrank = ExtractiveSummarizer()

    def _get_pipeline(self):
        """Lazy load BARTpho pipeline với double-checked locking."""
        if self._pipeline is not None:
            return self._pipeline

        with self._load_lock:
            if self._pipeline is not None:
                return self._pipeline

            model_candidates = [
                self.model_name,
                BARTPHO_WORD_MODEL,
                VIT5_MODEL,
                MULTILINGUAL_FALLBACK_MODEL,
            ]
            # Loại bỏ trùng lặp nhưng giữ thứ tự
            seen = set()
            model_candidates = [m for m in model_candidates if not (m in seen or seen.add(m))]
            last_error = None

            for model in model_candidates:
                try:
                    from transformers import (
                        AutoTokenizer,
                        AutoModelForSeq2SeqLM,
                        pipeline as hf_pipeline,
                    )

                    logger.info(f"⏳ Đang tải summarization model: {model} (device={'cpu' if self.device == -1 else f'cuda:{self.device}'})...")

                    # Load tokenizer với legacy=False để tránh lỗi 'dict is not a Sequence' trên transformers mới
                    try:
                        tokenizer = AutoTokenizer.from_pretrained(model, legacy=False)
                    except (TypeError, AttributeError):
                        # Một số model cũ không hỗ trợ tham số legacy
                        tokenizer = AutoTokenizer.from_pretrained(model)

                    model_obj = AutoModelForSeq2SeqLM.from_pretrained(model)

                    self._pipeline = hf_pipeline(
                        "summarization",
                        model=model_obj,
                        tokenizer=tokenizer,
                        device=self.device,
                        max_length=self.max_length,
                        min_length=self.min_length,
                        num_beams=self.num_beams,
                        truncation=True,
                        do_sample=False,    # Greedy/beam search cho tính nhất quán
                        early_stopping=True,
                    )
                    logger.info(f"✅ Abstractive summarization model đã sẵn sàng: {model}")
                    return self._pipeline

                except (OSError, EnvironmentError) as e:
                    logger.warning(f"⚠️ Không tải được model {model}: {e}")
                    last_error = e
                    continue
                except ImportError as e:
                    raise ImportError(
                        f"Thiếu dependency: {e}\n"
                        "Chạy: pip install transformers torch"
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Lỗi khác khi tải {model}: {e}")
                    last_error = e
                    continue

            raise RuntimeError(
                f"Không thể tải bất kỳ model abstractive nào: {last_error}\n"
                "Hãy đảm bảo kết nối internet để tải model từ HuggingFace Hub,\n"
                "hoặc dùng strategy='extractive' / strategy='hybrid' (tự động fallback)."
            )

    def _prepare_input(self, content: str) -> str:
        """
        Bước 1 WF-03: TextRank chọn câu quan trọng → làm ngữ cảnh giới hạn.
        Giảm hallucination: BARTpho chỉ tóm tắt từ ngữ cảnh được chọn.
        """
        if self.use_textrank_context:
            context = self._textrank.get_top_context(content, top_n=TEXTRANK_TOP_N_CONTEXT)
        else:
            context = content

        # Truncate để không vượt max token của model
        return context[:MAX_INPUT_CHARS]

    def summarize(self, content: str, chunk_id: str) -> list[dict]:
        """
        Sinh tóm tắt trừu tượng:
          1. TextRank chọn ngữ cảnh (giảm hallucination)
          2. BARTpho sinh bản tóm tắt mới
          3. Tách thành từng câu (để caller NLI-check từng câu)

        Returns:
            list[dict]: mỗi câu kèm chunk_id, method="abstractive", nhan_nli="PENDING"
        """
        pipe = self._get_pipeline()
        input_text = self._prepare_input(content)

        if not input_text.strip():
            return []

        try:
            result = pipe(input_text)
            summary_text = result[0].get("summary_text", "").strip()

            if not summary_text:
                logger.warning(f"BARTpho trả về kết quả rỗng cho chunk {chunk_id}")
                return []

        except Exception as e:
            logger.error(f"Lỗi BARTpho inference cho chunk {chunk_id}: {e}")
            return []

        # Tách thành từng câu (mỗi câu sẽ được NLI-check riêng)
        raw_sentences = [s.strip() for s in re.split(r'[.!?]\s+', summary_text) if len(s.strip()) > 15]

        # Nếu model sinh 1 câu dài, chia thêm bằng dấu phẩy + mệnh đề
        sentences = []
        for s in raw_sentences:
            if len(s) > 200:
                # Chia câu dài tại dấu phẩy nếu cần
                sub = [p.strip() for p in s.split(",") if len(p.strip()) > 20]
                if len(sub) >= 2:
                    sentences.extend(sub[:3])  # Giới hạn 3 mệnh đề
                else:
                    sentences.append(s)
            else:
                sentences.append(s)

        if not sentences and summary_text:
            sentences = [summary_text[:300]]

        return [
            {
                "sentence": s,
                "chunk_id": chunk_id,
                "method": "abstractive",
                "nhan_nli": "PENDING",          # Chưa kiểm tra NLI
                "diem_faithfulness": None,
                "publish_action": "PENDING_NLI_CHECK",
                "source_context": input_text[:200],  # Context TextRank đã dùng
            }
            for s in sentences
        ]


# ─── Main Summarizer (tự động chọn strategy) ─────────────────────────────────

class DocumentSummarizer:
    """
    Tóm tắt toàn bộ văn bản, xử lý từng chunk và tích hợp NLI check.

    Strategies:
        "extractive" : TextRank an toàn, không hallucinate
        "abstractive": BARTpho/ViT5 + NLI check bắt buộc
        "hybrid"     : Thử abstractive trước, fallback extractive nếu lỗi
    """

    def __init__(
        self,
        strategy: str = "hybrid",   # Đổi default từ "extractive" → "hybrid"
        abstractive_model: str = DEFAULT_ABSTRACTIVE_MODEL,
        run_nli_check: bool = True,
        top_n_per_chunk: int = 3,
        device: int = -1,
    ):
        self.strategy = strategy
        self.run_nli_check = run_nli_check
        self._nli_checker = None
        self._abstractive_available = False

        if strategy == "extractive":
            self._summarizer = ExtractiveSummarizer(top_n_sentences=top_n_per_chunk)
            self._extractive_fallback = None
        elif strategy == "abstractive":
            self._summarizer = AbstractiveSummarizer(
                model_name=abstractive_model,
                device=device,
            )
            self._extractive_fallback = ExtractiveSummarizer(top_n_sentences=top_n_per_chunk)
        elif strategy == "hybrid":
            # Thử khởi tạo abstractive, fallback extractive nếu không load được
            self._abstractive_summarizer = AbstractiveSummarizer(
                model_name=abstractive_model,
                device=device,
            )
            self._summarizer = self._abstractive_summarizer
            self._extractive_fallback = ExtractiveSummarizer(top_n_sentences=top_n_per_chunk)
        else:
            raise ValueError(f"strategy phải là 'extractive', 'abstractive', hoặc 'hybrid'. Nhận: {strategy!r}")

    def _get_nli_checker(self):
        if self._nli_checker is None:
            try:
                from backend.services.nli.nli_checker import get_nli_checker
            except ImportError:
                from services.nli.nli_checker import get_nli_checker
            self._nli_checker = get_nli_checker()
        return self._nli_checker

    def _run_nli_check(self, sentences: list[dict], chunk_content: str) -> list[dict]:
        """
        Chạy NLI check từng câu theo WF-03.
        Chỉ cần thiết cho abstractive (extractive luôn đạt entailment).
        """
        checker = self._get_nli_checker()
        checked = []

        for sent_dict in sentences:
            # Extractive đã có nhãn entailment — bỏ qua
            if sent_dict.get("nhan_nli") == "entailment" and sent_dict.get("method") == "extractive":
                checked.append(sent_dict)
                continue

            nli_result = checker.check(
                premise=chunk_content,
                hypothesis=sent_dict["sentence"],
                chunk_id=sent_dict.get("chunk_id"),
            )

            sent_dict.update({
                "nhan_nli": nli_result["nhan_nli"],
                "diem_faithfulness": nli_result["diem_faithfulness"],
                "publish_action": nli_result["publish_action"],
                "nli_method": nli_result.get("method", "unknown"),
            })
            checked.append(sent_dict)

        return checked

    def summarize_chunk(self, chunk: dict) -> dict:
        """
        Tóm tắt 1 chunk, bao gồm NLI check theo WF-03.

        Với strategy "hybrid":
          - Thử AbstractiveSummarizer (BARTpho/ViT5)
          - Nếu model load lỗi → tự động fallback ExtractiveSummarizer
          - NLI check vẫn chạy đầy đủ dù dùng phương pháp nào

        Args:
            chunk: dict từ chunks.jsonl với chunk_id, content, doc_id...

        Returns:
            dict với sentences (list), overall_action, trang_thai_xuat_ban, strategy_used
        """
        chunk_id = chunk.get("chunk_id", "unknown")
        content = chunk.get("content", "")
        doc_id = chunk.get("doc_id", "unknown")

        if not content.strip():
            return {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "sentences": [],
                "overall_action": "SKIP_EMPTY",
                "trang_thai_xuat_ban": "PENDING_REVIEW",
                "strategy_used": "none",
            }

        # ── 1. Sinh tóm tắt ───────────────────────────────────────────────
        strategy_used = self.strategy
        sentences = []

        if self.strategy in ("abstractive", "hybrid"):
            try:
                sentences = self._summarizer.summarize(content=content, chunk_id=chunk_id)
                strategy_used = "abstractive"
            except (RuntimeError, ImportError) as e:
                logger.warning(
                    f"AbstractiveSummarizer thất bại cho chunk {chunk_id}: {e}\n"
                    "→ Fallback về ExtractiveSummarizer."
                )
                if self._extractive_fallback:
                    sentences = self._extractive_fallback.summarize(content=content, chunk_id=chunk_id)
                    strategy_used = "extractive_fallback"

        if not sentences and self.strategy == "extractive":
            sentences = self._summarizer.summarize(content=content, chunk_id=chunk_id)

        if not sentences:
            return {
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "sentences": [],
                "overall_action": "SKIP_EMPTY",
                "trang_thai_xuat_ban": "PENDING_REVIEW",
                "strategy_used": strategy_used,
            }

        # ── 2. NLI check từng câu (WF-03) ─────────────────────────────────
        if self.run_nli_check and strategy_used != "extractive":
            sentences = self._run_nli_check(sentences, chunk_content=content)

        # ── 3. Xác định overall action (WF-03 logic) ──────────────────────
        has_contradiction = any(s.get("nhan_nli") == "contradiction" for s in sentences)
        has_neutral = any(s.get("nhan_nli") == "neutral" for s in sentences)

        if has_contradiction:
            overall_action = "BLOCK_PENDING_REVIEW"
            trang_thai = "PENDING_REVIEW"
        elif has_neutral:
            overall_action = "WARN_PENDING_REVIEW"
            trang_thai = "PENDING_REVIEW"
        else:
            overall_action = "AUTO_PUBLISH"
            trang_thai = "PUBLISHED"

        # Thống kê
        n_entailment = sum(1 for s in sentences if s.get("nhan_nli") == "entailment")
        n_contradiction = sum(1 for s in sentences if s.get("nhan_nli") == "contradiction")
        n_neutral = sum(1 for s in sentences if s.get("nhan_nli") == "neutral")

        return {
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "sentences": sentences,
            "overall_action": overall_action,
            "trang_thai_xuat_ban": trang_thai,
            "has_contradiction": has_contradiction,
            "has_neutral": has_neutral,
            "strategy_used": strategy_used,
            "nli_stats": {
                "entailment": n_entailment,
                "contradiction": n_contradiction,
                "neutral": n_neutral,
                "total": len(sentences),
            },
        }

    def summarize_document(self, doc_id: str, chunks: list[dict]) -> dict:
        """
        Tóm tắt toàn bộ văn bản (nhiều chunks).
        WF-03: Nếu bất kỳ chunk nào có contradiction → chặn cả văn bản.

        Returns:
            dict tổng hợp với trang_thai_xuat_ban cho cả document
        """
        chunk_results = []
        any_contradiction = False
        any_neutral = False
        total_nli_stats = {"entailment": 0, "contradiction": 0, "neutral": 0, "total": 0}

        for chunk in chunks:
            result = self.summarize_chunk(chunk)
            chunk_results.append(result)
            if result.get("has_contradiction"):
                any_contradiction = True
            if result.get("has_neutral"):
                any_neutral = True
            # Tổng hợp NLI stats
            for k in total_nli_stats:
                total_nli_stats[k] += result.get("nli_stats", {}).get(k, 0)

        # WF-03: Có contradiction ở BẤT KỲ chunk nào → chặn cả văn bản
        if any_contradiction:
            doc_action = "BLOCK_PENDING_REVIEW"
            doc_status = "PENDING_REVIEW"
        elif any_neutral:
            doc_action = "WARN_PENDING_REVIEW"
            doc_status = "PENDING_REVIEW"
        else:
            doc_action = "AUTO_PUBLISH"
            doc_status = "PUBLISHED"

        # Thống kê strategy được dùng
        strategies_used = list({r.get("strategy_used", "unknown") for r in chunk_results})

        # Điểm faithfulness trung bình (chỉ từ câu đã có điểm)
        all_scores = [
            s.get("diem_faithfulness")
            for r in chunk_results
            for s in r.get("sentences", [])
            if s.get("diem_faithfulness") is not None
        ]
        avg_faithfulness = round(sum(all_scores) / len(all_scores), 4) if all_scores else None

        return {
            "doc_id": doc_id,
            "chunk_results": chunk_results,
            "overall_action": doc_action,
            "trang_thai_xuat_ban": doc_status,
            "total_chunks": len(chunk_results),
            "total_sentences": sum(len(r["sentences"]) for r in chunk_results),
            "strategies_used": strategies_used,
            "avg_faithfulness": avg_faithfulness,
            "nli_stats": total_nli_stats,
        }


# ─── Singleton cho Abstractive (tránh load model nhiều lần) ──────────────────

_abstractive_singleton: Optional[AbstractiveSummarizer] = None
_abstractive_lock = threading.Lock()


def get_abstractive_summarizer(
    model_name: str = DEFAULT_ABSTRACTIVE_MODEL,
    device: int = -1,
) -> AbstractiveSummarizer:
    """Trả về singleton AbstractiveSummarizer (thread-safe)."""
    global _abstractive_singleton
    if _abstractive_singleton is None:
        with _abstractive_lock:
            if _abstractive_singleton is None:
                _abstractive_singleton = AbstractiveSummarizer(
                    model_name=model_name, device=device
                )
    return _abstractive_singleton


# ─── Convenience functions ────────────────────────────────────────────────────

def summarize_document(
    doc_id: str,
    chunks: list[dict],
    strategy: str = "hybrid",
    run_nli_check: bool = True,
) -> dict:
    """Shortcut: tóm tắt 1 văn bản từ danh sách chunks.

    Args:
        doc_id: ID văn bản
        chunks: Danh sách chunks từ chunks.jsonl
        strategy: "extractive" | "abstractive" | "hybrid" (default: "hybrid")
        run_nli_check: Có chạy NLI check sau abstractive không (default: True)
    """
    summarizer = DocumentSummarizer(strategy=strategy, run_nli_check=run_nli_check)
    return summarizer.summarize_document(doc_id=doc_id, chunks=chunks)


# ─── CLI Test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Test Summarization Service")
    parser.add_argument(
        "--strategy",
        choices=["extractive", "abstractive", "hybrid"],
        default="extractive",
        help="Chiến lược tóm tắt (default: extractive để test nhanh)",
    )
    parser.add_argument(
        "--nli", action="store_true",
        help="Chạy NLI check sau khi tóm tắt",
    )
    parser.add_argument(
        "--chunks", type=int, default=3,
        help="Số chunk để test (default: 3)",
    )
    args = parser.parse_args()

    print(f"🧪 Test Summarization Service (strategy={args.strategy})...")

    chunks_path = Path("data/processed/chunks.jsonl")
    if not chunks_path.exists():
        # Thử relative path từ backend/
        chunks_path = Path("../data/processed/chunks.jsonl")
    if not chunks_path.exists():
        print(f"❌ Không tìm thấy chunks.jsonl")
        sys.exit(1)

    # Load N chunk đầu để test
    test_chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            test_chunks.append(json.loads(line.strip()))

    if not test_chunks:
        print("❌ Không có chunks để test.")
        sys.exit(1)

    summarizer = DocumentSummarizer(strategy="extractive", run_nli_check=False)

    for chunk in test_chunks:
        result = summarizer.summarize_chunk(chunk)
        print(f"\n📄 Chunk: {result['chunk_id']}")
        print(f"   Status: {result['trang_thai_xuat_ban']} | Action: {result['overall_action']}")
        for sent in result["sentences"][:2]:
            print(f"   → {sent['sentence'][:120]}...")
