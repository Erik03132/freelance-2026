import fs from "fs";
import path from "path";

/**
 * Интерфейс для элемента векторного хранилища.
 */
interface VectorItem {
  text: string;
  vector: number[];
}

/**
 * Интерфейс для результата поиска.
 */
interface SearchResult {
  text: string;
  score: number;
}

/**
 * Простая функция для расчета косинусного сходства между двумя векторами.
 * Это "сердце" нашего RAG-поиска.
 */
function cosineSimilarity(vecA: number[], vecB: number[]): number {
  let dotProduct = 0;
  let mA = 0;
  let mB = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    mA += vecA[i] * vecA[i];
    mB += vecB[i] * vecB[i];
  }
  mA = Math.sqrt(mA);
  mB = Math.sqrt(mB);
  if (mA === 0 || mB === 0) return 0;
  return dotProduct / (mA * mB);
}

/**
 * Функция поиска релевантных знаний в векторной базе.
 */
export async function searchKnowledge(queryVector: number[], topK = 3): Promise<SearchResult[]> {
  const vectorsPath = path.join(process.cwd(), "knowledge", "processed", "vectors.json");
  
  if (!fs.existsSync(vectorsPath)) {
    throw new Error(`Vector store not found at ${vectorsPath}`);
  }

  let vectorStore: VectorItem[];
  try {
    const rawData = fs.readFileSync(vectorsPath, "utf-8");
    vectorStore = JSON.parse(rawData);
  } catch (error) {
    throw new Error(`Failed to read or parse vector store: ${error instanceof Error ? error.message : String(error)}`);
  }
  
  const results: SearchResult[] = vectorStore.map(item => ({
    text: item.text,
    score: cosineSimilarity(queryVector, item.vector)
  }));

  // Сортируем по релевантности и берем топ-K кусков
  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}
