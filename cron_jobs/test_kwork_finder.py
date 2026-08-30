#!/usr/bin/env python3
"""
Тесты на чистую логику kwork_finder.py v2 (без сети).
Прогон: python3 test_kwork_finder.py  (или pytest).
"""
import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kwork_finder as kf


class TestExtractors(unittest.TestCase):
    def test_budget_plain(self):
        self.assertEqual(kf.extract_budget("Бюджет: 8000 руб."), 8000.0)
        self.assertEqual(kf.extract_budget("до 5000 ₽"), 5000.0)

    def test_budget_thousands(self):
        self.assertEqual(kf.extract_budget("цена 5 тыс"), 5000.0)
        self.assertEqual(kf.extract_budget("до 3к"), 3000.0)

    def test_budget_none(self):
        self.assertIsNone(kf.extract_budget("обсуждается"))

    def test_proposals(self):
        self.assertEqual(kf.extract_proposals("Предложений: 12"), 12)
        self.assertEqual(kf.extract_proposals("15 предложений"), 15)
        self.assertEqual(kf.extract_proposals("откликнулись 4"), 4)

    def test_proposals_none(self):
        self.assertIsNone(kf.extract_proposals("без цифр"))

    def test_client_orders(self):
        info = kf.extract_client_info("Заказов на сайте: 12 Рейтинг: 4.8 подтверждён")
        self.assertEqual(info["orders"], 12)
        self.assertAlmostEqual(info["rating"], 4.8)
        self.assertTrue(info["verified"])

    def test_rating_not_from_orders(self):
        # "12 заказов" НЕ должно давать ложный рейтинг
        info = kf.extract_client_info("У заказчика 12 заказов, новый аккаунт")
        self.assertEqual(info["orders"], 12)
        self.assertIsNone(info["rating"])


class TestHardExclude(unittest.TestCase):
    def test_video_excluded(self):
        job = {"title": "Создать видео для YouTube", "desc": "монтаж ролика, анимация",
               "budget": 5000, "proposals": 5, "client_info": {}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "X")
        self.assertIn("video", ev["skill_detail"]["exclude"])

    def test_logo_excluded(self):
        job = {"title": "Нарисовать логотип и фирменный стиль", "desc": "брендинг, упаковка",
               "budget": 4000, "proposals": 5, "client_info": {}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "X")
        self.assertIn("logo_design", ev["skill_detail"]["exclude"])

    def test_mobile_excluded(self):
        job = {"title": "Мобильное приложение на Flutter", "desc": "iOS и Android",
               "budget": 50000, "proposals": 5, "client_info": {}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "X")


class TestSkillMatch(unittest.TestCase):
    def test_telegram_bitrix_is_ours(self):
        # РЕАЛЬНОЕ ТЗ (desc длиннее заголовка) -> матч по описанию, решение A
        job = {"title": "Telegram-бот на aiogram + Bitrix24",
               "desc": ("Нужен Telegram-бот на aiogram, который забирает сделки из "
                        "Bitrix24 CRM и шлёт уведомления в чат. Интеграция по API."),
               "budget": 8000, "proposals": 4,
               "client_info": {"orders": 12, "rating": 4.8, "verified": True, "found": True}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "A")
        self.assertGreaterEqual(ev["skill"], 60)

    def test_rag_is_ours(self):
        job = {"title": "RAG embeddings semantic search",
               "desc": ("Нужен semantic search поверх embeddings, vector store, "
                        "reranking и LangChain-пайплайн на Python для базы знаний."),
               "budget": 30000, "proposals": 22,
               "client_info": {"orders": 40, "rating": 5.0, "verified": True, "found": True}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "A")

    def test_too_many_proposals_excluded(self):
        job = {"title": "Telegram-бот на aiogram",
               "desc": ("Сделать Telegram-бота с интеграцией в CRM и парсингом "
                        "заявок через API."),
               "budget": 8000, "proposals": 85,
               "client_info": {"orders": 30, "rating": 4.9, "verified": True, "found": True}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "X")
        self.assertIn("задавлено", ev["reason"])

    def test_low_skill_excluded(self):
        # нет тех-маркеров под наши навыки, но и exclude нет -> неопределённый матч -> B (кандидат)
        job = {"title": "Помощь с документами", "desc": "нужна помощь с оформлением бумаг",
               "budget": 3000, "proposals": 2, "client_info": {}}
        ev = kf.evaluate(job)
        self.assertIn(ev["decision"], ("B", "X"))

    def test_weak_client_to_B(self):
        # РЕАЛЬНОЕ ТЗ, матч высокий, но заказчик с 0 заказами -> не A
        job = {"title": "Telegram-бот на aiogram",
               "desc": "Нужен бот с интеграцией Bitrix24 CRM и парсингом заявок.",
               "budget": 8000, "proposals": 3,
               "client_info": {"orders": 0, "rating": None, "verified": False, "found": True}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "B")
        self.assertIn("слабый/рисковый заказчик", ev["reason"])

    def test_false_A_by_title_only_is_B(self):
        # ЗАЩИТА (ADR-009): кворк "Работа без навыков" имеет в заголовке
        # случайный маркер (напр. "бот"/"автоматизация") и НЕТ реального ТЗ
        # (desc == title) -> это неопределённый матч -> B, а не фейковый A.
        job = {"title": "Работа без навыков, автоматизация процессов",
               "desc": "Работа без навыков, автоматизация процессов",
               "budget": None, "proposals": None, "client_info": {}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "B")
        self.assertIn("недостоверен", ev["reason"])

    def test_real_desc_lifts_to_A(self):
        # Реальное описание с ядром навыков -> матч по desc, а не только заголовку.
        job = {"title": "Нужен бот",
               "desc": ("Сделать Telegram-бота на aiogram с интеграцией Bitrix24 CRM, "
                        "парсинг заявок и выгрузка в Google Таблицы."),
               "budget": 8000, "proposals": 3,
               "client_info": {"orders": 12, "rating": 4.8, "verified": True, "found": True}}
        ev = kf.evaluate(job)
        self.assertEqual(ev["decision"], "A")
        self.assertIn("telegram_bot", ev["skill_detail"]["our"])


class TestDemoSanity(unittest.TestCase):
    def test_demo_runs(self):
        # demo не должен падать и должен выдать решения A и X
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            kf.run_demo(kf.DEFAULTS)
        out = buf.getvalue()
        self.assertIn("DEMO", out)
        self.assertIn("HARD_EXCLUDE", out)          # есть X по не-навыкам
        self.assertIn("финал 94", out)              # есть A с высоким финалом
        self.assertIn("на рассмотрение", out)       # есть B-кандидат (без реального ТЗ / слабый клиент)


if __name__ == "__main__":
    unittest.main(verbosity=2)
