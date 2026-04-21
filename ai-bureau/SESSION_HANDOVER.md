# AI BUREAU: Session Handover (08.04.2026)

## 🏗 Что сделано:
1. **RAG Инфраструктура**: Работает на связке `scripts/ingest.js` (индексация) + `server.js` (поиск и чат).
2. **База знаний**: `knowledge/processed/vectors.json` — содержит семантические векторы твоего справочника.
3. **BureauBot**: Стильный React-компонент в `App.tsx`, подключен к бэкенду на порту 3001.

## 🛠 Как запустить все системы:
1. В одной вкладке терминала: `npm run dev` (Фронтенд на порту 3000).
2. Во второй вкладке: `node server.js` (ИИ-Бэкенд на порту 3001).
3. Чтобы обновить знания бота: отредактируй `knowledge/raw/manual.txt` и запусти `node scripts/ingest.js`.

## 🚀 План (Обновлено после паузы):
- [ ] **Supabase Setup**: Ждем ключи (URL + Anon Key) после перезагрузки.
- [ ] **Database Migration**: Перенос данных из `vectors.json` в `pgvector`.
- [ ] **Serverless API**: Адаптация под Vercel Functions.
- [ ] **Final Deploy**: Запуск на Vercel.

**Статус: Ожидание ключей от шефа. Перезагрузка...** 🔄
