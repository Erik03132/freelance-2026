import http from "http";
import fs from "fs";
import path from "path";

/* ──────────────────────────────────────────────────────────────────────────
 * Конфигурация и безопасный парсинг .env.local
 * Прежде здесь был наивный line.split("=") — он ломался на значениях,
 * содержащих "=" (например, в base64-токенах или URL с query-параметрами).
 * ────────────────────────────────────────────────────────────────────────── */
function loadEnv(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const content = fs.readFileSync(filePath, "utf-8");
  const env = {};
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIndex = trimmed.indexOf("=");
    if (eqIndex === -1) continue;
    const key = trimmed.slice(0, eqIndex).trim();
    // Берём всё ПОСЛЕ первого "=" — значение может содержать "=".
    let value = trimmed.slice(eqIndex + 1).trim();
    // Снимаем внешние кавычки, если они есть.
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    env[key] = value;
  }
  return env;
}

const env = loadEnv(path.join(process.cwd(), ".env.local"));
const PORT = Number(env.PORT) || 3001;
const OPENROUTER_API_KEY = env.OPENROUTER_API_KEY || "";
const TELEGRAM_BOT_TOKEN = env.TELEGRAM_BOT_TOKEN || "";
const TELEGRAM_CHAT_ID = env.TELEGRAM_CHAT_ID || "";

if (!OPENROUTER_API_KEY) {
  console.warn("⚠️  OPENROUTER_API_KEY не задан — ответы бота не будут работать.");
}
if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
  console.warn("⚠️  TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID не заданы — лиды не будут сохраняться.");
}

/* ──────────────────────────────────────────────────────────────────────────
 * RAG: косинусное сходство + поиск по векторной базе.
 * ────────────────────────────────────────────────────────────────────────── */
function cosineSimilarity(vecA, vecB) {
  let dotProduct = 0;
  let mA = 0;
  let mB = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    mA += vecA[i] * vecA[i];
    mB += vecB[i] * vecB[i];
  }
  const norm = Math.sqrt(mA) * Math.sqrt(mB);
  if (norm === 0) return 0;
  return dotProduct / norm;
}

function loadVectorStore() {
  const vectorsPath = path.join(process.cwd(), "knowledge", "processed", "vectors.json");
  if (!fs.existsSync(vectorsPath)) {
    throw new Error(`Vector store not found at ${vectorsPath}`);
  }
  return JSON.parse(fs.readFileSync(vectorsPath, "utf-8"));
}

async function getEmbedding(text) {
  const resp = await fetch("https://openrouter.ai/api/v1/embeddings", {
    method: "POST",
    headers: { Authorization: `Bearer ${OPENROUTER_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: "openai/text-embedding-3-small", input: text }),
  });
  const data = await resp.json();
  if (data.error || !data.data?.[0]?.embedding) {
    const msg = data.error?.message || "неизвестная ошибка embeddings";
    throw new Error(`OpenRouter embeddings: ${msg}`);
  }
  return data.data[0].embedding;
}

function retrieveContext(queryVector, vectorStore, topK = 3) {
  return vectorStore
    .map((item) => ({ text: item.text, score: cosineSimilarity(queryVector, item.vector) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
    .map((item) => item.text)
    .join("\n\n");
}

async function callLLM(messages) {
  const resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: { Authorization: `Bearer ${OPENROUTER_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "google/gemini-pro-1.5",
      messages,
    }),
  });
  const data = await resp.json();
  if (data.error || !data.choices?.[0]?.message?.content) {
    const msg = data.error?.message || "неизвестная ошибка LLM";
    throw new Error(`OpenRouter chat: ${msg}`);
  }
  return data.choices[0].message.content;
}

/* ──────────────────────────────────────────────────────────────────────────
 * Telegram: отправка лида менеджеру.
 * Раньше собранные лиды (тип бизнеса, задача, бюджет, контакт) просто
 * выбрасывались — теперь они уходят в Telegram-канал/чат.
 * ────────────────────────────────────────────────────────────────────────── */
async function sendLeadToTelegram(lead) {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
    console.warn("⚠️  Лид не отправлен: не задан TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID");
    console.log("📋 Лид (не сохранён):", JSON.stringify(lead, null, 2));
    return false;
  }

  const lines = [
    "🎯 <b>Новый лид с сайта AI BUREAU</b>",
    "",
    `🏢 <b>Бизнес:</b> ${escapeHtml(lead.businessType || "—")}`,
    `📝 <b>Задача:</b> ${escapeHtml(lead.task || "—")}`,
    `💰 <b>Бюджет:</b> ${escapeHtml(lead.budget || "—")}`,
    `📞 <b>Контакт:</b> ${escapeHtml(lead.contact || "—")}`,
  ];
  if (lead.summary) {
    lines.push("", `🤖 <b>ИИ-выжимка диалога:</b>\n${escapeHtml(lead.summary)}`);
  }
  lines.push("", `🕐 ${new Date().toLocaleString("ru-RU", { timeZone: "Europe/Moscow" })} (МСК)`);

  const text = lines.join("\n");
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;

  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text,
        parse_mode: "HTML",
        disable_web_page_preview: true,
      }),
    });
    const data = await resp.json();
    if (!data.ok) {
      console.error("❌ Telegram API отклонил сообщение:", data.description);
      return false;
    }
    console.log("✅ Лид отправлен в Telegram");
    return true;
  } catch (e) {
    console.error("❌ Ошибка отправки лида в Telegram:", e.message);
    return false;
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/* ──────────────────────────────────────────────────────────────────────────
 * Простой in-memory rate limiter (защита от спама / abuse).
 * ────────────────────────────────────────────────────────────────────────── */
const requestLog = new Map(); // ip -> [timestamps]
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX = 15;

function isRateLimited(ip) {
  const now = Date.now();
  const hits = (requestLog.get(ip) || []).filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
  if (hits.length >= RATE_LIMIT_MAX) return true;
  hits.push(now);
  requestLog.set(ip, hits);
  return false;
}

/* ──────────────────────────────────────────────────────────────────────────
 * HTTP-сервер
 * ────────────────────────────────────────────────────────────────────────── */
const SYSTEM_PROMPT_BASE =
  "Ты — BureauBot, интеллектуальный помощник AI БЮРО. " +
  "Твой тон: профессиональный, прагматичный, по делу. " +
  "Используй предоставленный КОНТЕКСТ для ответа на вопросы. " +
  "Отвечай кратко (1–3 предложения), если не просят подробностей. " +
  "Если в контексте нет нужной информации — честно скажи, что уточнишь у архитектора, " +
  "не выдумывай детали.";

function buildSystemPrompt(context) {
  return context ? `${SYSTEM_PROMPT_BASE}\n\nКОНТЕКСТ:\n${context}` : SYSTEM_PROMPT_BASE;
}

const server = http.createServer(async (req, res) => {
  // CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  const clientIp = req.socket.remoteAddress || "unknown";

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  // Health-check (полезно для мониторинга).
  if (req.method === "GET" && req.url === "/api/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true }));
    return;
  }

  if (req.method !== "POST" || (req.url !== "/api/chat" && req.url !== "/api/lead")) {
    res.writeHead(404);
    res.end();
    return;
  }

  if (isRateLimited(clientIp)) {
    res.writeHead(429, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ reply: "Слишком много запросов. Подождите минуту." }));
    return;
  }

  let body = "";
  req.on("data", (chunk) => {
    body += chunk;
    // Защита от огромных payload'ов.
    if (body.length > 1e6) req.destroy();
  });
  req.on("end", async () => {
    try {
      const payload = JSON.parse(body);

      /* ── /api/lead: отдельная отправка лида в Telegram ─────────────────── */
      if (req.url === "/api/lead") {
        const { leadData, summary, messages: history } = payload;
        const finalSummary =
          summary || (Array.isArray(history) ? await summarizeHistory(history) : undefined);
        const sent = await sendLeadToTelegram({ ...leadData, summary: finalSummary });
        res.writeHead(sent ? 200 : 502, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: sent }));
        return;
      }

      /* ── /api/chat: основной диалог с RAG + памятью ────────────────────── */
      const { message, context: funnelContext, messages: history } = payload;

      if (!message || typeof message !== "string" || !message.trim()) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ reply: "Пустое сообщение." }));
        return;
      }

      console.log(`💬 [${clientIp}] Вопрос: ${message}`);

      // 1. RAG: ищем релевантный контекст.
      const vectorStore = loadVectorStore();
      const queryVector = await getEmbedding(message);
      const context = retrieveContext(queryVector, vectorStore);

      // 2. История диалога (память). Раньше шёл только последний message.
      const turns = Array.isArray(history) ? history.slice(-10) : [];
      const llmMessages = [
        { role: "system", content: buildSystemPrompt(context) },
        ...turns.map((t) => ({ role: t.role === "bot" ? "assistant" : "user", content: t.text })),
        { role: "user", content: message },
      ];

      const reply = await callLLM(llmMessages);
      console.log(`🤖 Ответ: ${reply.slice(0, 80)}…`);

      // 3. Если воронка завершена — отправляем лид в Telegram.
      if (funnelContext?.stage === "completed" && funnelContext.leadData) {
        sendLeadToTelegram({
          ...funnelContext.leadData,
          summary: await summarizeHistory([...turns, { role: "bot", text: reply }], message),
        }).catch((e) => console.error("Lead send error:", e.message));
      }

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ reply }));
    } catch (e) {
      console.error("Server error:", e);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ reply: "Ошибка нейро-связи. Попробуйте ещё раз." }));
    }
  });
});

/* Генерирует краткую ИИ-выжимку диалога для менеджера. */
async function summarizeHistory(history, lastUserMessage) {
  const turns = history
    .filter((t) => t && t.text)
    .slice(-8)
    .map((t) => `${t.role === "bot" ? "Бот" : "Клиент"}: ${t.text}`)
    .join("\n");
  if (!turns) return undefined;

  try {
    const summary = await callLLM([
      {
        role: "system",
        content:
          "Сделай краткую выжимку (2–4 предложения) сути запроса клиента для менеджера. " +
          "Выдели: чем занимается бизнес, какую задачу хочет решить, какой бюджет. " +
          "Пиши по-русски, без воды.",
      },
      { role: "user", content: `Диалог:\n${turns}\n\nПоследний вопрос клиента: ${lastUserMessage || "—"}` },
    ]);
    return summary;
  } catch (e) {
    console.error("Summarize error:", e.message);
    return undefined;
  }
}

server.listen(PORT, () => {
  console.log(`🚀 AI Bureau RAG-сервер запущен на http://localhost:${PORT}`);
});
