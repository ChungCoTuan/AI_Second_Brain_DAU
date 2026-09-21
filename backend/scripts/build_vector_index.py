import sys
import os

# Thêm thư mục gốc vào path để import
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal
from app.db.models import Obligation, Threshold, Document
from app.services.nlp_pipeline import create_embedding
from app.services.vector_db import vector_db

def build_index():
    print("Bắt đầu xây dựng Vector Index...")
    db = SessionLocal()
    
    # Xoá index cũ
    vector_db.clear()
    
    embeddings = []
    metadatas = []
    
    # 1. Đưa các Nghĩa vụ (Obligations) đã publish vào DB
    print("Đang xử lý Nghĩa vụ (Obligations)...")
    obligations = db.query(Obligation).filter(Obligation.status == "published").all()
    for obs in obligations:
        text_to_embed = f"Văn bản: {obs.vb}. Điều khoản: {obs.dieu}. Nội dung: {obs.noi_dung}"
        print(f"Embedding: {obs.vb} - {obs.dieu}")
        
        emb = create_embedding(text_to_embed)
        embeddings.append(emb)
        metadatas.append({
            "id": obs.id,
            "type": "nghiaVu",
            "vb": obs.vb,
            "dieu": obs.dieu,
            "noiDung": obs.noi_dung,
            "nguon": obs.nguon
        })
        
    # 2. Đưa các Con số chốt (Thresholds) đã publish vào DB
    print(f"Đang xử lý Con số chốt (Thresholds)...")
    thresholds = db.query(Threshold).filter(Threshold.status == "published").all()
    for th in thresholds:
        text_to_embed = f"Văn bản: {th.vb}. Điều khoản: {th.dieu}. Con số: {th.gia_tri}. Ý nghĩa: {th.y_nghia}"
        print(f"Embedding: {th.vb} - {th.dieu}")
        
        emb = create_embedding(text_to_embed)
        embeddings.append(emb)
        metadatas.append({
            "id": th.id,
            "type": "conSoChot",
            "vb": th.vb,
            "dieu": th.dieu,
            "noiDung": f"{th.gia_tri} - {th.y_nghia}",
            "nguon": th.nguon
        })
        
    # 3. Lưu vào FAISS
    if embeddings:
        print(f"Đang lưu {len(embeddings)} vectors vào FAISS...")
        vector_db.add_texts(embeddings, metadatas)
        print("Xong!")
    else:
        print("Không có dữ liệu nào đã được Publish để đưa vào Vector DB.")
        
    db.close()

if __name__ == "__main__":
    build_index()
