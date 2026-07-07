"""
Тест LLM2Vec эмбеддера.

Проверяет:
1. Загрузку модели
2. Генерацию эмбеддингов
3. Семантический поиск
"""
import sys
import time
from llm2vec_embedder import LLM2VecEmbedder


def test_basic():
    """Базовый тест: загрузка + эмбеддинги."""
    print("=" * 60)
    print("ТЕСТ 1: Базовая функциональность")
    print("=" * 60)
    
    start = time.time()
    embedder = LLM2VecEmbedder(device="cpu")
    load_time = time.time() - start
    print(f"⏱️  Время загрузки модели: {load_time:.1f}s")
    
    texts = [
        "Как ухаживать за попугаем корелла?",
        "Кормление кореллы: семена, фрукты, овощи",
        "Клетка для попугая должна быть просторной",
        "Python — язык программирования",
    ]
    
    start = time.time()
    embeddings = embedder.encode(texts)
    encode_time = time.time() - start
    
    print(f"✅ Эмбеддинги созданы: shape={embeddings.shape}")
    print(f"⏱️  Время кодирования {len(texts)} текстов: {encode_time:.2f}s")
    print(f"📊 Размерность: {embeddings.shape[1]}")
    
    return embedder


def test_similarity(embedder):
    """Тест семантического сходства."""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Семантический поиск")
    print("=" * 60)
    
    query = "чем кормить попугая"
    documents = [
        "Корелла любит семена подсолнечника и просо",
        "Клетка должна быть не менее 60x40x60 см",
        "Попугаю нужны свежие фрукты и овощи ежедневно",
        "Python используется для машинного обучения",
        "Корелла может прожить до 25 лет в неволе",
    ]
    
    start = time.time()
    similarities = embedder.similarity(query, documents)
    search_time = time.time() - start
    
    print(f"\n🔍 Запрос: '{query}'")
    print(f"⏱️  Время поиска: {search_time:.2f}s")
    print("\n📋 Результаты (отсортированы по релевантности):")
    
    ranked = sorted(
        zip(similarities, documents),
        key=lambda x: x[0],
        reverse=True
    )
    
    for i, (score, doc) in enumerate(ranked, 1):
        print(f"{i}. [{score:.4f}] {doc}")
    
    return ranked


def test_comparison():
    """Сравнение с простым поиском."""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Сравнение с keyword search")
    print("=" * 60)
    
    query = "уход за птицей"
    documents = [
        "Корелла требует ежедневного ухода и внимания",
        "Клетку нужно чистить раз в неделю",
        "Попугай корелла — дружелюбная птица",
        "Автомобиль Toyota Camry 2020 года",
        "Ветеринар осматривает попугая каждый месяц",
    ]
    
    # LLM2Vec search
    embedder = LLM2VecEmbedder(device="cpu")  # Sheared-Llama-2.7B
    llm_scores = embedder.similarity(query, documents)
    
    # Keyword search
    query_words = set(query.lower().split())
    keyword_scores = []
    for doc in documents:
        score = sum(1 for w in query_words if w in doc.lower())
        keyword_scores.append(score)
    
    print(f"\n🔍 Запрос: '{query}'")
    print("\n📊 Сравнение методов:")
    print(f"{'Документ':<50} {'LLM2Vec':>10} {'Keyword':>10}")
    print("-" * 72)
    
    for doc, llm_s, kw_s in zip(documents, llm_scores, keyword_scores):
        doc_short = doc[:47] + "..." if len(doc) > 50 else doc
        print(f"{doc_short:<50} {llm_s:>10.4f} {kw_s:>10}")
    
    print("\n💡 Вывод: LLM2Vec понимает семантику, keyword — только слова")


if __name__ == "__main__":
    print("🚀 Тестирование LLM2Vec Embedder\n")
    
    try:
        embedder = test_basic()
        test_similarity(embedder)
        
        if "--compare" in sys.argv:
            test_comparison()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
