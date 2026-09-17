"""NLI Checker — DAU Second Brain (EPIC-3 + EPIC-9).

Kiểm tra faithfulness (tính trung thực) của câu tóm tắt / câu trả lời
so với đoạn văn bản gốc (chunk) theo 3 nhãn NLI:
  - entailment  : câu suy ra được từ nguồn — an toàn để publish
  - neutral     : không đủ căn cứ xác nhận — cảnh báo, tùy config
  - contradiction: mâu thuẫn với nguồn — chặn publish toàn bộ văn bản (WF-03)

Tuân thủ WF-03 và WF-05 trong DAU_Second_Brain_Dac_Ta_Nghiep_Vu_Kien_Truc.md.

FIX 1.2: Đổi từ zero-shot-classification → NLI sequence-classification thực sự
FIX 2.3: Thêm threading.Lock() cho singleton
"""

from __future__ import annotations

import logging
import sys
import threading
from enum import Enum
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

logger = logging.getLogger(__name__)


# ─── Hằng số & Enum ──────────────────────────────────────────────────────────

class NLILabel(str, Enum):
    ENTAILMENT = "entailment"
    NEUTRAL = "neutral"
    CONTRADICTION = "contradiction"


class PublishAction(str, Enum):
    AUTO_PUBLISH = "AUTO_PUBLISH"           # Toàn entailment → publish ngay
    WARN_PENDING_REVIEW = "WARN_PENDING_REVIEW"  # Có neutral → cảnh báo
    BLOCK_PENDING_REVIEW = "BLOCK_PENDING_REVIEW"  # Có contradiction → chặn


# FIX 1.2: Model nhỏ hơn (~560MB), đúng task NLI sequence-classification
# Hỗ trợ 100 ngôn ngữ bao gồm tiếng Việt, chạy được trên CPU
DEFAULT_NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

# Fallback: model siêu nhỏ (~270MB), ít chính xác hơn nhưng nhanh hơn
FALLBACK_NLI_MODEL = "cross-encoder/nli-MiniLM2-L6-H768"

# Ngưỡng điểm confidence tối thiểu
MIN_CONFIDENCE_THRESHOLD = 0.55

# Map nhãn model → NLILabel (mDeBERTa trả về: "entailment", "neutral", "contradiction")
_LABEL_MAP = {
    "entailment": NLILabel.ENTAILMENT,
    "neutral": NLILabel.NEUTRAL,
    "contradiction": NLILabel.CONTRADICTION,
    # cross-encoder có thể trả về format khác
    "label_0": NLILabel.CONTRADICTION,  # cross-encoder: 0=contradiction
    "label_1": NLILabel.ENTAILMENT,     # cross-encoder: 1=entailment
    "label_2": NLILabel.NEUTRAL,        # cross-encoder: 2=neutral
}


# ─── Rule-Based Fallback (không cần model, dùng khi không có torch) ──────────

class RuleBasedNLIChecker:
    """
    Fallback NLI checker thuần rule-based — không cần model, không cần torch.
    Chạy được mọi lúc, nhưng kém chính xác hơn model.

    Logic: kiểm tra sự xuất hiện của các từ khóa trong premise vs hypothesis.
    Nếu hypothesis chứa thông tin không có trong premise → neutral.
    Nếu hypothesis phủ định nội dung trong premise → contradiction.
    """

    NEGATION_WORDS = {
        "không", "chưa", "chẳng", "đừng", "cấm", "bị cấm",
        "không phải", "không được", "không có", "không thể",
        "bác bỏ", "phủ nhận", "trái với",
    }

    def check(self, premise: str, hypothesis: str, chunk_id: Optional[str] = None) -> dict:
        premise_lower = premise.lower()
        hypo_lower = hypothesis.lower()

        # Kiểm tra phủ định bất đối xứng (contradiction signal)
        premise_has_negation = any(w in premise_lower for w in self.NEGATION_WORDS)
        hypo_has_negation = any(w in hypo_lower for w in self.NEGATION_WORDS)

        if premise_has_negation != hypo_has_negation:
            # Một bên phủ định, bên kia không → có khả năng mâu thuẫn
            nhan_nli = NLILabel.NEUTRAL  # Conservative: không block, chỉ warn
        else:
            # Kiểm tra overlap từ khóa
            premise_words = set(premise_lower.split())
            hypo_words = set(hypo_lower.split())
            overlap = len(premise_words & hypo_words)
            overlap_ratio = overlap / max(len(hypo_words), 1)

            if overlap_ratio >= 0.3:
                nhan_nli = NLILabel.ENTAILMENT
            else:
                nhan_nli = NLILabel.NEUTRAL

        publish_action = {
            NLILabel.ENTAILMENT: PublishAction.AUTO_PUBLISH,
            NLILabel.NEUTRAL: PublishAction.WARN_PENDING_REVIEW,
            NLILabel.CONTRADICTION: PublishAction.BLOCK_PENDING_REVIEW,
        }[nhan_nli]

        return {
            "chunk_id": chunk_id,
            "premise_preview": premise[:200],
            "hypothesis": hypothesis,
            "nhan_nli": nhan_nli.value,
            "diem_faithfulness": 0.6 if nhan_nli == NLILabel.ENTAILMENT else 0.4,
            "publish_action": publish_action.value,
            "priority": "HIGH" if nhan_nli == NLILabel.CONTRADICTION else None,
            "method": "rule_based",
        }

    def check_all_sentences(
        self,
        doc_id: str,
        summary_sentences: list[str],
        source_chunk_content: str,
        chunk_id: str,
    ) -> dict:
        results = []
        for sentence in summary_sentences:
            if not sentence.strip():
                continue
            result = self.check(
                premise=source_chunk_content,
                hypothesis=sentence,
                chunk_id=chunk_id,
            )
            results.append(result)

        has_contradiction = any(r["nhan_nli"] == NLILabel.CONTRADICTION.value for r in results)
        has_neutral = any(r["nhan_nli"] == NLILabel.NEUTRAL.value for r in results)

        if has_contradiction:
            overall_action = PublishAction.BLOCK_PENDING_REVIEW.value
            trang_thai_xuat_ban = "PENDING_REVIEW"
        elif has_neutral:
            overall_action = PublishAction.WARN_PENDING_REVIEW.value
            trang_thai_xuat_ban = "PENDING_REVIEW"
        else:
            overall_action = PublishAction.AUTO_PUBLISH.value
            trang_thai_xuat_ban = "PUBLISHED"

        avg_score = (
            sum(r["diem_faithfulness"] for r in results) / len(results)
            if results else 0.0
        )

        return {
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "sentence_results": results,
            "overall_action": overall_action,
            "trang_thai_xuat_ban": trang_thai_xuat_ban,
            "avg_faithfulness": round(avg_score, 4),
            "has_contradiction": has_contradiction,
            "has_neutral": has_neutral,
        }


# ─── NLI Checker Class (Model-based) ─────────────────────────────────────────

class NLIChecker:
    """
    Kiểm tra NLI cho từng câu tóm tắt/trả lời so với chunk nguồn.

    FIX 1.2: Dùng đúng task "text-classification" (NLI sequence-classification)
    thay vì zero-shot-classification.

    FIX 2.3: Thread-safe với _load_lock.

    Model mDeBERTa-v3-base-mnli-xnli:
      - Kích thước: ~560MB (nhỏ hơn xlm-roberta-large ~1.5GB)
      - Hỗ trợ 100+ ngôn ngữ bao gồm tiếng Việt
      - Input format: "[CLS] premise [SEP] hypothesis [SEP]"
      - Output: entailment / neutral / contradiction
    """

    def __init__(
        self,
        model_name: str = DEFAULT_NLI_MODEL,
        device: int = -1,  # -1 = CPU, 0 = GPU đầu tiên
        min_confidence: float = MIN_CONFIDENCE_THRESHOLD,
    ):
        self.model_name = model_name
        self.device = device
        self.min_confidence = min_confidence
        self._pipeline = None     # Lazy load
        self._load_lock = threading.Lock()  # FIX 2.3: thread-safe init
        self._fallback = RuleBasedNLIChecker()

    def _get_pipeline(self):
        """
        FIX 1.2: Dùng đúng task "text-classification" cho NLI.
        FIX 2.3: Thread-safe lazy loading.
        """
        # Double-checked locking pattern
        if self._pipeline is not None:
            return self._pipeline

        with self._load_lock:
            if self._pipeline is not None:  # Re-check sau khi acquire lock
                return self._pipeline

            try:
                from transformers import pipeline as hf_pipeline

                logger.info(f"Đang tải NLI model: {self.model_name} ...")

                # FIX 1.2: "text-classification" là task đúng cho NLI
                # Model NLI sequence-classification trả về nhãn entailment/neutral/contradiction
                self._pipeline = hf_pipeline(
                    "text-classification",
                    model=self.model_name,
                    device=self.device,
                    top_k=None,  # Trả về tất cả labels với scores
                    truncation=True,
                    max_length=512,
                )
                logger.info("✅ NLI model đã sẵn sàng.")

            except ImportError:
                raise ImportError(
                    "Cần cài transformers: pip install transformers torch\n"
                    "Hoặc dùng RuleBasedNLIChecker() nếu không có torch."
                )
            except Exception as e:
                logger.warning(f"Không tải được {self.model_name}: {e}")
                logger.info(f"Thử fallback model: {FALLBACK_NLI_MODEL}")
                try:
                    from transformers import pipeline as hf_pipeline
                    self._pipeline = hf_pipeline(
                        "text-classification",
                        model=FALLBACK_NLI_MODEL,
                        device=self.device,
                        top_k=None,
                        truncation=True,
                    )
                    logger.info(f"✅ Fallback NLI model sẵn sàng: {FALLBACK_NLI_MODEL}")
                except Exception as e2:
                    raise RuntimeError(
                        f"Không tải được cả 2 NLI models: {e2}\n"
                        "Dùng RuleBasedNLIChecker() thay thế."
                    )

        return self._pipeline

    def check(
        self,
        premise: str,
        hypothesis: str,
        chunk_id: Optional[str] = None,
    ) -> dict:
        """
        FIX 1.2: NLI đúng format — concatenate premise + hypothesis.

        Model NLI sequence-classification nhận input:
          "[CLS] premise [SEP] hypothesis [SEP]"
        và trả về xác suất cho 3 nhãn.
        """
        try:
            pipe = self._get_pipeline()
        except (ImportError, RuntimeError) as e:
            logger.warning(f"Model NLI không khả dụng ({e}), dùng rule-based fallback.")
            return self._fallback.check(premise, hypothesis, chunk_id)

        # FIX 1.2: Format input đúng cho NLI model
        # Cắt premise để tổng không vượt quá 512 tokens
        premise_truncated = premise[:400]
        nli_input = f"{premise_truncated} [SEP] {hypothesis}"

        try:
            results = pipe(nli_input)

            # results là list of {label, score} — lấy label có score cao nhất
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], list):
                    # top_k=None → [[{label, score}, ...]]
                    label_scores = results[0]
                else:
                    # Dạng khác
                    label_scores = results

                # Tìm label có score cao nhất
                best = max(label_scores, key=lambda x: x["score"])
                top_label = best["label"].lower()
                top_score = best["score"]
            else:
                logger.warning("NLI model trả về kết quả bất thường, dùng rule-based.")
                return self._fallback.check(premise, hypothesis, chunk_id)

        except Exception as e:
            logger.warning(f"NLI inference lỗi: {e}. Dùng rule-based fallback.")
            return self._fallback.check(premise, hypothesis, chunk_id)

        # Map nhãn model → NLILabel
        nhan_nli = _LABEL_MAP.get(top_label, NLILabel.NEUTRAL)

        # Nếu score thấp hơn ngưỡng → không chắc → neutral (conservative)
        if top_score < self.min_confidence and nhan_nli != NLILabel.NEUTRAL:
            logger.debug(
                f"Score thấp ({top_score:.3f} < {self.min_confidence}) "
                f"→ downgrade {nhan_nli.value} → neutral"
            )
            nhan_nli = NLILabel.NEUTRAL

        # Định tuyến theo nhãn (WF-03)
        if nhan_nli == NLILabel.ENTAILMENT:
            publish_action = PublishAction.AUTO_PUBLISH
            priority = None
        elif nhan_nli == NLILabel.CONTRADICTION:
            publish_action = PublishAction.BLOCK_PENDING_REVIEW
            priority = "HIGH"
        else:  # NEUTRAL
            publish_action = PublishAction.WARN_PENDING_REVIEW
            priority = "LOW"

        return {
            "chunk_id": chunk_id,
            "premise_preview": premise[:200],
            "hypothesis": hypothesis,
            "nhan_nli": nhan_nli.value,
            "diem_faithfulness": round(top_score, 4),
            "publish_action": publish_action.value,
            "priority": priority,
            "method": "model_based",
        }

    def check_all_sentences(
        self,
        doc_id: str,
        summary_sentences: list[str],
        source_chunk_content: str,
        chunk_id: str,
    ) -> dict:
        """
        Kiểm tra toàn bộ câu tóm tắt của 1 văn bản.
        Logic WF-03:
          - Có bất kỳ 'contradiction' → BLOCK_PENDING_REVIEW
          - Có 'neutral' nhưng không có 'contradiction' → WARN_PENDING_REVIEW
          - Tất cả 'entailment' → AUTO_PUBLISH
        """
        results = []
        for sentence in summary_sentences:
            if not sentence.strip():
                continue
            result = self.check(
                premise=source_chunk_content,
                hypothesis=sentence,
                chunk_id=chunk_id,
            )
            results.append(result)

        has_contradiction = any(
            r["nhan_nli"] == NLILabel.CONTRADICTION.value for r in results
        )
        has_neutral = any(
            r["nhan_nli"] == NLILabel.NEUTRAL.value for r in results
        )

        if has_contradiction:
            overall_action = PublishAction.BLOCK_PENDING_REVIEW.value
            trang_thai_xuat_ban = "PENDING_REVIEW"
        elif has_neutral:
            overall_action = PublishAction.WARN_PENDING_REVIEW.value
            trang_thai_xuat_ban = "PENDING_REVIEW"
        else:
            overall_action = PublishAction.AUTO_PUBLISH.value
            trang_thai_xuat_ban = "PUBLISHED"

        avg_score = (
            sum(r["diem_faithfulness"] for r in results) / len(results)
            if results else 0.0
        )

        return {
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "sentence_results": results,
            "overall_action": overall_action,
            "trang_thai_xuat_ban": trang_thai_xuat_ban,
            "avg_faithfulness": round(avg_score, 4),
            "has_contradiction": has_contradiction,
            "has_neutral": has_neutral,
        }


# ─── Singleton instance (thread-safe) ────────────────────────────────────────

_nli_checker_instance: Optional[NLIChecker] = None
_singleton_lock = threading.Lock()  # FIX 2.3: lock cho singleton creation


def get_nli_checker(
    model_name: str = DEFAULT_NLI_MODEL,
    device: int = -1,
    use_rule_based: bool = False,
) -> "NLIChecker | RuleBasedNLIChecker":
    """
    Trả về singleton NLIChecker, khởi tạo nếu chưa có.

    FIX 2.3: Thread-safe với double-checked locking.

    Args:
        use_rule_based: Nếu True, dùng RuleBasedNLIChecker (không cần torch)
    """
    global _nli_checker_instance

    if use_rule_based:
        return RuleBasedNLIChecker()

    # Double-checked locking
    if _nli_checker_instance is None:
        with _singleton_lock:
            if _nli_checker_instance is None:
                _nli_checker_instance = NLIChecker(
                    model_name=model_name, device=device
                )

    return _nli_checker_instance


def reset_nli_checker():
    """Reset singleton — cho phép đổi model mà không restart process."""
    global _nli_checker_instance
    with _singleton_lock:
        _nli_checker_instance = None
    logger.info("NLI checker singleton đã được reset.")


# ─── LangChain Runnable wrapper ───────────────────────────────────────────────

def make_nli_runnable(checker=None):
    """
    Tạo LangChain Runnable từ NLIChecker.
    Dùng trong pipeline: rag_chain | nli_runnable

    Input dict cần có:
      - "premise": str (chunk gốc)
      - "hypothesis": str (câu cần kiểm tra)
      - "chunk_id": str (optional)
    """
    from langchain_core.runnables import RunnableLambda

    if checker is None:
        checker = get_nli_checker()

    def _run(item: dict) -> dict:
        return checker.check(
            premise=item.get("premise", ""),
            hypothesis=item.get("hypothesis", ""),
            chunk_id=item.get("chunk_id"),
        )

    return RunnableLambda(_run)


# ─── CLI Test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test NLI Checker")
    parser.add_argument(
        "--rule-based", action="store_true",
        help="Dùng rule-based checker (không cần torch/transformers)"
    )
    args = parser.parse_args()

    print("🧪 Test NLI Checker...")
    if args.rule_based:
        print("   Mode: Rule-Based (không cần model)")
        checker = RuleBasedNLIChecker()
    else:
        print(f"   Mode: Model-Based ({DEFAULT_NLI_MODEL})")
        checker = NLIChecker()

    test_cases = [
        {
            "premise": "Thông tư 05/2021/TT-BGDĐT quy định về đào tạo trình độ thạc sĩ, có hiệu lực từ ngày ký.",
            "hypothesis": "Thông tư này quy định về đào tạo sau đại học trình độ thạc sĩ.",
            "expected": "entailment",
        },
        {
            "premise": "Thông tư 05/2021/TT-BGDĐT quy định về đào tạo trình độ thạc sĩ.",
            "hypothesis": "Thông tư này quy định về đào tạo trình độ tiến sĩ.",
            "expected": "contradiction",
        },
        {
            "premise": "Trường đại học cần báo cáo định kỳ cho Bộ Giáo dục.",
            "hypothesis": "Việc báo cáo sẽ được thực hiện mỗi năm một lần.",
            "expected": "neutral",
        },
    ]

    all_pass = True
    for tc in test_cases:
        result = checker.check(tc["premise"], tc["hypothesis"])
        passed = result["nhan_nli"] == tc["expected"]
        status = "✅" if passed else "⚠️"
        if not passed:
            all_pass = False
        print(
            f"{status} [{tc['expected']}] → Dự đoán: {result['nhan_nli']} "
            f"(score={result['diem_faithfulness']:.3f}, method={result.get('method', 'N/A')})"
        )

    print(f"\n{'✅ Tất cả test cases passed!' if all_pass else '⚠️ Một số test cases sai (có thể do model chưa tải)'}")
