# Фронтенд-стандарты AI Bureau

## Tech Stack проекта
| Задача | Инструмент |
|--------|-----------|
| Сборка | **Vite** + React + TypeScript |
| Стили | Vanilla CSS (TailwindCSS только по запросу) |
| Анимации | CSS animations / Framer Motion |
| State | useState/useReducer (простое) / Zustand (сложное) |
| Валидация | Zod |
| Тестирование | Playwright (E2E) |

## Component Patterns
- **Composition > Inheritance** — `<Card><CardHeader/><CardBody/></Card>`
- **Compound Components** — Context + Provider для связанных компонентов
- **Render Props** — для переиспользуемой логики с custom rendering

## Performance Optimization
- React.memo, useMemo, useCallback — мемоизация
- Code splitting через lazy() + Suspense
- Виртуализация длинных списков (@tanstack/react-virtual)

## Core Web Vitals Targets
| Метрика | Цель | Как достичь |
|---------|------|------------|
| LCP | < 2.5 сек | WebP, preload critical fonts |
| FID/INP | < 100ms | Минимизировать JS, defer non-critical |
| CLS | < 0.1 | Задавать размеры изображений, избегать layout shifts |

## SEO Checklist (для каждой страницы)
- Уникальный `<title>` (50-60 символов)
- `<meta description>` (150-160 символов)
- Единственный `<h1>` на странице
- Правильная иерархия H1 → H2 → H3
- Семантические HTML5 элементы (`<main>`, `<article>`, `<nav>`)
- Schema.org разметка (Organization, Service, FAQ)
- OG-теги для соцсетей
- `<img alt>` на всех изображениях

## Accessibility (a11y)
- Keyboard navigation на всех интерактивных элементах
- ARIA-атрибуты: `role`, `aria-expanded`, `aria-modal`
- Focus management
- Touch targets: минимум 44x44px
- Контрастность: WCAG AA (4.5:1)

## Ограничения
- Сайт обязан грузиться < 3 секунд на 3G
- Mobile First — всегда начинай с мобильной версии
- Vanilla CSS по умолчанию
- Никаких placeholder-изображений в финальном продукте
- Semantic HTML — `<div>` только когда нет семантической альтернативы
- Не добавлять зависимости ради зависимостей
