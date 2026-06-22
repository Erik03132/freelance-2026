from __future__ import annotations

"""
📚 RAG Memory — База знаний агента.

Это «память» агента. Сюда загружаются специализированные знания,
которые превращают универсального агента в конкретного специалиста.

Для Анжелы: товары, цены, доставка, уход за птицей.
Для Шерлока: конкуренты, рынок, SEO-метрики.
Для другого ребёнка: его собственная область.

Используем ChromaDB для лаборатории (простой, локальный).
В продакшне Анжелы — Neon/pgvector (облачный).
"""
import os
import json
from pathlib import Path

# ChromaDB — лёгкая локальная векторная БД
try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    print("⚠️ ChromaDB не установлен. RAG работает в режиме simple search.")

# Пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "knowledge"
CHROMA_DIR = BASE_DIR / ".chroma_db"


class RAGMemory:
    """
    База знаний агента.
    
    Загружает .md и .json файлы из папки knowledge/ и делает их
    доступными для поиска. Агент использует инструмент search_knowledge()
    чтобы находить нужную информацию.
    """

    def __init__(self, knowledge_dir: str | Path = DATA_DIR):
        self.knowledge_dir = Path(knowledge_dir)
        self.documents: list[dict] = []  # [{content, source}]
        self._collection = None
        
        # Загружаем документы
        self._load_documents()
        
        # Инициализируем векторный поиск (если ChromaDB доступен)
        if HAS_CHROMA and self.documents:
            self._init_vector_store()

    def _load_documents(self):
        """Загружает все .md и .json файлы из директории знаний."""
        if not self.knowledge_dir.exists():
            self.knowledge_dir.mkdir(parents=True)
            # Создаём пример
            example = self.knowledge_dir / "example.md"
            example.write_text(
                "# Пример базы знаний\n\n"
                "Поместите сюда файлы .md или .json с знаниями для агента.\n"
                "Каждый файл будет разбит на фрагменты и проиндексирован.\n",
                encoding="utf-8",
            )
            print(f"📁 Создана папка {self.knowledge_dir}/ — положите туда файлы знаний")
            return

        for file_path in sorted(self.knowledge_dir.iterdir()):
            if file_path.suffix == ".md":
                self._load_markdown(file_path)
            elif file_path.suffix == ".json":
                self._load_json(file_path)

        if self.documents:
            print(f"📚 RAG: загружено {len(self.documents)} фрагментов знаний")

    def _load_markdown(self, path: Path):
        """Загружает .md файл, разбивая на секции по заголовкам."""
        text = path.read_text(encoding="utf-8")
        # Разбиваем по заголовкам ## (каждая секция = отдельный документ)
        sections = []
        current = ""
        for line in text.split("\n"):
            if line.startswith("## ") and current.strip():
                sections.append(current.strip())
                current = line + "\n"
            else:
                current += line + "\n"
        if current.strip():
            sections.append(current.strip())

        for section in sections:
            if len(section) > 20:  # Пропускаем слишком короткие
                self.documents.append({
                    "content": section,
                    "source": path.name,
                })

    def _load_json(self, path: Path):
        """Загружает .json файл (массив объектов с полем content)."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    content = item.get("content", "")
                    if content and len(content) > 20:
                        self.documents.append({
                            "content": content,
                            "source": path.name,
                        })
        except Exception as e:
            print(f"⚠️ Ошибка чтения {path.name}: {e}")

    def _init_vector_store(self):
        """Создаём векторный индекс через ChromaDB."""
        try:
            os.makedirs(str(CHROMA_DIR), exist_ok=True)
            os.environ["CHROMA_CACHE_DIR"] = str(CHROMA_DIR / ".cache")
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            
            # Используем встроенные эмбеддинги (бесплатные, без API)
            ef = embedding_functions.DefaultEmbeddingFunction()
            
            self._collection = client.get_or_create_collection(
                name="knowledge",
                embedding_function=ef,
            )

            # Добавляем документы (если коллекция пуста)
            if self._collection.count() == 0:
                self._collection.add(
                    documents=[d["content"] for d in self.documents],
                    metadatas=[{"source": d["source"]} for d in self.documents],
                    ids=[f"doc_{i}" for i in range(len(self.documents))],
                )
                print(f"🔍 Векторный индекс создан: {len(self.documents)} документов")
            else:
                print(f"🔍 Векторный индекс загружен: {self._collection.count()} документов")
                
        except Exception as e:
            print(f"⚠️ ChromaDB init error: {e}")
            self._collection = None

    def search(self, query: str, limit: int = 3) -> list[str]:
        """
        Ищет релевантную информацию.
        
        Если ChromaDB доступен — семантический поиск.
        Иначе — простой текстовый поиск (fallback).
        """
        # Вариант 1: Семантический поиск (ChromaDB)
        if self._collection:
            try:
                results = self._collection.query(
                    query_texts=[query],
                    n_results=min(limit, self._collection.count()),
                )
                if results and results["documents"]:
                    return results["documents"][0]
            except Exception as e:
                print(f"⚠️ Vector search error: {e}")

        # Вариант 2: Простой текстовый поиск (fallback)
        return self._simple_search(query, limit)

    def _simple_search(self, query: str, limit: int) -> list[str]:
        """Простой поиск по вхождению слов (без ML)."""
        query_words = set(query.lower().split())
        scored = []
        for doc in self.documents:
            content_lower = doc["content"].lower()
            score = sum(1 for w in query_words if w in content_lower)
            if score > 0:
                scored.append((score, doc["content"]))
        scored.sort(reverse=True)
        return [text for _, text in scored[:limit]]

    def add(self, content: str, source: str = "learned"):
        """Добавляет новое знание (самообучение)."""
        self.documents.append({"content": content, "source": source})
        if self._collection:
            try:
                doc_id = f"doc_{len(self.documents)}"
                self._collection.add(
                    documents=[content],
                    metadatas=[{"source": source}],
                    ids=[doc_id],
                )
            except Exception:
                pass


# === Глобальный экземпляр RAG ===
_memory: RAGMemory | None = None


def get_memory(knowledge_dir: str | Path = DATA_DIR) -> RAGMemory:
    """Получить (или создать) экземпляр RAG Memory."""
    global _memory
    if _memory is None:
        _memory = RAGMemory(knowledge_dir)
    return _memory


def search(query: str, limit: int = 3) -> list[str]:
    """Быстрый доступ к поиску (для использования из tools.py)."""
    return get_memory().search(query, limit)
