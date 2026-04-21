const { GoogleGenerativeAI } = require("@google/generative-ai");
const fs = require("fs");
const path = require("path");
require("dotenv").config({ path: ".env.local" });

const API_KEY = process.env.GEMINI_API_KEY || "";
const genAI = new GoogleGenerativeAI(API_KEY);
const embeddingModel = genAI.getGenerativeModel({ model: "text-embedding-004" });

async function run() {
  console.log("🚀 Запуск индексации (Pure JS version)...");

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
      const result = await embeddingModel.embedContent(chunk);
      const embedding = result.embedding.values;
      
      vectorStore.push({
        text: chunk,
        vector: embedding
      });
    } catch (error) {
      console.error("⚠️ Ошибка при создании эмбеддинга:", error);
    }
  }

  fs.writeFileSync(processedPath, JSON.stringify(vectorStore, null, 2));
  console.log("✅ Векторная база готова: knowledge/processed/vectors.json");
}

run();
