"""База знаний с RAG и поиском FAQ."""

import json
import logging
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """База знаний с векторным поиском."""
    
    def __init__(self, knowledge_base_path: Path):
        self.knowledge_base_path = knowledge_base_path
        self._data = None
        self._model = None
        self._index = None
        self._faq_texts = []
        self._objections = []
        
        self._load_data()
        self._build_index()
    
    def _load_data(self):
        """Загрузка данных из JSON."""
        try:
            with open(self.knowledge_base_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            
            # Извлекаем FAQ
            if "faq" in self._data:
                self._faq_texts = [
                    f"{item['question']} {item['answer']}"
                    for item in self._data["faq"]
                ]
            
            # Извлекаем возражения
            if "objections" in self._data:
                self._objections = self._data["objections"]
            
            logger.info(f"Loaded knowledge base: {len(self._faq_texts)} FAQ items")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            self._data = {"faq": [], "objections": [], "products": {}}
    
    def _build_index(self):
        """Построение векторного индекса для поиска."""
        try:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            
            if self._faq_texts:
                # Кодируем тексты
                embeddings = self._model.encode(self._faq_texts)
                
                # Создаем FAISS индекс
                dimension = embeddings.shape[1]
                self._index = faiss.IndexFlatL2(dimension)
                self._index.add(np.array(embeddings).astype("float32"))
                
                logger.info(f"Built FAISS index: {self._index.ntotal} vectors")
            else:
                logger.warning("No FAQ texts to index")
                
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
    
    def search(self, query: str, top_k: int = 3) -> str:
        """
        Поиск по базе знаний.
        
        Args:
            query: Запрос для поиска
            top_k: Количество результатов
            
        Returns:
            Строка с найденным контекстом
        """
        if not self._index or not self._faq_texts:
            return ""
        
        try:
            # Кодируем запрос
            query_embedding = self._model.encode([query])
            
            # Ищем ближайших соседей
            distances, indices = self._index.search(
                np.array(query_embedding).astype("float32"),
                min(top_k, len(self._faq_texts))
            )
            
            # Формируем контекст
            context_parts = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self._data.get("faq", [])):
                    faq_item = self._data["faq"][idx]
                    context_parts.append(
                        f"Вопрос: {faq_item['question']}\n"
                        f"Ответ: {faq_item['answer']}"
                    )
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return ""
    
    def find_objection_response(self, client_text: str) -> Optional[str]:
        """
        Поиск ответа на возражение.
        
        Args:
            client_text: Текст клиента
            
        Returns:
            Ответ на возражение или None
        """
        client_lower = client_text.lower()
        
        for objection in self._objections:
            objection_text = objection.get("objection", "").lower()
            
            # Простое ключевое слово
            if any(word in client_lower for word in objection_text.split()):
                return objection.get("response")
        
        return None
    
    def get_company_info(self) -> dict:
        """Получение информации о компании."""
        return self._data.get("company", {})
    
    def get_products(self) -> dict:
        """Получение списка продуктов."""
        return self._data.get("products", {})
    
    def get_delivery_terms(self) -> dict:
        """Получение условий поставки."""
        return self._data.get("delivery_terms", {})
    
    def get_faq_by_category(self, category: str) -> list:
        """Получение FAQ по категории."""
        # Можно расширить для категоризации
        return self._data.get("faq", [])
    
    def add_faq_item(self, question: str, answer: str):
        """Добавление нового FAQ."""
        if "faq" not in self._data:
            self._data["faq"] = []
        
        self._data["faq"].append({
            "question": question,
            "answer": answer
        })
        
        # Пересоздаем индекс
        self._faq_texts.append(f"{question} {answer}")
        self._build_index()
        
        # Сохраняем
        self._save()
        
        logger.info(f"Added new FAQ: {question}")
    
    def add_objection(self, objection: str, response: str):
        """Добавление нового возражения."""
        if "objections" not in self._data:
            self._data["objections"] = []
        
        self._data["objections"].append({
            "objection": objection,
            "response": response
        })
        
        self._save()
        
        logger.info(f"Added new objection: {objection}")
    
    def _save(self):
        """Сохранение базы знаний."""
        try:
            with open(self.knowledge_base_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            
            logger.info("Knowledge base saved")
            
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")
    
    def update_from_transcript(self, transcript_text: str, llm_client=None):
        """
        Обновление базы знаний из транскрипта.
        
        Args:
            transcript_text: Текст транскрипта
            llm_client: Клиент LLM для извлечения информации
        """
        # Здесь можно добавить логику извлечения FAQ из транскриптов
        # Например, с помощью LLM
        pass


# Глобальный экземпляр
_knowledge_base: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    """Получить глобальный экземпляр базы знаний."""
    global _knowledge_base
    if _knowledge_base is None:
        from .config import KNOWLEDGE_BASE_PATH
        _knowledge_base = KnowledgeBase(KNOWLEDGE_BASE_PATH)
    return _knowledge_base
