# AI Bureau · Website

> **Сайт инженерного бюро по проектированию автономных AI-систем.**  
> Astro + React + BureauBot. Dark theme с Apple-style анимациями.

---

## 🏗 Стек

| Технология | Назначение |
|-----------|-----------|
| [Astro](https://astro.build) v5 | Статическая генерация |
| [React](https://react.dev) 18 | BureauBot (остров) |
| [Inter](https://fonts.google.com/specimen/Inter) | Шрифт |
| CSS (native) | Apple-анимации, scroll-reveal, stagger |

## 🎨 Дизайн

- **Тёмная тема** (черный фон, cyan #00f0ff акцент)
- **Apple-style easing** — `ease-out` для входа, `spring` для интерактива
- **Scroll-reveal** — элементы появляются при скролле (Intersection Observer)
- **Stagger** — карточки появляются по очереди
- **Микро-анимации** — hover, focus, click-эффекты
- **prefers-reduced-motion** — анимации отключаются для accessibility

## 📄 Страницы

| Страница | Описание |
|----------|---------|
| `/` | Главная: 5 услуг, процесс, кейсы, CTA |
| `/services/ai-agents` | AI-агенты с RAG |
| `/services/voice-bots` | Голосовые боты |
| `/services/rag-knowledge` | Чат-боты с базой знаний |
| `/services/private-llm` | Private LLM |
| `/services/audit` | AI-консалтинг |
| `/cases` | Портфолио и кейсы |
| `/faq` | Частые вопросы (JSON-LD) |
| `/contact` | Контакты |

## 🚀 Запуск

```bash
cd ai-bureau
npm install
npm run dev      # dev-сервер на :4321
npm run build    # production сборка
npm run server   # PM2-сервер с RAG
```

## 🤖 BureauBot

React-компонент чата (встроен на каждой странице через `client:load`):
- Квалификация лидов (бизнес → задача → бюджет → контакт)
- RAG-ответы на основе базы знаний
- Smart Fallback (наводящие вопросы при непонимании)
- Передача на оператора с ИИ-выжимкой

## 🔍 SEO/GEO

- JSON-LD разметка (Organization, FAQPage, Service)
- `llms.txt` для AI-поисковиков (Яндекс Нейро, Perplexity)
- `robots.txt` + `sitemap.xml` (авто)

---

<p align="center">
  <sub>AI BUREAU © 2026 · architect@ai-bureau.pro</sub>
</p>
