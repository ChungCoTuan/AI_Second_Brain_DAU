# NLP Pipeline Interface
# Đồ án quy định sử dụng các mô hình mã nguồn mở (Local NLP Models) như:
# - BARTpho / ViT5 cho tóm tắt và bóc tách
# - TextRank / SVM cho phân loại (classification)
# - NLI (Natural Language Inference) cho 3 nhãn (entailment/contradiction/neutral)

import re
import os
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class LegalInformationExtractor:
    def __init__(self, use_ai=False):
        self.use_ai = use_ai
        self.pipeline = None
        if self.use_ai:
            try:
                from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
                import torch
                print("Dang tai mo hinh AI QA...")
                # Khởi tạo mô hình QA đa ngữ trực tiếp
                self.model_name = "timpal0l/mdeberta-v3-base-squad2"
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.qa_model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
                self.torch = torch
                
                print("Dang tai mo hinh Summarization (BARTpho/ViT5)...")
                self.summarizer = pipeline("summarization", model="VietAI/vit5-base-vietnews-summarization", max_length=150)
                
                print("Dang tai mo hinh NLI (3 nhan)...")
                self.nli_model = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
            except Exception as e:
                print(f"Canh bao: Khong the tai mo hinh AI. Chuyen sang Heuristic. Loi: {e}")
                self.use_ai = False

    def _ask_qa(self, question, context):
        inputs = self.tokenizer(question, context, return_tensors="pt", truncation=True, max_length=512)
        with self.torch.no_grad():
            outputs = self.qa_model(**inputs)
        
        start_idx = self.torch.argmax(outputs.start_logits)
        end_idx = self.torch.argmax(outputs.end_logits)
        
        start_prob = self.torch.max(self.torch.softmax(outputs.start_logits, dim=-1))
        end_prob = self.torch.max(self.torch.softmax(outputs.end_logits, dim=-1))
        score = float(start_prob * end_prob)
        
        if start_idx > end_idx or start_idx == 0: # 0 is CLS token meaning no answer
            return {"answer": "", "score": 0.0}
            
        answer_tokens = inputs.input_ids[0][start_idx:end_idx+1]
        answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()
        return {"answer": answer, "score": score}

    def extract_obligation(self, text_chunk: str) -> Dict[str, str]:
        """
        Bóc tách Nghĩa vụ (Chủ thể, Hành động, Hạn chót) từ một đoạn văn bản.
        """
        # --- LUỒNG AI ĐỌC HIỂU (QA) ---
        if self.use_ai and hasattr(self, 'qa_model'):
            try:
                # Ngưỡng tự tin (Score threshold) để ngăn chặn "vơ đại"
                confidence_threshold = 0.05
                safe_context = text_chunk[:1000]
                
                # 1. Hỏi Chủ thể
                ans_sub = self._ask_qa("Ai là người thực hiện hoặc chịu trách nhiệm?", safe_context)
                subject = ans_sub['answer'] if ans_sub['score'] > confidence_threshold else "Không có"
                
                # 2. Hỏi Hành động
                ans_act = self._ask_qa("Phải làm nhiệm vụ gì?", safe_context)
                action = ans_act['answer'] if ans_act['score'] > confidence_threshold else "Không có"
                
                # 3. Hỏi Hạn chót
                ans_dead = self._ask_qa("Hạn chót hoặc thời gian thực hiện là khi nào?", safe_context)
                deadline = ans_dead['answer'] if ans_dead['score'] > confidence_threshold else "Không có"
                
                return {
                    "chu_the": subject.capitalize(),
                    "han_chot": deadline,
                    "noi_dung": action.capitalize()
                }
            except Exception as e:
                print(f"Lỗi suy luận AI: {e}. Fallback về Heuristic.")
                
        # --- LUỒNG HEURISTIC (DỰ PHÒNG) ---
        # 1. Trích xuất Hạn chót (Deadline)
        deadline = "Không quy định cụ thể"
        date_pattern = r"(?:trước ngày|ngày|từ ngày|đến ngày|hạn)\s+(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)"
        match = re.search(date_pattern, text_chunk.lower())
        if match:
            deadline = f"Theo mốc thời gian: {match.group(1)}"
        else:
            year_match = re.search(r"(?:năm học|năm)\s+(20\d{2})", text_chunk.lower())
            if year_match:
                deadline = f"Trong năm {year_match.group(1)}"

        # 2. Trích xuất Chủ thể (Subject)
        subject = "Các đơn vị, cá nhân liên quan"
        # Danh sách từ khoá các phòng ban thường gặp trong trường Đại học
        subjects_list = [
            "Hiệu trưởng", "Phòng Quản lý Đào tạo", "Phòng Đào tạo", "Phòng Tài chính",
            "Phòng Khảo thí", "Khoa", "Thí sinh", "Sinh viên", "Tiểu ban",
            "Ban Thư ký", "Hội đồng tuyển sinh", "Giảng viên", "Bộ Giáo dục"
        ]
        for s in subjects_list:
            if s.lower() in text_chunk.lower():
                subject = s
                break
                
        # 3. Trích xuất Hành động (Action)
        # Lấy câu chứa chủ thể hoặc một câu ý nghĩa
        action = "Thực hiện theo quy định của văn bản"
        lines = text_chunk.split('\n')
        for line in lines:
            if len(line) > 30 and ("phải" in line.lower() or "có trách nhiệm" in line.lower() or "thực hiện" in line.lower()):
                action = line.strip()
                break
        if action == "Thực hiện theo quy định của văn bản" and len(lines) > 1 and len(lines[1]) > 20:
             action = lines[1].strip()
             
        # Giới hạn độ dài hành động
        if len(action) > 150:
            action = action[:147] + "..."
            
        return {
            "chu_the": subject,
            "han_chot": deadline,
            "noi_dung": action
        }

    def extract_threshold(self, text_chunk: str) -> Dict[str, str]:
        """
        Bóc tách Con số chốt (Thresholds / Định mức).
        """
        # --- LUỒNG AI ĐỌC HIỂU (QA) ---
        if self.use_ai and hasattr(self, 'qa_model'):
            try:
                safe_context = text_chunk[:1000]
                ans_thresh = self._ask_qa("Con số, số lượng hoặc tỷ lệ là bao nhiêu?", safe_context)
                if ans_thresh['score'] > 0.05 and ans_thresh['answer']:
                    return {
                        "gia_tri": f"Ngưỡng: {ans_thresh['answer']}",
                        "y_nghia": "Được trích xuất bởi AI"
                    }
            except Exception as e:
                print(f"Lỗi suy luận AI: {e}. Fallback về Heuristic.")
                
        # --- LUỒNG HEURISTIC (DỰ PHÒNG) ---
        threshold = "Không có con số chốt"
        meaning = "Định mức chung"
        
        # Tìm các con số kèm đơn vị hoặc phần trăm
        num_pattern = r"(\d+(?:\.\d+)?)\s*(lần|ngày|tháng|năm|sinh viên|giảng viên|%|phần trăm|chỉ tiêu|triệu|tỷ)"
        match = re.search(num_pattern, text_chunk.lower())
        if match:
            threshold = f"Ngưỡng: {match.group(1)} {match.group(2)}"
            
            # Cố gắng tìm ý nghĩa của con số
            if "%" in match.group(2) or "phần trăm" in match.group(2):
                meaning = "Tỷ lệ phần trăm"
            elif match.group(2) in ["ngày", "tháng", "năm"]:
                meaning = "Thời hạn / Chu kỳ"
            elif match.group(2) in ["sinh viên", "chỉ tiêu"]:
                meaning = "Định mức quy mô"
            elif match.group(2) in ["triệu", "tỷ"]:
                meaning = "Định mức tài chính"
            
        return {
            "gia_tri": threshold,
            "y_nghia": meaning
        }

    def summarize_text(self, text: str) -> str:
        """
        Tóm tắt văn bản dùng mô hình BARTpho / ViT5
        """
        if self.use_ai and hasattr(self, 'summarizer'):
            try:
                # Cắt bớt input nếu quá dài để tránh lỗi OOM
                input_text = text[:1024]
                summary = self.summarizer(input_text, max_length=100, min_length=15, do_sample=False)
                return summary[0]['summary_text']
            except Exception as e:
                print(f"Lỗi tóm tắt AI: {e}")
                
        # Fallback Heuristic: Lấy câu đầu tiên
        sentences = [s.strip() for s in text.replace(';', '.').split('.') if len(s.strip()) > 10]
        if sentences:
            return sentences[0] + "."
        return text[:100] + "..."

    def verify_nli(self, premise: str, hypothesis: str) -> str:
        """
        Kiểm tra độ trung thực NLI (Entailment, Contradiction, Neutral).
        """
        if self.use_ai and hasattr(self, 'nli_model'):
            try:
                labels = ["entailment", "contradiction", "neutral"]
                result = self.nli_model(f"Context: {premise} Hypothesis: {hypothesis}", labels, multi_label=False)
                best_label = result['labels'][0]
                return best_label
            except Exception as e:
                print(f"Lỗi NLI: {e}")
                
        # Fallback Heuristic
        return "neutral"

    def extract_document_relations(self, text: str, source_doc: str) -> list[Dict[str, str]]:
        """
        Dùng Regex để tìm các quan hệ: Căn cứ, Thay thế, Bãi bỏ.
        """
        relations = []
        text_lower = text.lower()
        
        # Mẫu regex để tìm "thay thế", "bãi bỏ", "căn cứ" + "Thông tư/Nghị định/Quyết định/Luật + Số hiệu"
        # Bắt Số hiệu VD: 08/2021/TT-BGDĐT, 123/QĐ-UBND, Luật Giáo dục đại học...
        pattern = r"(thay thế|bãi bỏ|căn cứ)\s+((?:toàn bộ\s+)?(?:thông tư|nghị định|quyết định|luật|công văn)[^,\.\n;\(]+)"
        
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            rel_type = match.group(1).strip()
            target_doc = match.group(2).strip().upper() # VD: THÔNG TƯ 08/2021/TT-BGDĐT
            
            relations.append({
                "source_doc": source_doc,
                "target_doc": target_doc,
                "relation_type": rel_type
            })
            
        return relations

# Khởi tạo instance toàn cục (Bật use_ai=True để sử dụng mô hình QA)
extractor = LegalInformationExtractor(use_ai=True)

def classify_text(text: str) -> str:
    """
    Phân loại chủ đề văn bản dựa trên thuật toán Cân điểm Từ khóa (Keyword Scoring).
    Sử dụng thay cho TextRank/SVM khi chưa có dữ liệu huấn luyện.
    """
    text_lower = text.lower()
    
    # Định nghĩa các chủ đề và trọng số từ khóa
    topics = {
        "Tuyển sinh": ["tuyển sinh", "thí sinh", "xét tuyển", "trúng tuyển", "chỉ tiêu", "nhập học", "điểm chuẩn"],
        "Đào tạo": ["chương trình đào tạo", "tín chỉ", "sinh viên", "giảng viên", "học phần", "điểm thi", "chuẩn đầu ra", "tốt nghiệp"],
        "Tài chính": ["học phí", "ngân sách", "chi tiêu", "tài chính", "dự toán", "quyết toán", "lương", "thu nhập"],
        "Đảm bảo chất lượng": ["kiểm định", "đánh giá", "chất lượng", "khảo thí", "đo lường", "obe", "cbe", "chuẩn quốc gia"],
        "Hợp tác quốc tế": ["quốc tế", "nước ngoài", "liên kết", "trao đổi", "du học", "đối tác", "mou", "moa"],
        "Nghiên cứu Khoa học": ["nghiên cứu", "khoa học", "đề tài", "bài báo", "hội thảo", "tạp chí", "isi", "scopus"]
    }
    
    scores = {topic: 0 for topic in topics.keys()}
    
    # Đếm tần suất xuất hiện để tính điểm
    for topic, keywords in topics.items():
        for kw in keywords:
            # Cộng điểm dựa trên số lần xuất hiện của từ khóa
            scores[topic] += text_lower.count(kw)
            
    # Lấy chủ đề có điểm cao nhất
    max_score = 0
    best_topic = "Khác"
    
    for topic, score in scores.items():
        if score > max_score and score >= 3: # Cần ít nhất 3 điểm để được xếp loại
            max_score = score
            best_topic = topic
            
    return best_topic
def create_embedding(text: str) -> list[float]:
    """
    Interface tạo Vector nhúng cho văn bản.
    """
    # TODO: Tích hợp model tạo embedding tại đây (VD: PhoBERT, vncorenlp)
    return [0.0] * 768

def generate_rag_answer(query: str, context_chunks: list[str]) -> str:
    """
    Sử dụng Gemini API để sinh câu trả lời RAG dựa trên các đoạn ngữ cảnh.
    """
    if not GEMINI_API_KEY:
        return "Hệ thống chưa được cấu hình GEMINI_API_KEY trong file .env. Vui lòng thêm API Key để sử dụng tính năng Chatbot AI."
        
    context_text = "\n\n---\n\n".join(context_chunks)
    
    prompt = f"""Bạn là một Trợ lý AI pháp lý chuyên nghiệp của Hệ thống DAU Second Brain. 
Nguyên tắc hoạt động:
1. GIAO TIẾP THÔNG THƯỜNG: Nếu người dùng chào hỏi, hỏi thăm hoặc hỏi về khả năng của bạn (VD: "Bạn là ai?", "Bạn làm được gì?"), hãy trả lời tự nhiên, lịch sự và giới thiệu bạn là Trợ lý AI chuyên tra cứu Quy chế, Thông tư nội bộ của trường.
2. TRẢ LỜI NGHIỆP VỤ: Nếu người dùng hỏi về quy định, luật lệ, HÃY CHỈ DỰA VÀO phần TÀI LIỆU NGỮ CẢNH bên dưới để tổng hợp câu trả lời. 
3. CHỐNG ẢO GIÁC (HALLUCINATION): Nếu câu hỏi liên quan đến quy định/pháp luật nhưng TÀI LIỆU NGỮ CẢNH không chứa thông tin phù hợp, HÃY NÓI RÕ: "Dựa vào các văn bản hiện có trên hệ thống, tôi không tìm thấy thông tin để trả lời câu hỏi này." Tuyệt đối không dùng kiến thức bên ngoài để bịa ra luật.

TÀI LIỆU NGỮ CẢNH:
{context_text}

CÂU HỎI CỦA NGƯỜI DÙNG: {query}
"""
    try:
        model = genai.GenerativeModel('gemini-3.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Xin lỗi, đã xảy ra lỗi khi gọi AI: {str(e)}"
