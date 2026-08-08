# OmniRoute Patches — Context Filter & Handoff Fix

## Проблема 1: filterTargetsByRequestCompatibility отбрасывает 20/23 моделей

**Файл:** `open-sse/services/combo/comboStructure.ts`

**Причина:** OpenCode отправляет запросы с контекстом ~200K токенов. Функция
`filterTargetsByRequestCompatibility` вычисляет `requiredContextTokens` и через
`evaluateContextLimit` проверяет каждый таргет. Модели с контекстным окном < 200K
отбрасываются. Большинство бесплатных OpenRouter-моделей имеют окна 8K-128K.

**Варианты фикса:**

### Вариант A: lenient mode (простой)
В `filterTargetsByRequestCompatibility`, после строки где начинается контекстная
фильтрация, добавить проверку на режим "lenient":

```typescript
// В начале filterTargetsByRequestCompatibility, после extraction:
// Если contextFilterMode = "lenient" — не дропаем модели по контексту,
// оставляем их в пуле (пусть fail на этапе отправки, а не на этапе фильтрации)

const contextFilterMode = (body as any)._omniroute_contextFilterMode
  || process.env.OMNIROUTE_CONTEXT_FILTER_MODE
  || "strict";

if (contextFilterMode === "lenient" && requirements.requiredContextTokens > 0) {
  // В lenient-режиме пропускаем проверку контекстного окна
  // Контекстное окно будет проверено провайдером на этапе отправки
  requirements.requiredContextTokens = 0;
}
```

### Вариант B: увеличить заявленный контекст OpenRouter-моделей
В `src/lib/modelCapabilities.ts` (или где хранятся capabilities моделей) увеличить
`contextWindow` для openrouter-моделей. Например, если модель заявляет 8K,
увеличить до 200K. Это обманет фильтр, но может вызвать ошибки на провайдере.

**Рекомендация:** Вариант A — быстрее и безопаснее.

---

## Проблема 2: Handoff не работает для priority-стратегии

**Файлы:** `open-sse/services/contextHandoff.ts` + `open-sse/services/combo.ts`

**Причина:** Universal handoff уже включён по умолчанию (`DEFAULT_UNIVERSAL_HANDOFF_CONFIG.enabled: true`),
но требует `sessionId`. В коде `maybeGenerateUniversalHandoff()` (contextHandoff.ts):

```typescript
if (!options.sessionId) return; // ← стоп-кран
```

SessionId извлекается из заголовков `X-Session-Id` / `x-codex-session-id` / `x-omniroute-session`
через `extractSessionAffinityKey()` в combo.ts. OpenCode НЕ передаёт эти заголовки.

**Фикс:** в combo.ts, в точке где вызывается универсальный handoff (~строка 1342),
добавить генерацию sessionId если его нет:

```typescript
// В combo.ts, перед вызовом maybeGenerateUniversalHandoff:
let effectiveSessionId = extractSessionAffinityKey(requestHeaders);
if (!effectiveSessionId) {
  // Генерируем sessionId из хеша сообщений + comboName
  const crypto = await import('node:crypto');
  const msgHash = crypto.createHash('sha256')
    .update(JSON.stringify(messages.slice(-3)))
    .digest('hex').slice(0, 16);
  effectiveSessionId = `auto:${comboName}:${msgHash}`;
}

maybeGenerateUniversalHandoff({
  sessionId: effectiveSessionId,
  comboName,
  messages,
  prevModel,
  currModel,
  universalConfig,
  handleSingleModel,
});
```

---

## Применение патчей на VPS

```bash
# 1. Зайти на VPS
ssh root@217.149.23.113

# 2. Найти установленный omniroute
OMNIDIR=$(npm root -g)/omniroute

# 3. Патч 1 — contextFilterMode lenient
# Добавить в начало filterTargetsByRequestCompatibility:
sed -i '/function filterTargetsByRequestCompatibility/,/const requirements = deriveRequestCompatibilityRequirements/{
  /const requirements = deriveRequestCompatibilityRequirements/i\
  const contextFilterMode = process.env.OMNIROUTE_CONTEXT_FILTER_MODE || "strict";\
  if (contextFilterMode === "lenient" && estimateRequestInputTokens(body) > 0) {\
    ; // skip context filtering\
  }
}' $OMNIDIR/open-sse/services/combo/comboStructure.js

# 4. Установить переменную в .env
echo 'OMNIROUTE_CONTEXT_FILTER_MODE=lenient' >> /root/.omniroute/.env

# 5. Патч 2 — sessionId для priority
# (ручная правка combo.js, т.к. сложнее автоматизировать)

# 6. Перезапустить
pm2 restart omniroute
```

## Обходной путь (без патча кода)

Пока VPS недоступен, `omni-auto-router` на :8123 работает как fallback:
- Определяет, что VPS недоступен (health check кешируется на 60с)
- Шлёт запросы напрямую в OpenRouter, минуя VPS
- Имеет 15 бесплатных моделей в цепочке Tier 0
- Работает через локальный Ollama (qwen2.5:7b) как первый вариант
