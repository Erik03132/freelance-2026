import http from "http";
import fs from "fs";
import path from "path";

// Загружаем .env.local вручную
const envContent = fs.readFileSync(".env.local", "utf-8");
const env = {};
envContent.split("\n").forEach(line => {
  const [key, value] = line.split("=");
  if (key && value) env[key.trim()] = value.trim();
});

const PORT = 3001;
const OPENROUTER_API_KEY = env.OPENROUTER_API_KEY || "";

function cosineSimilarity(vecA, vecB) {
  let dotProduct = 0; let mA = 0; let mB = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    mA += vecA[i] * vecA[i];
    mB += vecB[i] * vecB[i];
  }
  return dotProduct / (Math.sqrt(mA) * Math.sqrt(mB));
}

async function getEmbedding(text) {
  const resp = await fetch("https://openrouter.ai/api/v1/embeddings", {
    method: "POST",
    headers: { "Authorization": `Bearer ${OPENROUTER_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: "openai/text-embedding-3-small", input: text })
  });
  const data = await resp.json();
  return data.data[0].embedding;
}

const server = http.createServer(async (req, res) => {
  // CORS Headers
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
        const { message } = JSON.parse(body);
        console.log(`💬 Вопрос: ${message}`);

        const queryVector = await getEmbedding(message);
        const vectorsPath = path.join(process.cwd(), "knowledge", "processed", "vectors.json");
        const vectorStore = JSON.parse(fs.readFileSync(vectorsPath, "utf-8"));
        
        const context = vectorStore
          .map(item => ({ text: item.text, score: cosineSimilarity(queryVector, item.vector) }))
          .sort((a,b) => b.score - a.score)
          .slice(0, 3)
          .map(item => item.text)
          .join("\n\n");

        const llmResp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: { "Authorization": `Bearer ${OPENROUTER_API_KEY}`, "Content-Type": "application/json" },
          body: JSON.stringify({
            model: "google/gemini-pro-1.5",
            messages: [
              { role: "system", content: "Ты — BureauBot, интеллектуальный помощник AI БЮРО. Твой тон: профессиональный, прагматичный. Используй предоставленный КОНТЕКСТ для ответа на вопросы. Если в контексте нет инфы, отвечай вежливо на основе общих знаний о бюро, но делай акцент на том, что ты агент AI БЮРО.\n\nКОНТЕКСТ:\n" + context },
              { role: "user", content: message }
            ]
          })
        });

        const llmData = await llmResp.json();
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ reply: llmData.choices[0].message.content }));
      } catch (e) {
        console.error(e);
        res.writeHead(500);
        res.end(JSON.stringify({ reply: "Ошибка нейро-связи. Попробуйте еще раз." }));
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
