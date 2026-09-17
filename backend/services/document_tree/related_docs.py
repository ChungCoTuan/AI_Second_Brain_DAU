"""Document Tree / Cây Văn Bản — DAU Second Brain (SVC-06, WF-06, EPIC-6).

Tìm văn bản liên quan theo 2 cơ chế:
  1. Quan hệ tường minh (rule-based): đọc từ document_relations.jsonl
     → CAN_CU, THAY_THE, SUA_DOI, BAI_BO
  2. Quan hệ ngữ nghĩa (embedding): tái dùng FAISS index của SVC-05
     → LIEN_QUAN_NGU_NGHIA (cosine similarity)

Không xây model mới — tái sử dụng hoàn toàn hạ tầng đã có (EPIC-5).
Chi phí triển khai: thấp.

Cách dùng:
  from services.document_tree.related_docs import DocumentTree
  tree = DocumentTree()
  related = tree.find_related("BGD_TT_012024_D1", doc_content="...", doc_id="BGD_TT_012024")
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

logger = logging.getLogger(__name__)

DEFAULT_INDEX_PATH = "data/vector_db/faiss_index"
DEFAULT_RELATIONS_PATH = "data/processed/document_relations.jsonl"
SIMILARITY_THRESHOLD = 0.65   # Ngưỡng tối thiểu cho LIEN_QUAN_NGU_NGHIA
TOP_K_SEMANTIC = 5


class DocumentTree:
    """
    Tìm văn bản liên quan cho Cây Văn Bản (WF-06).
    Tái sử dụng FAISS index của SVC-05 — không cần model mới.
    """

    def __init__(
        self,
        index_path: str = DEFAULT_INDEX_PATH,
        relations_path: str = DEFAULT_RELATIONS_PATH,
        device: str = "cpu",
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        top_k: int = TOP_K_SEMANTIC,
    ):
        self.index_path = index_path
        self.relations_path = relations_path
        self.device = device
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

        self._explicit_relations: Optional[dict] = None  # Cache rule-based relations
        self._vector_store = None  # Lazy load

    # ── Rule-based Relations ───────────────────────────────────────────────

    def _load_explicit_relations(self) -> dict:
        """
        Load quan hệ tường minh từ document_relations.jsonl.
        Cache sau lần đầu load.
        """
        if self._explicit_relations is not None:
            return self._explicit_relations

        relations: dict = {}  # doc_id → list[relation]

        if not Path(self.relations_path).exists():
            logger.warning(f"Không tìm thấy: {self.relations_path}")
            self._explicit_relations = {}
            return {}

        with open(self.relations_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rel = json.loads(line)
                doc_a = rel.get("document_id_a", "")
                if doc_a not in relations:
                    relations[doc_a] = []
                relations[doc_a].append(rel)

        self._explicit_relations = relations
        total = sum(len(v) for v in relations.values())
        logger.info(f"📊 Đã load {total} quan hệ tường minh cho {len(relations)} văn bản.")
        return relations

    def get_explicit_relations(self, doc_id: str) -> list[dict]:
        """
        Lấy tất cả quan hệ tường minh của 1 văn bản.

        Returns:
            list[dict]: mỗi dict có loai_quan_he, document_id_b, mo_ta
        """
        relations_map = self._load_explicit_relations()
        raw = relations_map.get(doc_id, [])

        result = []
        for rel in raw:
            result.append({
                "doc_id_related": rel.get("document_id_b", ""),
                "loai_quan_he": rel.get("loai_quan_he", ""),
                "mo_ta": rel.get("mo_ta", ""),
                "diem_tuong_dong": None,
                "nguon": "rule_based",
            })

        return result

    # ── Semantic Relations ─────────────────────────────────────────────────

    def _get_vector_store(self):
        """Lazy load FAISS vector store (tái sử dụng từ rag_chain.py)."""
        if self._vector_store is None:
            try:
                from services.retrieval.rag_chain import _get_vector_store
                self._vector_store = _get_vector_store(
                    index_path=self.index_path,
                    device=self.device,
                )
            except FileNotFoundError:
                logger.warning(
                    "FAISS index chưa có. Chạy: python -m services.retrieval.build_index --include_pending"
                )
                self._vector_store = None
        return self._vector_store

    def get_semantic_relations(
        self,
        doc_content: str,
        doc_id: str,
    ) -> list[dict]:
        """
        Tìm văn bản liên quan ngữ nghĩa bằng FAISS similarity search.
        Tái sử dụng hoàn toàn vector store của SVC-05.

        Args:
            doc_content: Nội dung tóm tắt/chunk đại diện của văn bản hiện tại
            doc_id: doc_id của văn bản hiện tại (để loại ra khỏi kết quả)

        Returns:
            list[dict]: văn bản liên quan với diem_tuong_dong
        """
        vs = self._get_vector_store()
        if vs is None:
            return []

        try:
            # Similarity search với score (L2 distance)
            results = vs.similarity_search_with_score(
                query=doc_content[:512],  # Giới hạn input
                k=self.top_k + 5,  # Lấy thêm để có buffer lọc
            )
        except Exception as e:
            logger.error(f"FAISS search error: {e}")
            return []

        related = []
        seen_doc_ids = {doc_id}  # Loại văn bản hiện tại

        for doc, l2_distance in results:
            related_doc_id = doc.metadata.get("doc_id", "")

            if related_doc_id in seen_doc_ids:
                continue

            # Chuyển L2 distance sang cosine similarity (approximate)
            similarity = 1.0 / (1.0 + l2_distance)

            if similarity < self.similarity_threshold:
                continue

            seen_doc_ids.add(related_doc_id)
            related.append({
                "doc_id_related": related_doc_id,
                "loai_quan_he": "LIEN_QUAN_NGU_NGHIA",
                "mo_ta": f"Liên quan ngữ nghĩa (similarity={similarity:.3f})",
                "diem_tuong_dong": round(similarity, 4),
                "ten_van_ban": doc.metadata.get("ten_van_ban", ""),
                "chu_de": doc.metadata.get("chu_de", ""),
                "nguon": "semantic_faiss",
            })

            if len(related) >= self.top_k:
                break

        return related

    # ── Main: Find All Related ─────────────────────────────────────────────

    def find_related(
        self,
        doc_id: str,
        doc_content: str = "",
        include_semantic: bool = True,
    ) -> dict:
        """
        Tìm toàn bộ văn bản liên quan theo WF-06:
          - Quan hệ tường minh (rule-based) từ document_relations.jsonl
          - Quan hệ ngữ nghĩa (FAISS semantic search) nếu include_semantic=True

        Args:
            doc_id: ID văn bản hiện tại
            doc_content: Nội dung để tìm ngữ nghĩa (cần thiết cho semantic search)
            include_semantic: Có tìm quan hệ ngữ nghĩa không

        Returns:
            dict với explicit_relations, semantic_relations, all_relations
        """
        # 1. Quan hệ tường minh
        explicit = self.get_explicit_relations(doc_id)

        # 2. Quan hệ ngữ nghĩa
        semantic = []
        if include_semantic and doc_content:
            semantic = self.get_semantic_relations(
                doc_content=doc_content,
                doc_id=doc_id,
            )

        # 3. Phân loại output theo WF-06 (tách rõ 2 loại)
        return {
            "doc_id": doc_id,
            "explicit_relations": explicit,      # CAN_CU, THAY_THE, SUA_DOI, BAI_BO
            "semantic_relations": semantic,       # LIEN_QUAN_NGU_NGHIA
            "all_relations": explicit + semantic,
            "total": len(explicit) + len(semantic),
            "ghi_chu": (
                "Quan hệ tường minh: trích xuất từ regex/NER. "
                "Quan hệ ngữ nghĩa: tính từ FAISS embedding similarity."
            ),
        }


# ─── CLI Test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json as _json
    from pathlib import Path as _Path

    print("🧪 Test Document Tree — Cây Văn Bản...")

    tree = DocumentTree()

    # Lấy doc đầu tiên từ documents.jsonl để test
    docs_path = _Path("data/processed/documents.jsonl")
    chunks_path = _Path("data/processed/chunks.jsonl")

    if not docs_path.exists():
        print(f"❌ Không tìm thấy {docs_path}")
        sys.exit(1)

    with open(docs_path, "r", encoding="utf-8") as f:
        first_doc = _json.loads(f.readline().strip())

    doc_id = first_doc["doc_id"]
    ten_van_ban = first_doc.get("ten_van_ban", "")

    # Lấy content từ chunk đầu tiên của doc này
    doc_content = ""
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            chunk = _json.loads(line.strip())
            if chunk.get("doc_id") == doc_id:
                doc_content = chunk.get("content", "")[:512]
                break

    print(f"\n📄 Văn bản: {ten_van_ban}")
    print(f"   ID: {doc_id}")

    result = tree.find_related(
        doc_id=doc_id,
        doc_content=doc_content,
        include_semantic=True,
    )

    print(f"\n🔗 Quan hệ tường minh ({len(result['explicit_relations'])} kết quả):")
    for rel in result["explicit_relations"][:5]:
        print(f"   [{rel['loai_quan_he']}] → {rel['doc_id_related']}: {rel['mo_ta'][:60]}")

    print(f"\n🧠 Quan hệ ngữ nghĩa ({len(result['semantic_relations'])} kết quả):")
    if result["semantic_relations"]:
        for rel in result["semantic_relations"][:5]:
            print(
                f"   [LIEN_QUAN] → {rel['doc_id_related']} "
                f"(score={rel['diem_tuong_dong']:.3f}): {rel.get('ten_van_ban', '')[:50]}"
            )
    else:
        print("   (Chưa có FAISS index. Chạy build_index.py trước.)")
