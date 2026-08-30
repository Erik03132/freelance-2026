#!/usr/bin/env python3
"""AI Scout Fast Triage — автооценка новостей по релевантности и качеству."""

import sqlite3
import json
import sys
from datetime import datetime, timedelta

# Ключевые слова для скоринга
POSITIVE_KEYWORDS = [
    'agent', 'agents', 'ai', 'llm', 'gpt', 'gemini', 'claude', 'openai',
    'anthropic', 'google', 'nvidia', 'hugging face', 'model', 'models',
    'inference', 'rag', 'rag', 'voice', 'crm', 'telegram', 'bitrix',
    'open source', 'open-source', 'fine-tuning', 'quantization',
    'qwen', 'llama', 'mistral', 'gemma', 'local llm', 'api',
    'automation', 'automate', 'workflow', 'bot', 'bots',
    'coding', 'developer', 'deployment', 'serving', 'vllm',
    'benchmark', 'reasoning', 'multimodal', 'mcp',
    'ИИ', 'нейросеть', 'модель', 'агент', 'голосовой', 'бот',
    'RAG', 'внедрение', 'промптинг', 'fine-tuning', 'квантизация',
    'qwen', 'llama', 'open source', 'fine-tune'
]

NEGATIVE_KEYWORDS = [
    'celebrity', 'entertainment', 'movie', 'film', 'music',
    'game', 'gaming', 'sport', 'fashion', 'beauty', 'recipe',
    'travel', 'weather', 'politics', 'election', 'trump', 'biden',
    'covid', 'virus', 'health', 'diet', 'weight', 'fitness',
    'children', 'baby', 'pregnancy', 'parenting',
    'advertisement', 'sponsored', 'ad ', 'clickbait'
]


def score_text(text: str) -> float:
    """Score 0.0–1.0 по плотности ключевых слов."""
    if not text:
        return 0.0
    text_lower = text.lower()
    
    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw.lower() in text_lower)
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw.lower() in text_lower)
    
    score = min(pos_count / 5.0, 1.0)  # нормализуем к 5 совпадениям = 1.0
    score -= neg_count * 0.15  # штраф
    return max(0.0, min(1.0, score))


def run_triage(db_path: str = None) -> list:
    """Run triage on all items with status='new'."""
    if db_path is None:
        import os
        db_path = os.path.expanduser("~/freelance-2026/ai-scout.db")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, source, url, title, raw_text, author, timestamp
        FROM features
        WHERE status = 'new'
        ORDER BY id DESC
        LIMIT 50
    """)
    
    items = cursor.fetchall()
    results = []
    
    for item in items:
        combined = f"{item['title']} {item['raw_text'] or ''}"
        score = score_text(combined)
        
        # Сохраняем скор
        cursor.execute(
            "UPDATE features SET initial_score = ?, status = 'triaged' WHERE id = ?",
            (score, item['id'])
        )
        
        results.append({
            'id': item['id'],
            'source': item['source'],
            'title': item['title'],
            'url': item['url'],
            'author': item['author'],
            'score': score,
            'timestamp': item['timestamp']
        })
    
    conn.commit()
    conn.close()
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else None
    results = run_triage(db_path)
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Summary
    if results:
        print(f"\n--- SUMMARY ---")
        print(f"Total triaged: {len(results)}")
        high = [r for r in results if r['score'] >= 0.4]
        print(f"High score (>=0.4): {len(high)}")
        for r in high[:5]:
            print(f"  [{r['source']}] {r['title'][:50]}... (score: {r['score']:.2f})")
