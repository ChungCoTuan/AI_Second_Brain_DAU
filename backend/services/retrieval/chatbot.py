"""Chatbot với Memory — DAU Second Brain (WF-05).

Chatbot hỏi-đáp có lịch sử hội thoại, sử dụng FAISS index đã xây dựng.
Tích hợp ConversationBufferWindowMemory để nhớ context 5 lượt gần nhất.

Cách dùng:
  from services.retrieval.chatbot import DAUChatbot
  bot = DAUChatbot()
  print(bot.chat("Quy định học phí là gì?"))
  print(bot.chat("Văn bản đó ban hành năm nào?"))  # Nhớ context lượt trước
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

logger = logging.getLogger(__name__)

DEFAULT_INDEX_PATH = "data/vector_db/faiss_index"


class DAUChatbot:
    """
    Chatbot RAG có memory cho DAU Second Brain.

    Sử dụng LangChain ConversationBufferWindowMemory để lưu lịch sử hội thoại.
    Nếu có LLM, dùng ConversationalRetrievalChain.
    Nếu không có LLM, dùng extractive approach từ rag_chain.py.
    """

    def __init__(
        self,
        index_path: str = DEFAULT_INDEX_PATH,
        device: str = "cpu",
        memory_window: int = 5,
        llm=None,  # Optional: truyền LLM nếu có
    ):
        self.index_path = index_path
        self.device = device
        self.memory_window = memory_window
        self.llm = llm
        self._memory = None
        self._chain = None
        self._history: list[dict] = []  # Lịch sử đơn giản khi không dùng LangChain memory

    def _get_memory(self):
        """Lazy load LangChain memory."""
        if self._memory is None:
            from langchain.memory import ConversationBufferWindowMemory

            self._memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer",
                k=self.memory_window,
            )
        return self._memory

    def _get_chain(self):
        """Lazy load ConversationalRetrievalChain (chỉ khi có LLM)."""
        if self._chain is None and self.llm is not None:
            from langchain.chains import ConversationalRetrievalChain
            from langchain.prompts import PromptTemplate
            from services.retrieval.rag_chain import get_retriever

            CONDENSE_PROMPT = PromptTemplate.from_template(
                """Dựa trên lịch sử hội thoại và câu hỏi hiện tại, \
hãy tạo ra câu hỏi độc lập (không phụ thuộc lịch sử) để tra cứu văn bản pháp quy.

Lịch sử: {chat_history}
Câu hỏi hiện tại: {question}
Câu hỏi độc lập (tiếng Việt):"""
            )

            retriever = get_retriever(
                index_path=self.index_path, device=self.device
            )

            self._chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=self._get_memory(),
                condense_question_prompt=CONDENSE_PROMPT,
                return_source_documents=True,
                verbose=False,
            )
        return self._chain

    def chat(self, user_message: str) -> dict:
        """
        Gửi tin nhắn, nhận câu trả lời có trích dẫn và lịch sử.

        Args:
            user_message: Câu hỏi của người dùng

        Returns:
            dict với answer, citations, history_length
        """
        # ── Nếu có LLM: dùng ConversationalRetrievalChain ──────────────────
        if self.llm is not None:
            chain = self._get_chain()
            if chain is not None:
                try:
                    result = chain.invoke({"question": user_message})
                    answer = result.get("answer", "")
                    sources = result.get("source_documents", [])
                    citations = [
                        {
                            "chunk_id": doc.metadata.get("chunk_id"),
                            "ten_van_ban": doc.metadata.get("ten_van_ban"),
                            "dieu_khoan": doc.metadata.get("title"),
                            "so_trang": doc.metadata.get("so_trang"),
                        }
                        for doc in sources
                    ]
                    self._history.append({"role": "user", "content": user_message})
                    self._history.append({"role": "assistant", "content": answer})
                    return {
                        "answer": answer,
                        "citations": citations,
                        "history_length": len(self._history) // 2,
                    }
                except Exception as e:
                    logger.error(f"Chain error: {e}")

        # ── Fallback: extractive RAG với simple history ─────────────────────
        from services.retrieval.rag_chain import query_with_citation

        # Thêm context từ lịch sử vào câu hỏi (simple approach)
        enriched_question = user_message
        if self._history:
            last_exchange = self._history[-2:]
            ctx = " ".join(h["content"] for h in last_exchange)
            enriched_question = f"{user_message} (ngữ cảnh: {ctx[:200]})"

        result = query_with_citation(
            question=enriched_question,
            index_path=self.index_path,
            device=self.device,
            run_nli_check=False,  # Tắt NLI cho chatbot real-time
        )

        self._history.append({"role": "user", "content": user_message})
        if result["answer"]:
            self._history.append({"role": "assistant", "content": result["answer"]})

        return {
            "answer": result.get("answer") or result.get("message"),
            "citations": result.get("citations", []),
            "history_length": len(self._history) // 2,
            "nli_status": result.get("nli_status"),
        }

    def clear_history(self) -> None:
        """Xóa lịch sử hội thoại."""
        self._history = []
        if self._memory is not None:
            self._memory.clear()
        logger.info("🗑️ Đã xóa lịch sử hội thoại.")

    def get_history(self) -> list[dict]:
        """Trả về toàn bộ lịch sử hội thoại."""
        return self._history.copy()

    def format_history_for_display(self) -> str:
        """Format lịch sử hội thoại dạng text để hiển thị."""
        lines = []
        for turn in self._history:
            prefix = "👤 Bạn" if turn["role"] == "user" else "🤖 Trợ lý"
            lines.append(f"{prefix}: {turn['content']}")
        return "\n\n".join(lines)


# ─── CLI Interactive Mode ─────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 DAU Second Brain — Chatbot Tra Cứu Văn Bản Pháp Quy")
    print("=" * 60)
    print("Gõ 'exit' để thoát | 'clear' để xóa lịch sử | 'history' xem lịch sử\n")

    bot = DAUChatbot()

    while True:
        try:
            user_input = input("👤 Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Tạm biệt!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("👋 Tạm biệt!")
            break
        if user_input.lower() == "clear":
            bot.clear_history()
            print("🗑️ Đã xóa lịch sử.\n")
            continue
        if user_input.lower() == "history":
            print(bot.format_history_for_display() or "(Chưa có lịch sử)")
            print()
            continue

        result = bot.chat(user_input)
        print(f"\n🤖 Trợ lý: {result['answer']}")

        if result.get("citations"):
            print(f"\n📎 Nguồn trích dẫn:")
            for cit in result["citations"][:3]:
                ten_vb = cit.get("ten_van_ban", "N/A")
                dieu = cit.get("dieu_khoan", "")
                print(f"   - {ten_vb} — {dieu}")

        print(f"\n   [Lượt hội thoại: {result.get('history_length', 0)}]\n")
