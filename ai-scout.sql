CREATE TABLE IF NOT EXISTS features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,          -- youtube/tg/gmail/habr_angela
    url TEXT UNIQUE NOT NULL,      -- Исходная ссылка
    title TEXT NOT NULL,           -- Заголовок
    raw_text TEXT,                 -- Сырой текст / расшифровка
    author TEXT,                   -- Автор/источник
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    initial_score REAL,            -- Предсказание Angela
    status TEXT DEFAULT 'new',     -- new → triaged → expert_review → accepted/rejected/archived
    hermes_verdict TEXT,           -- Итоговый вердикт эксперта
    action_taken TEXT              -- Таска/ES-N или причина отклонения
);