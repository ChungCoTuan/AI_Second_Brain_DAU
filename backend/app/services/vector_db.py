import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple

class VectorDBManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.index_path = os.path.join(self.data_dir, "faiss_index.bin")
        self.meta_path = os.path.join(self.data_dir, "faiss_meta.json")
        
        self.dimension = 384 # Default for paraphrase-MiniLM-L3-v2
        self.index = None
        self.metadata = []
        
        self.load_index()

    def load_index(self):
        """Tải FAISS index và metadata từ đĩa (nếu có)."""
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"Loaded FAISS index with {self.index.ntotal} vectors.")
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Khởi tạo một index trống mới."""
        # IndexFlatL2 for L2 distance, or IndexFlatIP for Cosine similarity (if vectors are normalized)
        # SBERT usually works well with Cosine similarity, so we use Inner Product (IP).
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        print("Initialized new FAISS index.")

    def save_index(self):
        """Lưu FAISS index và metadata xuống đĩa."""
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_texts(self, embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Thêm danh sách các vector và siêu dữ liệu vào index."""
        if not embeddings or not metadatas:
            return
            
        if len(embeddings) != len(metadatas):
            raise ValueError("Số lượng embeddings và metadatas phải bằng nhau.")
            
        vectors = np.array(embeddings).astype('float32')
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        self.index.add(vectors)
        self.metadata.extend(metadatas)
        self.save_index()

    def clear(self):
        """Xoá toàn bộ index."""
        self._create_new_index()
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)

    def search(self, query_embedding: List[float], top_k: int = 3, threshold: float = 0.5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Tìm kiếm các đoạn văn bản gần nhất.
        Trả về danh sách (metadata, score)
        """
        if self.index.ntotal == 0:
            return []
            
        query_vector = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # D là ma trận điểm (Cosine similarity) vì đã dùng IndexFlatIP + Normalize
        # I là ma trận chỉ mục (index) trong mảng
        D, I = self.index.search(query_vector, top_k)
        
        results = []
        for i in range(len(I[0])):
            idx = I[0][i]
            score = D[0][i]
            if idx != -1 and score >= threshold:
                results.append((self.metadata[idx], float(score)))
                
        return results

# Singleton instance
vector_db = VectorDBManager(data_dir=os.path.join(os.path.dirname(__file__), "..", "..", "data"))
