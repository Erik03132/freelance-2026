# Ornith-1.5 — самообучающиеся агентные LLM (локальный «мозг»)

**Что:** семейство открытых (MIT) агентных LLM с энд-ту-энд самоулучшением
(self-scaffolding → self-improvement loop). Модель сама генерит задачи →
скаффолды → solution-rollouts для RL, непрерывно расширяя свой curriculum.
Репозиторий/сайт: https://ornith.ai/ornith_1_5.html
Веса: HF `ornith-ai/Ornith-1.5-*` (коллекция), есть GGUF/FP8/MLX/NVFP4.

**Три размера:**
- **397B MoE** — флагман, на уровне Claude Opus 4.8 (Terminal-Bench 2.1: 86.1 vs
  85.0; DeepSWE 56 vs 59; SWE-bench Verified 86 vs 85.8). Локально НЕ поднять
  (нужен GPU-кластер).
- **35B MoE (A3B)** — активирует 3B/токен. Terminal-Bench 2.1: 68.5 (бьёт
  Gemma-4-31B 43.4 и Muse-Glimmer-30B 51.7); SWE-bench Verified 79. Локально
  реально через llama.cpp / vLLM.
- **9B Dense** (+ квант `-Mobile` под iPhone/Android). Terminal-Bench 2.1: 47.0;
  SWE-bench Verified 70.6 — обходит Gemma-4-31B (52) и Qwen3.6-35B-A3B.
  Есть GGUF → на Mac (M-серия, MLX) крутится локально.

**Где юзать:** локальный агентный «мозг» для агентов бюро (Levitan/AVM/Angela)
вместо/вместе с облачными моделями. Главная фишка — метод самоулучшения
(генерация задач × скаффолд × прогон, GRPO по наградам
validity × difficulty × novelty), то есть не просто веса, а способ выращивать
агентность.

**ВАЖНО — не замена macos-harness:** это разные слои. macos-harness = «руки»
(computer-use runtime на Mac, дёргает GUI/клавиатуру по PID). Ornith-1.5 =
«голова» (LLM, принимает решения). Стыкуют: Ornith решает → macos-harness
исполняет. Заменять одно другим нельзя.

**Запуск (из HF-карточек):**
```bash
# 9B GGUF, OpenAI-совместимый API на :8000
llama-server -hf hf.co/ornith-ai/Ornith-1.5-9B-GGUF --port 8000 -c 262144

# vLLM (9B, tool-calling)
vllm serve ornith-ai/Ornith-1.5-9B --served-model-name Ornith-1.5-9B \
  --max-model-len 262144 --gpu-memory-utilization 0.90 \
  --enable-auto-tool-choice --tool-call-parser qwen3_xml \
  --reasoning-parser qwen3 --trust-remote-code

# sglang (35B/9B)
python -m sglang.launch_server --model-path ornith-ai/Ornith-1.5-9B \
  --context-length 262144 --mem-fraction-static 0.85 \
  --tool-call-parser qwen3_coder --reasoning-parser qwen3
```

**Риски (экспертиза, авг-2026):**
- Цифры self-reported (от вендора); независимых бенчей мало. На LocalLLaMA хвалят
  9B («лучший 9B для агентов», 57% vs 33% у Qwen3.5-9B на бенче автора), но
  выборка малая → проверять живьём.
- Под капотом Qwen-линейка: нужна аккуратная настройка chat-template (в форкноутах
  сами предупреждают про Qwen template mismatch с vLLM/Harbor).
- Контекст 262K, tool/parser `qwen3_coder`+`qwen3` — заточено под агентный
  coding/tool-use, не универсальный чат.
- 397B локально недоступен; для нас рабочие варианты — только 9B и 35B-A3B.
- Для роли Chief (read-only) не нужно — инфраструктура worker-агента.

**Статус:** Кандидат. Брать 9B-GGUF (Mac) и 35B-A3B (сервер) как локальный
агентный мозг; стыковать с macos-harness, не заменять. Проверить живьём на
реальной задаче бюро перед продом.
