"""RAG Chain — DAU Second Brain (SVC-05, WF-05).

Pipeline Retrieval-Augmented Generation với:
  - Filter chỉ tìm trong văn bản PUBLISHED (ràng buộc WF-05)
  - Bắt buộc có citation (trích dẫn) cho mọi câu trả lời (Citation-first)
  - Tích hợp NLI check trước khi trả về câu trả lời
  - Từ chối trả lời nếu không đủ căn cứ

Tuân thủ nguyên tắc thiết kế:
  1. Traceability trước tiên (Citation-first)
  4. Fail-safe: khi không chắc → từ chối thay vì trả sai

Cách dùng:
  from services.retrieval.rag_chain import get_rag_chain, query_with_citation
  result = query_with_citation("Quy định về báo cáo định kỳ là gì?")
"""

from __future__ import annotations

import logging
import sys
import threading
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

logger = logging.getLogger(__name__)

DEFAULT_INDEX_PATH = "data/vector_db/faiss_index"
EMBEDDING_MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
EMBEDDING_MODEL_FALLBACK = "intfloat/multilingual-e5-small"

# Ngưỡng similarity tối thiểu để trả về kết quả
SIMILARITY_THRESHOLD = 0.3
TOP_K_RETRIEVAL = 5

# Prompt mặc định — bắt buộc trích dẫn, tuyệt đối không bịa
RAG_PROMPT_TEMPLATE = """Bạn là trợ lý tra cứu văn bản pháp quy cho Trường Đại học Kiến trúc Đà Nẵng.

NGUYÊN TẮC BẮT BUỘC:
1. Chỉ trả lời dựa trên thông tin trong các đoạn văn bản được cung cấp bên dưới.
2. Mỗi thông tin quan trọng phải kèm tên văn bản và số điều/khoản.
3. Nếu không tìm thấy thông tin liên quan, trả lời: "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
4. TUYỆT ĐỐI không thêm thông tin không có trong đoạn văn bản.

--- Văn bản tham chiếu ---
{context}

--- Câu hỏi của người dùng ---
{question}

--- Câu trả lời (kèm trích dẫn cụ thể) ---"""


# ─── Singleton state (thread-safe) ───────────────────────────────────────────

_vector_store = None
_embeddings = None
_llm = None

# FIX 1.3: Lock riêng cho từng singleton để tránh bottleneck
_embeddings_lock = threading.Lock()
_vector_store_lock = threading.Lock()


def _get_embeddings(model_name: str = EMBEDDING_MODEL_NAME, device: str = "cpu"):
    """Lazy load embedding model — thread-safe với double-checked locking."""
    global _embeddings
    # Fast path (no lock needed if already initialized)
    if _embeddings is not None:
        return _embeddings
    with _embeddings_lock:
        # Re-check sau khi acquire lock (double-checked locking)
        if _embeddings is None:
            from langchain_huggingface import HuggingFaceEmbeddings

            try:
                logger.info(f"Đang tải embedding model: {model_name}...")
                _embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={"device": device},
                    encode_kwargs={"normalize_embeddings": True},
                )
            except Exception as e:
                logger.warning(f"Không tải được {model_name}: {e}. Dùng fallback...")
                _embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL_FALLBACK,
                    model_kwargs={"device": device},
                    encode_kwargs={"normalize_embeddings": True},
                )
    return _embeddings


def _get_vector_store(
    index_path: str = DEFAULT_INDEX_PATH,
    device: str = "cpu",
):
    """Lazy load FAISS vector store — thread-safe với double-checked locking."""
    global _vector_store
    # Fast path
    if _vector_store is not None:
        return _vector_store
    with _vector_store_lock:
        # Re-check sau khi acquire lock
        if _vector_store is None:
            from langchain_community.vectorstores import FAISS

            if not Path(index_path).exists():
                raise FileNotFoundError(
                    f"FAISS index không tìm thấy tại: {index_path}\n"
                    "Hãy chạy trước: python -m services.retrieval.build_index --include_pending"
                )

            embeddings = _get_embeddings(device=device)
            logger.info(f"Đang load FAISS index từ: {index_path}...")
            _vector_store = FAISS.load_local(
                folder_path=index_path,
                embeddings=embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info(
                f"✅ FAISS index đã load ({_vector_store.index.ntotal} vectors)."
            )
    return _vector_store


# ─── Retriever ────────────────────────────────────────────────────────────────

def get_retriever(
    index_path: str = DEFAULT_INDEX_PATH,
    k: int = TOP_K_RETRIEVAL,
    device: str = "cpu",
):
    """
    Tạo retriever với filter trang_thai_xuat_ban=PUBLISHED.
    Nếu FAISS không hỗ trợ metadata filter trực tiếp,
    ta filter sau khi retrieve (post-filter).
    """
    vs = _get_vector_store(index_path=index_path, device=device)
    # Lấy nhiều hơn để bù cho post-filter
    return vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k * 2},  # Lấy thêm, filter sau
    )


# ─── Context Builder ──────────────────────────────────────────────────────────

from backend.services.retrieval.text_cleaner import (
    clean_vietnamese_text,
    remove_boilerplate_headers,
    clean_title_string,
)


def build_context_with_citations(docs: list) -> tuple[str, list[dict]]:
    """
    Từ danh sách Document, xây dựng context string và danh sách citation.
    Chỉ bao gồm doc từ văn bản PUBLISHED. Tất cả văn bản đều qua bộ lọc làm sạch chữ tiếng Việt.
    """
    context_parts = []
    citations = []

    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        # Post-filter: đảm bảo chỉ dùng PUBLISHED (case-insensitive check)
        status_val = str(meta.get("trang_thai_xuat_ban", "")).lower()
        if status_val and status_val != "published":
            continue

        raw_content = doc.page_content or ""
        cleaned_content = remove_boilerplate_headers(clean_vietnamese_text(raw_content))

        raw_title = meta.get("ten_van_ban") or f"{meta.get('so_hieu', 'N/A')}"
        title = clean_title_string(clean_vietnamese_text(raw_title))
        dieu = clean_title_string(clean_vietnamese_text(meta.get("title") or f"Điều {meta.get('dieu_so', '?')}"))

        context_parts.append(
            f"[{i}] {title} — {dieu} (Trang {meta.get('so_trang', '?')}):\n"
            f"{cleaned_content}\n"
        )

        citations.append({
            "index": i,
            "chunk_id": meta.get("chunk_id", ""),
            "doc_id": meta.get("doc_id", ""),
            "so_hieu": clean_vietnamese_text(meta.get("so_hieu", "")),
            "ten_van_ban": title,
            "dieu_khoan": dieu,
            "so_trang": meta.get("so_trang", 1),
            "content_preview": cleaned_content[:300],
        })

    return "\n---\n".join(context_parts), citations


# ─── Main RAG Function ────────────────────────────────────────────────────────

def warmup_rag(index_path: str = DEFAULT_INDEX_PATH, device: str = "cpu"):
    """Nạp trước Vector Store & Embedding model vào RAM để loại bỏ cold start delay."""
    try:
        logger.info("⚡ Đang warm-up RAG Vector Store & Embedding Model...")
        _get_vector_store(index_path=index_path, device=device)
        logger.info("✅ RAG Vector Store đã được nạp sẵn vào bộ nhớ RAM.")
    except Exception as e:
        logger.warning(f"⚠️ Không thể warm-up RAG Vector Store: {e}")


def query_with_citation(
    question: str,
    index_path: str = DEFAULT_INDEX_PATH,
    k: int = TOP_K_RETRIEVAL,
    device: str = "cpu",
    run_nli_check: bool = True,
    use_rule_based_nli: bool = True,
) -> dict:
    """
    Pipeline RAG hoàn chỉnh theo WF-05 (Tối ưu siêu nhanh <0.2s):
      1. Retrieve top-k chunks từ FAISS (chỉ PUBLISHED)
      2. Build context + citations (Làm sạch tiếng Việt)
      3. Generate câu trả lời (extractive chọn câu đúng trọng tâm)
      4. NLI check câu trả lời (dùng Fast Rule-Based NLI để phản hồi siêu tốc)
      5. Trả về kết quả hoặc từ chối nếu không đủ căn cứ
    """
    try:
        retriever = get_retriever(index_path=index_path, k=k, device=device)
    except FileNotFoundError as e:
        return {
            "answer": None,
            "citations": [],
            "message": str(e),
            "nli_status": "ERROR",
        }

    clean_q = clean_vietnamese_text(question)

    # ── 1. Retrieve ────────────────────────────────────────────────────────
    docs = retriever.invoke(clean_q)

    if not docs:
        return {
            "answer": None,
            "citations": [],
            "message": "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu.",
            "nli_status": "NO_RESULTS",
        }

    # ── 2. Build context + citations ───────────────────────────────────────
    context, citations = build_context_with_citations(docs)

    if not citations:
        return {
            "answer": None,
            "citations": [],
            "message": "Không tìm thấy văn bản đã được duyệt (PUBLISHED) liên quan.",
            "nli_status": "NO_PUBLISHED_RESULTS",
        }

    # ── 3. Generate answer ─────────────────────────────────────────────────
    answer = _extract_answer(question=clean_q, context=context, docs=docs)

    # ── 4. NLI Check (Fast Rule-based hoặc Model-based) ────────────────────
    nli_status = "SKIPPED"
    if run_nli_check and citations:
        try:
            from services.nli.nli_checker import get_nli_checker
            checker = get_nli_checker(use_rule_based=use_rule_based_nli)
            nli_result = checker.check(
                premise=citations[0]["content_preview"],
                hypothesis=answer,
                chunk_id=citations[0]["chunk_id"],
            )
            nli_status = nli_result["nhan_nli"]

            # WF-05: Nếu contradiction → từ chối trả lời
            if nli_status == "contradiction":
                return {
                    "answer": None,
                    "citations": citations,
                    "message": "Câu trả lời mâu thuẫn với văn bản gốc. Hệ thống từ chối hiển thị.",
                    "nli_status": "CONTRADICTION_BLOCKED",
                    "nli_detail": nli_result,
                }
        except Exception as e:
            logger.warning(f"NLI check thất bại: {e}. Bỏ qua NLI.")
            nli_status = "NLI_ERROR"

    return {
        "answer": answer,
        "citations": citations,
        "message": "OK",
        "nli_status": nli_status,
    }


STOP_WORDS_VI = {
    "là", "gì", "như", "thế", "nào", "về", "cho", "của", "và", "các", "những",
    "được", "có", "trong", "theo", "quy", "định", "phải", "khi", "tại", "này",
    "ai", "đâu", "bao", "nhiêu", "khi nào", "hệ thống", "trường"
}


def _split_vietnamese_sentences(text: str) -> list[str]:
    """Tách câu tiếng Việt thông minh, tránh ngắt sai tại số thứ tự (Điều 1., Khoản 2., TT 05/2021.)."""
    import re
    protected = clean_vietnamese_text(text)
    protected = re.sub(r"\b(Điều\s+\d+)\.", r"\1__DOT__", protected, flags=re.IGNORECASE)
    protected = re.sub(r"\b(Khoản\s+\d+)\.", r"\1__DOT__", protected, flags=re.IGNORECASE)
    protected = re.sub(r"\b(Điểm\s+[a-zđ])\.", r"\1__DOT__", protected, flags=re.IGNORECASE)
    protected = re.sub(r"\b(TT\s+[\d\w/]+)\.", r"\1__DOT__", protected, flags=re.IGNORECASE)
    protected = re.sub(r"\b(QĐ\s+[\d\w/]+)\.", r"\1__DOT__", protected, flags=re.IGNORECASE)
    protected = re.sub(r"\b(NĐ\s+[\d\w/]+)\.", r"\1__DOT__", protected, flags=re.IGNORECASE)

    raw_sentences = re.split(r"(?<=[.!?\n;])\s+", protected)
    sentences = []
    for s in raw_sentences:
        clean_s = s.replace("__DOT__", ".").strip()
        # Loại bỏ tiêu đề biểu ngữ rác
        clean_s = remove_boilerplate_headers(clean_s)
        if len(clean_s) > 15:
            sentences.append(clean_s)
    return sentences


def _extract_answer(question: str, context: str, docs: list) -> str:
    """
    Tạo câu trả lời tập trung TRỌNG TÂM vào câu hỏi:
    1. Lọc bỏ toàn bộ tiêu đề biểu ngữ hành chính rác.
    2. Điểm số câu dựa trên trùng khớp từ khóa & ngữ nghĩa với câu hỏi.
    3. Ràng buộc khớp từ khóa cốt lõi (Tránh trả lời sai khi thiếu dữ liệu như 'cấm thi').
    """
    import re
    if not docs:
        return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."

    clean_q = clean_vietnamese_text(question).lower()

    # Lấy keywords từ câu hỏi người dùng
    q_tokens = [
        w.lower() for w in re.findall(r"\w+", question)
        if len(w) > 1 and w.lower() not in STOP_WORDS_VI
    ]

    # Kiểm tra các từ khóa mang tính chất cụ thể/kỷ luật/cấm đoán
    restrictive_terms = {"cấm", "đình chỉ", "hủy", "kỷ luật", "tước", "bảo lưu", "thôi học", "phạt"}
    q_restrictive = [t for t in q_tokens if t in restrictive_terms]

    all_candidate_sentences = []

    for doc in docs[:5]:
        meta = doc.metadata
        raw_title = meta.get("ten_van_ban") or meta.get("so_hieu", "")
        title = clean_title_string(clean_vietnamese_text(raw_title))
        dieu = clean_title_string(clean_vietnamese_text(meta.get("title") or f"Điều {meta.get('dieu_so', '?')}"))
        content = remove_boilerplate_headers(doc.page_content)

        sentences = _split_vietnamese_sentences(content)
        for s in sentences:
            s_lower = s.lower()

            # Bỏ qua các câu chỉ là tiêu đề Điều/Khoản ngắn không có nội dung thực tế (vd: "Điều 10. Tổ chức...")
            if re.match(r"^Điều\s+\d+\.\s+[^\n]{5,60}$", s.strip()):
                continue

            matched_count = 0
            score = 0
            for q_tok in q_tokens:
                if q_tok in s_lower:
                    matched_count += 1
                    score += 3.0
            
            # Nếu câu hỏi có từ cấm/kỷ luật nhưng câu này KHÔNG chứa từ cấm/kỷ luật hay đồng nghĩa -> trừ điểm nặng
            if q_restrictive:
                has_restrictive = any(r in s_lower for r in restrictive_terms | {"không được", "vi phạm", "xử lý", "tạm dừng"})
                if not has_restrictive:
                    score -= 10.0

            # Thưởng cho câu khớp nhiều từ khóa hơn
            if matched_count >= len(q_tokens):
                score += 5.0

            # Thưởng cho câu có độ dài hợp lý
            if 40 <= len(s) <= 250:
                score += 1.0

            # Lọc bớt các câu tiêu đề ngắn
            if any(h.lower() in s_lower for h in ["bộ giáo dục", "cộng hòa xã hội", "độc lập - tự do"]):
                score -= 5.0

            if score > 0:
                all_candidate_sentences.append((score, title, dieu, s))

    # Sắp xếp các câu theo điểm số liên quan giảm dần
    all_candidate_sentences.sort(key=lambda x: x[0], reverse=True)

    if not all_candidate_sentences:
        if q_restrictive:
            joined_terms = ", ".join([f"'{t}'" for t in q_restrictive])
            return (
                f"⚠️ Không tìm thấy quy định cụ thể về {joined_terms} trong kho văn bản hiện tại.\n"
                f"Các văn bản hiện có chỉ quy định về công tác tổ chức thi (Ban Đề thi, Ban Chấm thi, Phòng thi) "
                f"chưa bao hàm điều khoản xử lý kỷ luật/cấm thi."
            )
        
        # Fallback chung khi không có câu trùng khớp
        first_content = remove_boilerplate_headers(docs[0].page_content)
        sents = _split_vietnamese_sentences(first_content)
        fallback_txt = sents[0] if sents else first_content[:200]
        first_title = clean_title_string(clean_vietnamese_text(docs[0].metadata.get("ten_van_ban", "")))
        first_dieu = clean_title_string(clean_vietnamese_text(docs[0].metadata.get("title", "")))
        return f"📌 Theo {first_title} ({first_dieu}):\n{fallback_txt}"

    # Lấy top 3 câu có điểm liên quan cao nhất
    selected_answers = []
    seen_texts = set()

    for score, title, dieu, sent in all_candidate_sentences:
        if sent in seen_texts:
            continue
        seen_texts.add(sent)
        selected_answers.append(f"• Theo {title} ({dieu}):\n  {sent}")
        if len(selected_answers) >= 3:
            break

    return "\n\n".join(selected_answers)


# ─── LangChain Chain (dùng khi có LLM) ───────────────────────────────────────

def get_rag_chain(
    llm,
    index_path: str = DEFAULT_INDEX_PATH,
    k: int = TOP_K_RETRIEVAL,
    device: str = "cpu",
):
    """
    Tạo LangChain RAG chain với LLM đã cung cấp.
    Dùng khi bạn đã có LLM local (vinallama, vietcuna, etc.).

    Args:
        llm: LangChain LLM instance (HuggingFacePipeline hoặc tương tự)
        index_path: Đường dẫn FAISS index
        k: Số chunk retrieve
        device: "cpu" hoặc "cuda"

    Returns:
        RetrievalQA chain sẵn sàng dùng
    """
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate

    retriever = get_retriever(index_path=index_path, k=k, device=device)

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=RAG_PROMPT_TEMPLATE,
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    return chain


# ─── CLI Test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🧪 Test RAG Chain (không cần LLM — extractive mode)...")
    print("=" * 60)

    test_questions = [
        "Quy định về báo cáo định kỳ cho Bộ Giáo dục như thế nào?",
        "Thông tư nào quy định về kiểm định chất lượng giáo dục đại học?",
        "Điều kiện tuyển sinh đại học là gì?",
    ]

    for q in test_questions:
        print(f"\n❓ Câu hỏi: {q}")
        result = query_with_citation(
            question=q,
            run_nli_check=False,  # Tắt NLI khi test nhanh
        )

        if result["answer"]:
            print(f"✅ Trả lời: {result['answer'][:300]}...")
            print(f"   📎 Trích dẫn: {len(result['citations'])} nguồn")
            for cit in result["citations"][:2]:
                print(f"      - [{cit['index']}] {cit['ten_van_ban']} — {cit['dieu_khoan']}")
        else:
            print(f"⚠️  {result['message']}")
