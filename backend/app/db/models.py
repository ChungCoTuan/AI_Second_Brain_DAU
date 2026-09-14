from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
# from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    source_folder = Column(String, nullable=False)
    chu_de = Column(String, nullable=True) # Phân loại chủ đề AI
    status = Column(String, default="draft") # draft, in_review, published
    
    # Relationships
    obligations = relationship("Obligation", back_populates="document", cascade="all, delete-orphan")
    thresholds = relationship("Threshold", back_populates="document", cascade="all, delete-orphan")

class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    vb = Column(String, nullable=False)
    dieu = Column(String)
    loai = Column(String)
    chu_the = Column(String)
    noi_dung = Column(Text)
    han_chot = Column(String)
    nguon = Column(Text)
    status = Column(String, default="draft") # draft, published
    tom_tat = Column(Text, nullable=True)
    nli_label = Column(String, nullable=True) # entailment, contradiction, neutral

    document = relationship("Document", back_populates="obligations")

class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    vb = Column(String, nullable=False)
    dieu = Column(String)
    gia_tri = Column(String)
    y_nghia = Column(Text)
    nguon = Column(Text)
    status = Column(String, default="draft") # draft, published
    tom_tat = Column(Text, nullable=True)
    nli_label = Column(String, nullable=True) # entailment, contradiction, neutral

    document = relationship("Document", back_populates="thresholds")

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    # Tạm dùng JSONB để lưu mảng [0.1, 0.2, ...] vì máy user chưa cài đặt pgvector extension
    embedding = Column(JSONB) 
    
    document = relationship("Document")

class DocumentRelation(Base):
    __tablename__ = "document_relations"

    id = Column(Integer, primary_key=True, index=True)
    source_doc = Column(String, nullable=False) # VD: TT 08/2021
    target_doc = Column(String, nullable=False) # VD: TT 17/2021
    relation_type = Column(String, nullable=False) # VD: "thay thế", "bãi bỏ", "căn cứ"
    status = Column(String, default="published")
