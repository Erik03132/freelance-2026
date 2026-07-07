"""
LLM2Vec Embeddings — замена BGE для RAG.

Использует LLM для генерации эмбеддингов без дообучения.
Преимущество: работает в узких доменах без датасетов.
"""
import torch
from llm2vec import LLM2Vec
from typing import List, Union
import numpy as np


class LLM2VecEmbedder:
    """Эмбеддер на базе LLM2Vec."""
    
    def __init__(
        self,
        model_name: str = "McGill-NLP/LLM2Vec-Sheared-Llama-2.7B-262k-mntp-supervised",
        device: str = "cpu",
        max_length: int = 512
    ):
        """
        Инициализация LLM2Vec.
        
        Args:
            model_name: модель для эмбеддингов
            device: cpu или cuda
            max_length: максимальная длина текста
        """
        self.device = device
        self.max_length = max_length
        
        print(f"🔄 Загрузка LLM2Vec модели: {model_name}")
        self.model = LLM2Vec.from_pretrained(
            model_name,
            device_map=device,
            torch_dtype=torch.float32 if device == "cpu" else torch.float16,
        )
        print(f"✅ LLM2Vec загружен на {device}")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 8,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Генерация эмбеддингов.
        
        Args:
            texts: текст или список текстов
            batch_size: размер батча
            normalize: нормализовать векторы
            
        Returns:
            numpy array эмбеддингов [n_texts, embedding_dim]
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            with torch.no_grad():
                batch_embeddings = self.model.encode(
                    batch,
                    max_length=self.max_length,
                    normalize=normalize
                )
            
            if isinstance(batch_embeddings, torch.Tensor):
                batch_embeddings = batch_embeddings.cpu().numpy()
            
            embeddings.append(batch_embeddings)
        
        return np.vstack(embeddings)
    
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
_embedder: LLM2VecEmbedder | None = None


def get_embedder(device: str = "cpu") -> LLM2VecEmbedder:
    """Получить глобальный эмбеддер."""
    global _embedder
    if _embedder is None:
        _embedder = LLM2VecEmbedder(device=device)
    return _embedder


def encode(texts: Union[str, List[str]], device: str = "cpu") -> np.ndarray:
    """Быстрый доступ к encode."""
    return get_embedder(device).encode(texts)


def similarity(query: str, documents: List[str], device: str = "cpu") -> List[float]:
    """Быстрый доступ к similarity."""
    return get_embedder(device).similarity(query, documents)
