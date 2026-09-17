from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Float, Date, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ten_van_ban: Mapped[str] = mapped_column(Text, nullable=False)
    so_hieu: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    loai_van_ban: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    chu_de: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    pham_vi_ap_dung: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nguon_du_lieu: Mapped[Optional[str]] = mapped_column(String(100), default="chinhphu.vn")
    ngay_ban_hanh: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    co_quan_ban_hanh: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    file_goc_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    trang_thai_hieu_luc: Mapped[str] = mapped_column(String(50), default="con_hieu_luc")
    trang_thai_xuat_ban: Mapped[str] = mapped_column(String(50), default="pending_review", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    summaries: Mapped[List["Summary"]] = relationship("Summary", back_populates="document", cascade="all, delete-orphan")
    review_items: Mapped[List["ReviewItem"]] = relationship("ReviewItem", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(100), ForeignKey("documents.id"), index=True, nullable=False)
    dieu_khoan: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    noi_dung: Mapped[str] = mapped_column(Text, nullable=False)
    so_trang: Mapped[int] = mapped_column(Integer, default=1)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="chunk")


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(100), ForeignKey("documents.id"), index=True, nullable=False)
    noi_dung_tom_tat: Mapped[str] = mapped_column(Text, nullable=False)
    phien_ban_model: Mapped[str] = mapped_column(String(100), default="rule-based-nli-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="summaries")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="summary", cascade="all, delete-orphan")


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    summary_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("summaries.id"), index=True, nullable=True)
    chunk_id: Mapped[str] = mapped_column(String(100), ForeignKey("document_chunks.id"), index=True, nullable=False)
    cau_tom_tat: Mapped[str] = mapped_column(Text, nullable=False)
    diem_faithfulness: Mapped[float] = mapped_column(Float, default=1.0)
    nhan_nli: Mapped[str] = mapped_column(String(50), default="entailment", index=True)

    summary: Mapped[Optional["Summary"]] = relationship("Summary", back_populates="citations")
    chunk: Mapped["DocumentChunk"] = relationship("DocumentChunk", back_populates="citations")
    review_items: Mapped[List["ReviewItem"]] = relationship("ReviewItem", back_populates="citation")


class ReviewItem(Base):
    __tablename__ = "review_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    citation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("citations.id"), index=True, nullable=True)
    document_id: Mapped[str] = mapped_column(String(100), ForeignKey("documents.id"), index=True, nullable=False)
    nhan_nli: Mapped[str] = mapped_column(String(50), index=True, default="contradiction")
    do_uu_tien: Mapped[str] = mapped_column(String(50), default="high", index=True)
    trang_thai: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="review_items")
    citation: Mapped[Optional["Citation"]] = relationship("Citation", back_populates="review_items")
    logs: Mapped[List["ReviewLog"]] = relationship("ReviewLog", back_populates="review_item", cascade="all, delete-orphan")


class ReviewLog(Base):
    __tablename__ = "review_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("review_items.id"), index=True, nullable=False)
    cau_ai_sinh: Mapped[str] = mapped_column(Text, nullable=False)
    cau_sau_sua: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_id: Mapped[str] = mapped_column(String(100), default="can_bo_dao_tao")
    hanh_dong: Mapped[str] = mapped_column(String(50), nullable=False)
    diem_nli_sau_sua: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    review_item: Mapped["ReviewItem"] = relationship("ReviewItem", back_populates="logs")


class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    loai_bao_cao: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    chu_de_ap_dung: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    danh_sach_de_muc: Mapped[dict] = mapped_column(JSON, nullable=False)


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cau_hoi: Mapped[str] = mapped_column(Text, nullable=False)
    cau_tra_loi: Mapped[str] = mapped_column(Text, nullable=False)
    danh_sach_citation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    diem_faithfulness: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class DocumentRelation(Base):
    __tablename__ = "document_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id_a: Mapped[str] = mapped_column(String(100), ForeignKey("documents.id"), index=True, nullable=False)
    document_id_b: Mapped[str] = mapped_column(String(100), ForeignKey("documents.id"), index=True, nullable=False)
    loai_quan_he: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    diem_tuong_dong: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
