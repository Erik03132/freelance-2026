"""
MarinaVectorDB — Облачная векторная база знаний (Neon + pgvector)
С auto-reconnect и валидацией соединений.
"""
import os
import time
import json
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Загружаем настройки
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(os.path.join(BASE_DIR, '..', 'freelance-agent', '.env'), override=True)

# Lazy import Gemini (избегаем конфликтов при старте)
_genai = None

def _get_genai():
    global _genai
    if _genai is None:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        _genai = genai
    return _genai


class MarinaVectorDB:
    def __init__(self):
        self.db_url = os.getenv("NEON_DATABASE_URL")
        self.enabled = self.db_url is not None
        self.connection_pool = None
        if self.enabled:
            self._init_db()

    def _init_db(self):
        try:
            self.connection_pool = pool.SimpleConnectionPool(1, 10, self.db_url)
            conn = self.connection_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS marina_knowledge (
                            id SERIAL PRIMARY KEY,
                            content TEXT,
                            metadata JSONB,
                            embedding vector(3072)
                        );
                    """)
                    conn.commit()
            finally:
                self.connection_pool.putconn(conn)
            print("✅ Marina VectorDB: пул инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации Neon DB: {e}")
            self.enabled = False

    def _get_valid_conn(self):
        """Получить валидное соединение с 3 попытками."""
        for attempt in range(3):
            try:
                conn = self.connection_pool.getconn()
                # Проверяем через лёгкий запрос
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return conn
            except Exception:
                try:
                    self.connection_pool.putconn(conn, close=True)
                except:
                    pass
                if attempt == 2:
                    # Пересоздаём пул
                    try:
                        self.connection_pool.closeall()
                    except:
                        pass
                    self.connection_pool = pool.SimpleConnectionPool(1, 10, self.db_url)
                    return self.connection_pool.getconn()
        return None

    def get_embedding(self, text: str):
        """Генерация вектора через Google Gemini Embedding."""
        genai = _get_genai()
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def add_knowledge(self, text: str, meta: dict):
        if not self.enabled:
            return

        # Механизм повторов при 429 (Rate Limit)
        max_retries = 5
        base_delay = 15
        embedding = None

        for attempt in range(max_retries):
            try:
                embedding = self.get_embedding(text)
                break
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"   ⚠️ API 429. Сплю {wait_time} сек... (Попытка {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Ошибка генерации эмбеддинга: {e}")
                    return

        if embedding:
            conn = None
            try:
                conn = self._get_valid_conn()
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO marina_knowledge (content, metadata, embedding) VALUES (%s, %s, %s)",
                        (text, psycopg2.extras.Json(meta), embedding)
                    )
                    conn.commit()
                print("   ✅ Успешно проиндексировано в Neon")
            except Exception as e:
                print(f"❌ Ошибка записи в БД: {e}")
            finally:
                if conn:
                    self.connection_pool.putconn(conn)

    def search(self, query: str, limit=5):
        if not self.enabled:
            return []

        conn = None
        try:
            query_embedding = self.get_embedding(query)
            conn = self._get_valid_conn()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT content, metadata, 1 - (embedding <=> %s::vector) as similarity FROM marina_knowledge ORDER BY similarity DESC LIMIT %s",
                    (query_embedding, limit)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Ошибка поиска Neon: {e}")
            return []
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def health_check(self):
        """Проверка живости БД."""
        if not self.enabled:
            return False
        try:
            conn = self._get_valid_conn()
            self.connection_pool.putconn(conn)
            return True
        except:
            return False
