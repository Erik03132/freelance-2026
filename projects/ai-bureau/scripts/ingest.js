import fs from "fs";
import path from "path";
import dotenv from "dotenv";

dotenv.config({ path: ".env.local" });

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || "";

async function getEmbedding(text) {
  const response = await fetch("https://openrouter.ai/api/v1/embeddings", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "openai/text-embedding-3-small",
      input: text
    })
  });

  const data = await response.json();
  if (data.error) {
    throw new Error(data.error.message);
  }
  return data.data[0].embedding;
}

async function run() {
  console.log("🚀 Запуск индексации через OpenRouter (Guaranteed Flow)...");

  const rawFilePath = path.join("knowledge", "raw", "manual.txt");
  const processedPath = path.join("knowledge", "processed", "vectors.json");

  if (!fs.existsSync(rawFilePath)) {
    console.error("❌ Файл знаний не найден!");
    return;
  }

  const content = fs.readFileSync(rawFilePath, "utf-8");
  const chunks = content.split("\n\n").filter(c => c.trim().length > 0);
  console.log(`📦 Найдено чанков: ${chunks.length}`);

  const vectorStore = [];

  for (const chunk of chunks) {
    console.log(`🧠 Создаю эмбеддинг для: ${chunk.substring(0, 50).replace(/\n/g, " ")}...`);
    
    try {
      const embedding = await getEmbedding(chunk);
      vectorStore.push({
        text: chunk,
        vector: embedding
      });
    } catch (error) {
      console.error("⚠️ Ошибка при создании эмбеддинга:", error.message);
    }
  }

  const processedDir = path.dirname(processedPath);
  if (!fs.existsSync(processedDir)) fs.mkdirSync(processedDir, { recursive: true });

  fs.writeFileSync(processedPath, JSON.stringify(vectorStore, null, 2));
  console.log("✅ Векторная база ГОТОВА! Путь: knowledge/processed/vectors.json");
}

run().catch(console.error);
