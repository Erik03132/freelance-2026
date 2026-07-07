"""Smoke tests for knowledge_base module (data layer only)."""

import json
import tempfile
from pathlib import Path


def _make_kb_data():
    return {
        "company": {
            "name": "Глобал Филдс Экспорт",
            "phone": "+7(918)639-30-30"
        },
        "faq": [
            {
                "question": "Какие культуры закупаете?",
                "answer": "Пшеницу, ячмень, кукурузу, подсолнечник, рапс."
            },
            {
                "question": "Какие минимальные объемы?",
                "answer": "От 100 тонн для зерновых."
            }
        ],
        "objections": [
            {
                "objection": "Уже работаю с другим покупателем",
                "response": "Понимаю, мы можем предложить альтернативные условия."
            },
            {
                "objection": "Цены низкие",
                "response": "Готовы обсудить индивидуальные условия."
            }
        ],
        "products": {
            "пшеница": {"price": "по рынку", "min_volume": 100}
        },
        "delivery_terms": {
            "CPT": "доставка до терминала"
        }
    }


def _make_kb(data=None):
    from levitan.knowledge_base import KnowledgeBase
    payload = data if data is not None else _make_kb_data()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
        tmp_path = Path(f.name)
    return KnowledgeBase(tmp_path), tmp_path


def test_find_objection_first_match():
    kb, path = _make_kb()
    try:
        response = kb.find_objection_response("я уже работаю с другим покупателем")
        assert response is not None
        assert "Понимаю" in response
    finally:
        path.unlink(missing_ok=True)


def test_find_objection_second_match():
    kb, path = _make_kb()
    try:
        response = kb.find_objection_response("предлагаю низкие цены")
        assert response is not None
        assert "Готовы обсудить" in response
    finally:
        path.unlink(missing_ok=True)


def test_find_objection_partial_word():
    """'работаю' from objection text appears in client text."""
    kb, path = _make_kb()
    try:
        response = kb.find_objection_response("я уже работаю с другим покупателем")
        assert response is not None
    finally:
        path.unlink(missing_ok=True)


def test_get_company_info():
    kb, path = _make_kb()
    try:
        info = kb.get_company_info()
        assert info["name"] == "Глобал Филдс Экспорт"
        assert info["phone"] == "+7(918)639-30-30"
    finally:
        path.unlink(missing_ok=True)


def test_get_products():
    kb, path = _make_kb()
    try:
        products = kb.get_products()
        assert "пшеница" in products
        assert products["пшеница"]["min_volume"] == 100
    finally:
        path.unlink(missing_ok=True)


def test_load_empty_json():
    kb, path = _make_kb({})
    try:
        assert kb._data == {}
        assert kb._faq_texts == []
    finally:
        path.unlink(missing_ok=True)
