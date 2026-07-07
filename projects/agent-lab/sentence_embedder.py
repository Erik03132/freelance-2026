"""
Sentence-Transformers Embeddings — улучшение RAG без gated моделей.

Использует sentence-transformers с открытыми моделями:
- all-MiniLM-L6-v2: быстрая, 384 dim, хорошее качество
- all-mpnet-base-v2: медленнее, 768 dim, лучшее качество

Преимущество: работает без HuggingFace авторизации, высокое качество.
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np


class SentenceTransformerEmbedder:
    """Эмбеддер на базе sentence-transformers."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        """
        Инициализация SentenceTransformer.
        
        Args:
            model_name: модель (all-MiniLM-L6-v2 или all-mpnet-base-v2)
            device: cpu или cuda
        """
        self.device = device
        print(f"🔄 Загрузка модели: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        print(f"✅ Модель загружена на {device}")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Генерация эмбеддингов.
        
        Args:
            texts: текст или список текстов
            batch_size: размер батча
            normalize: нормализовать векторы
            show_progress: показать прогресс
            
        Returns:
            numpy array эмбеддингов [n_texts, embedding_dim]
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=show_progress
        )
        
        return embeddings
    
    def similarity(self, query: str, documents: List[str]) -> List[float]:
        """
        Косинусное сходство между запросом и документами.
        
        Args:
            query: запрос
            documents: список документов
            
        Returns:
            список скорингов
        """
        query_emb = self.encode([query])[0]
        docs_emb = self.encode(documents)
        
        similarities = np.dot(docs_emb, query_emb)
        return similarities.tolist()


# Глобальный экземпляр
_embedder: SentenceTransformerEmbedder | None = None


def get_embedder(
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu"
) -> SentenceTransformerEmbedder:
    """Получить глобальный эмбеддер."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformerEmbedder(model_name, device)
    return _embedder


def encode(
    texts: Union[str, List[str]],
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu"
) -> np.ndarray:
    """Быстрый доступ к encode."""
    return get_embedder(model_name, device).encode(texts)


def similarity(
    query: str,
    documents: List[str],
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu"
) -> List[float]:
    """Быстрый доступ к similarity."""
    return get_embedder(model_name, device).similarity(query, documents)
