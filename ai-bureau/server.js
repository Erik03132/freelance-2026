import http from "http";
import https from "https";
import fs from "fs";
import path from "path";


const envContent = fs.readFileSync(".env.local", "utf-8");
const env = {};
envContent.split("\n").forEach(line => {
  const [key, value] = line.split("=");
  if (key && value) env[key.trim()] = value.trim();
});

const PORT = 3001;
const OPENROUTER_API_KEY = env.OPENROUTER_API_KEY || "";
const LLM_MODEL = "google/gemini-2.0-flash-001";

const VECTORS_PATH = path.join(process.cwd(), "knowledge", "processed", "vectors.json");
const LEADS_PATH = path.join(process.cwd(), "leads.json");
const TOP_K_INITIAL = 15;
const TOP_K_FINAL = 7;
const FALLBACK_THRESHOLD = 0.65;

function apiPost(url, body, headers, ms = 30000) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const opts = {
      hostname: u.hostname,
      port: 443,
      path: u.pathname + u.search,
      method: "POST",
      headers: { ...headers, "Content-Type": "application/json" },
      timeout: ms
    };
    const req = https.request(opts, (res) => {
      let data = "";
      res.on("data", chunk => { data += chunk; });
      res.on("end", () => {
        try { resolve({ ok: res.statusCode >= 200 && res.statusCode < 300, status: res.statusCode, json: () => JSON.parse(data), text: () => data }); }
        catch { reject(new Error("Invalid JSON: " + data.slice(0, 200))); }
      });
    });
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(); reject(new Error("Request timeout")); });
    req.write(JSON.stringify(body));
    req.end();
  });
}

async function withRetry(fn, retries = 2) {
  for (let i = 0; i <= retries; i++) {
    try { return await fn(); }
    catch (e) {
      if (i === retries) throw e;
      console.log(`  Retry ${i + 1}/${retries}: ${e.message}`);
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}

function cosineSimilarity(vecA, vecB) {
  let dotProduct = 0, mA = 0, mB = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    mA += vecA[i] * vecA[i];
    mB += vecB[i] * vecB[i];
  }
  const normA = Math.sqrt(mA), normB = Math.sqrt(mB);
  return normA === 0 || normB === 0 ? 0 : dotProduct / (normA * normB);
}

function keywordOverlap(query, text) {
  const words = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);
  if (words.length === 0) return 0;
  const textLower = text.toLowerCase();
  let matches = 0;
  for (const w of words) {
    if (textLower.includes(w)) matches++;
  }
  return matches / words.length;
}

function rerankChunks(query, chunks) {
  return chunks.map(c => {
    const semantic = c.score;
    const keyword = keywordOverlap(query, c.text);
    c.hybridScore = 0.7 * semantic + 0.3 * keyword;
    return c;
  }).sort((a, b) => b.hybridScore - a.hybridScore);
}

async function getEmbedding(text) {
  return withRetry(async () => {
    const resp = await apiPost("https://openrouter.ai/api/v1/embeddings",
      { model: "openai/text-embedding-3-small", input: text },
      { "Authorization": `Bearer ${OPENROUTER_API_KEY}` }
    );
    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Embedding error ${resp.status}: ${err}`);
    }
    const data = await resp.json();
    return data.data[0].embedding;
  });
}

function loadVectors() {
  return JSON.parse(fs.readFileSync(VECTORS_PATH, "utf-8"));
}

async function retrieveContext(query, queryVector) {
  const store = loadVectors();

  const scored = store.map(item => ({
    text: item.text,
    source: item.source,
    score: cosineSimilarity(queryVector, item.vector)
  }));

  const topN = scored.sort((a, b) => b.score - a.score).slice(0, TOP_K_INITIAL);
  const reranked = rerankChunks(query, topN);
  const final = reranked.slice(0, TOP_K_FINAL);

  const maxScore = final.length > 0 ? final[0].hybridScore : 0;

  return {
    context: final.map(c => c.text).join("\n\n"),
    sources: final.map(c => c.source).filter((v, i, a) => a.indexOf(v) === i),
    maxScore
  };
}

function getStageSystemPrompt(stage, leadData) {
  const base = "Ты — BureauBot, интеллектуальный помощник AI БЮРО. Твой тон: профессиональный, прагматичный, дружелюбный. Отвечай кратко (2-4 предложения).";

  switch (stage) {
    case "greeting":
      return `${base}
Ты начинаешь диалог с посетителем сайта AI Bureau.
Поприветствуй и спроси, какой у него бизнес или сфера деятельности.
Используй КОНТЕКСТ, чтобы упомянуть релевантные услуги или кейсы бюро.`;

    case "business_type":
      return `${base}
Клиент назвал свой бизнес или сферу: "${leadData.businessType || "не указано"}".
Покажи, что ты понял, и спроси, какую задачу он хочет решить с помощью ИИ.
Постарайся связать его сферу с возможностями AI Bureau из КОНТЕКСТА.`;

    case "task_description":
      return `${base}
Клиент описал задачу: "${leadData.task || "не указано"}".
Подтверди, что задача понятна, и спроси про бюджет.
Постарайся дать короткую релевантную рекомендацию на основе КОНТЕКСТА.`;

    case "budget":
      return `${base}
Клиент назвал бюджет: "${leadData.budget || "не указано"}".
Поблагодари и попроси контакт (Telegram или Email) для связи архитектора.
Заверь, что предложение будет готово в течение 30 минут.`;

    case "contact_collection":
      return `${base}
Клиент оставил контакт: "${leadData.contact || "не указано"}".
Поблагодари, сообщи что данные переданы архитектору, и попрощайся.
Не задавай больше вопросов.`;

    case "completed":
      return `${base}
Диалог завершён. Поблагодари клиента и сообщи, что с ним свяжутся в ближайшее время.`;

    default:
      return base;
  }
}

function saveLead(leadData) {
  const entry = { ...leadData, timestamp: new Date().toISOString() };
  let leads = [];
  try {
    if (fs.existsSync(LEADS_PATH)) leads = JSON.parse(fs.readFileSync(LEADS_PATH, "utf-8"));
  } catch { }
  leads.push(entry);
  fs.writeFileSync(LEADS_PATH, JSON.stringify(leads, null, 2));
  console.log(`📝 Lead saved: ${JSON.stringify(entry)}`);
}

async function callLLM(messages) {
  return withRetry(async () => {
    const resp = await apiPost("https://openrouter.ai/api/v1/chat/completions",
      { model: LLM_MODEL, messages },
      { "Authorization": `Bearer ${OPENROUTER_API_KEY}` }
    );
    const data = await resp.json();
    if (!resp.ok || !data.choices?.[0]?.message?.content) {
      console.error("LLM error:", JSON.stringify(data).slice(0, 500));
      return null;
    }
    return data.choices[0].message.content;
  });
}

const server = http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === "POST" && req.url === "/api/chat") {
    let body = "";
    req.on("data", chunk => { body += chunk; });
    req.on("end", async () => {
      try {
        const { message, context: clientCtx } = JSON.parse(body);
        const stage = clientCtx?.stage || "greeting";
        const leadData = clientCtx?.leadData || {};
        console.log(`💬 [${stage}] ${message}`);

        const queryVector = await getEmbedding(message);
        const rag = await retrieveContext(message, queryVector);

        const SYSTEM_PROMPT = `${getStageSystemPrompt(stage, leadData)}

КОНТЕКСТ (знания AI Bureau):
${rag.context || "Общие знания о AI Bureau."}`;

        let reply = await callLLM([
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: message }
        ]);

        if (!reply) reply = "Извините, нейро-сеть временно недоступна. Попробуйте позже.";

        if (stage === "completed" || stage === "contact_collection") saveLead(leadData);

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ reply }));
      } catch (e) {
        console.error(e);
        if (!res.headersSent) {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ reply: "Ошибка нейро-связи. Попробуйте еще раз." }));
        }
      }
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(PORT, () => {
  console.log(`🚀 Zero-Dep RAG Server запущен на http://localhost:${PORT}`);
});
