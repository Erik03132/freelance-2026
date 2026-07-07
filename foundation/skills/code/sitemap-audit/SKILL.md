---
name: sitemap-audit
description: Быстрый SEO-аудит сайтов через sitemap.xml. Парсит 500K+ URL за секунды, находит слабые посадочные без полного краулинга.
---

## Когда использовать
- Нужен быстрый SEO-аудит большого сайта
- Полный краулинг занимает слишком много времени
- Хочешь найти "пустые" посадочные страницы
- Нужно проанализировать структуру URL

## Установка

```bash
# В проекте ai-bureau
cd projects/ai-bureau
npm install xml2js
```

## Быстрый старт

```bash
# Запуск аудита
node scripts/sitemap-audit.js example.com

# Результат:
# - Отчёт в консоль
# - CSV файл: audit-report-{domain}-{date}.csv
```

## Как работает

### 1. Парсинг sitemap.xml
```javascript
import { parseSitemap } from './sitemap-parser.js';

const urls = await parseSitemap('https://example.com/sitemap.xml');
// Возвращает: [{url, lastmod, changefreq, priority}]
```

### 2. Выделение паттернов URL
```javascript
import { extractPatterns } from './sitemap-parser.js';

const patterns = extractPatterns(urls.map(u => u.url));
// Возвращает: {'/product': {count: 150, pageType: 'product', examples: [...]}}
```

### 3. Оценка потенциала URL
```javascript
import { evaluateUrlPotential } from './demand-matcher.js';

const evaluation = evaluateUrlPotential(url, {
  priority: '0.8',
  lastmod: '2026-06-01',
  changefreq: 'weekly'
});
// Возвращает: {url, keywords, queries, score: 75, status: 'high'}
```

## Критерии оценки URL

| Фактор | Баллы | Описание |
|--------|-------|----------|
| Ключевые слова в URL | +20-30 | Длинные осмысленные сегменты |
| Приоритет в sitemap | +0-20 | priority="0.8" → +16 баллов |
| Частота обновлений | +10 | daily/weekly → +10 |
| Свежесть контента | +15 | lastmod < 30 дней |
| Устаревший контент | -20 | lastmod > 365 дней |

**Итого:** 0-100 баллов
- 70-100: 💪 Сильная страница
- 40-69: 😐 Средняя страница
- 0-39: ⚠️ Слабая страница

## Пример вывода

```
🚀 Sitemap-First Audit: habr.com

📊 СТАТИСТИКА:
   Всего URL: 456391
   Паттернов: 10

📈 АНАЛИЗ ПАТТЕРНОВ:
   💪 Сильные: 9
   😐 Средние: 1
   ⚠️  Слабые: 0

🏆 ТОП-5 СИЛЬНЫХ ПАТТЕРНОВ:
   1. [80] /ru/articles (232476 URL, blog)
   2. [80] /ru/companies (140735 URL, other)
   3. [80] /ru/news (64758 URL, other)

💡 РЕКОМЕНДАЦИИ:
   📊 Найдено 1 больших паттернов (>50 URL). Проверьте: нет ли дублей.

💾 Отчёт сохранён: audit-report-habr.com-2026-06-25.csv
```

## Сравнение с полным краулингом

| Метод | Время (500K URL) | Нагрузка | Результат |
|-------|------------------|----------|-----------|
| Полный краулинг | 30+ минут | Высокая | Все страницы |
| Sitemap-first | 10 секунд | Низкая | Структура + слабые места |

**Экономия времени:** 200x

## Интеграция с ботом

```javascript
// В боте Маркетолог
bot.onText(/\/audit (.+)/, async (msg, match) => {
  const domain = match[1];
  const report = await generateReport(domain);
  
  const message = `
📊 Аудит ${domain}:
- URL: ${report.totalUrls}
- Сильных: ${analysis.strong.length}
- Слабых: ${analysis.weak.length}
  `;
  
  bot.sendMessage(msg.chat.id, message);
});
```

## Troubleshooting

**Sitemap не найден:**
```javascript
// Проверь разные пути
const paths = ['/sitemap.xml', '/sitemap_index.xml', '/sitemap-index.xml'];
```

**Sitemap index (вложенные sitemap):**
```javascript
// parseSitemap автоматически обрабатывает sitemap index
const urls = await parseSitemap('https://example.com/sitemap_index.xml');
```

## Ресурсы
- Пример: `projects/ai-bureau/scripts/sitemap-audit.js`
- [XML Sitemap Protocol](https://www.sitemaps.org/protocol.html)
