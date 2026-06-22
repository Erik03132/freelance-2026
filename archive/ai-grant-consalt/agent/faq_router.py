import os
import json
from difflib import SequenceMatcher

def string_similarity(a: str, b: str) -> float:
    """Возвращает степень похожести двух строк (от 0.0 до 1.0)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def jaccard_similarity(a: str, b: str) -> float:
    """Сходство по пересечению слов (игнорирует порядок)"""
    set1 = set([word.strip("?.,!") for word in a.lower().split()])
    set2 = set([word.strip("?.,!") for word in b.lower().split()])
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0.0

class FAQRouter:
    def __init__(self):
        self.faq_db = []
        self._load_cache()
        self.SIMILARITY_THRESHOLD = 0.78 # Повышен: пропускаем сложные вопросы в Graph RAG

    def _load_cache(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'faq_cache.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.faq_db = json.load(f)

    def search_fast_lane(self, query: str):
        """
        Ищет ответ в горячем кеше. Если находит - отдает мгновенно.
        Иначе возвращает None, сигнализируя о необходимости запуска тяжелого RAG (Perplexity).
        """
        best_score = 0.0
        best_answer = None

        print(f"⚡ [FAQ Router]: Сканирую горячий кеш ({len(self.faq_db)} вопросов)...")

        for item in self.faq_db:
            # Комбинируем метрики для надежности текста без нейросетей
            score1 = string_similarity(query, item["question"])
            score2 = jaccard_similarity(query, item["question"])
            final_score = max(score1, score2)

            if final_score > best_score:
                best_score = final_score
                best_answer = item["answer"]

        if best_score >= self.SIMILARITY_THRESHOLD:
            print(f"✅ [FAQ Router]: Найдено совпадение в кеше! (Точность: {best_score*100:.1f}%)")
            return best_answer
        
        print(f"❌ [FAQ Router]: Совпадений не найдено (Макс. точность {best_score*100:.1f}%). Маршрутизирую в Deep RAG...")
        return None

    def learn_new_answer(self, query: str, answer: str):
        """
        SELF-LEARNING LOOP: Автоматически добавляет новый, сгенерированный сложным путем ответ,
        в горячий кеш. С этого момента на этот вопрос система будет отвечать мгновенно.
        """
        new_id = f"faq_{len(self.faq_db) + 1:03d}"
        new_entry = {
            "id": new_id,
            "question": query,
            "answer": answer
        }
        self.faq_db.append(new_entry)
        
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'faq_cache.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.faq_db, f, ensure_ascii=False, indent=2)
        
        print(f"🧠 [Самообучение]: Новый ответ навсегда записан в горячий кеш ({new_id}).")

if __name__ == "__main__":
    router = FAQRouter()
    
    # Тест 1: Точное или почти точное попадание
    query1 = "Как сейчас получить ИТ аккредитацию?"
    print(f"\nВопрос: {query1}")
    ans1 = router.search_fast_lane(query1)
    if ans1:
        print(f"ОТВЕТ: {ans1}")
        
    # Тест 2: Сложный нетипичный вопрос (должен уйти мимо кеша)
    query2 = "А если у меня филиал в Казахстане, дадут ли микрогрант ФСИ?"
    print(f"\nВопрос: {query2}")
    ans2 = router.search_fast_lane(query2)
    if ans2:
        print(f"ОТВЕТ: {ans2}")
