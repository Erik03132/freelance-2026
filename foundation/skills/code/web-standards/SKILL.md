---
name: web-standards
description: React/Vite/TypeScript frontend standards, component patterns, Core Web Vitals, accessibility WCAG AA, SEO checklist, CSS architecture.
---

## Tech Stack (по умолчанию)
| Задача | Инструмент |
|--------|-----------|
| Сборка | **Vite** + React + TypeScript |
| Стили | Vanilla CSS |
| State | useState/useReducer / Zustand |
| Валидация | Zod |
| Тестирование | Playwright (E2E) |

## Core Web Vitals Targets
| Метрика | Цель | Как достичь |
|---------|------|------------|
| LCP | < 2.5 сек | WebP, preload critical fonts |
| FID/INP | < 100ms | Минимизировать JS, defer non-critical |
| CLS | < 0.1 | Задавать размеры изображений, избегать layout shifts |

## SEO Checklist (для каждой страницы)
- Уникальный `<title>` (50-60 символов), `<meta description>` (150-160)
- Единственный `<h1>`, правильная иерархия H1 → H2 → H3
- Семантические HTML5 элементы, Schema.org
- OG-теги, `<img alt>`

## Accessibility (a11y)
- Keyboard navigation, ARIA-атрибуты, Focus management
- Touch targets: минимум 44x44px
- Контрастность: WCAG AA (4.5:1)

## Ограничения
- Mobile First, Vanilla CSS по умолчанию
- Semantic HTML — `<div>` только когда нет семантической альтернативы
- Не добавлять зависимости ради зависимостей
