import fs from "fs";
import path from "path";

const __filename = new URL(import.meta.url).pathname;
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");

const envContent = fs.readFileSync(path.join(projectRoot, ".env.local"), "utf-8");
const env = {};
envContent.split("\n").forEach(line => {
  const [key, value] = line.split("=");
  if (key && value) env[key.trim()] = value.trim();
});

const OPENROUTER_KEY = env.OPENROUTER_API_KEY || "";

async function getEmbedding(text) {
  const resp = await fetch("https://openrouter.ai/api/v1/embeddings", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENROUTER_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "openai/text-embedding-3-small",
      input: text.slice(0, 8000)
    })
  });
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`OpenRouter embedding ${resp.status}: ${err}`);
  }
  const data = await resp.json();
  return data.data[0].embedding;
}

function chunkByHeadings(content, source) {
  const lines = content.split("\n");
  const chunks = [];
  let buffer = [];
  let heading = "";

  for (const line of lines) {
    if (/^#{1,3}\s/.test(line)) {
      if (buffer.length > 0) {
        chunks.push({
          text: `[${source}] ${heading}\n${buffer.join("\n").trim()}`
        });
      }
      heading = line.replace(/^#+\s*/, "").trim();
      buffer = [line];
    } else {
      buffer.push(line);
    }
  }

  if (buffer.length > 0) {
    chunks.push({
      text: `[${source}] ${heading}\n${buffer.join("\n").trim()}`
    });
  }

  return chunks;
}

const files = [
  { file: path.join(projectRoot, "..", "MASTER_BACKLOG.md"), source: "Backlog" },
  { file: path.join(projectRoot, "..", "STRATEGY_2026.md"), source: "Strategy 2026" },
  { file: path.join(projectRoot, "..", "AGENT_SYSTEM_PROMPT.md"), source: "Agent System Prompt" },
  { file: path.join(projectRoot, "..", "AGENT_SKILL_ROADMAP.md"), source: "Agent Skill Roadmap" },
  { file: path.join(projectRoot, "..", "ACTIVE_TASKS.md"), source: "Active Tasks" },
  { file: path.join(projectRoot, "..", "GEMINI.md"), source: "Gemini Rules" },
  { file: path.join(projectRoot, "..", "DOOMSDAY_PROTOCOL.md"), source: "Doomsday Protocol" },
  { file: path.join(projectRoot, "..", "llms.txt"), source: "Incubird LLMS" },
  { file: path.join(projectRoot, "MARKETING_ROADMAP.md"), source: "AI Bureau Marketing" },
  { file: path.join(projectRoot, "SCOUTING_REPORT.md"), source: "AI Bureau Scouting" },
  { file: path.join(projectRoot, "SMART_FALLBACK_STANDARD.md"), source: "Smart Fallback" },
  { file: path.join(projectRoot, "TAX_REPORTING_ARCHITECTURE.md"), source: "Tax Architecture" },
  { file: path.join(projectRoot, "WEBSITE_COPY.md"), source: "Website Copy" },
  { file: path.join(projectRoot, "knowledge", "raw", "manual.txt"), source: "Bureau Manual" },
  { file: path.join(projectRoot, "..", "ai-eggs", "PROJECT.md"), source: "AI Eggs Project" },
  { file: path.join(projectRoot, "..", "ai-eggs", "AGENT_PROFILES.md"), source: "AI Eggs Agents" },
  { file: path.join(projectRoot, "..", "ai-grant-consalt", "ARCHITECTURE.md"), source: "Grant Consult" },
  { file: path.join(projectRoot, "..", "ai-grant-consalt", "CORE_ENGINE_LOGIC.md"), source: "Grant Engine" },
  { file: path.join(projectRoot, "..", "ai-senat", "PROJECT_SPEC.md"), source: "AI Senat" },
  { file: path.join(projectRoot, "..", "agent-lab", "README.md"), source: "Agent Lab" },
  { file: path.join(projectRoot, "..", "antigravity-brain", "README.md"), source: "Antigravity Brain" },
  { file: path.join(projectRoot, "..", "svo-start", "README.md"), source: "SVO Start" },
];

async function main() {
  const allChunks = [];

  for (const { file, source } of files) {
    try {
      const content = fs.readFileSync(file, "utf-8");
      const chunks = chunkByHeadings(content, source);
      allChunks.push(...chunks.map(c => ({ ...c, source })));
      console.log(`✅ ${source}: ${chunks.length} chunks`);
    } catch (e) {
      console.log(`❌ ${source}: ${e.message}`);
    }
  }

  console.log(`\n📦 Всего чанков: ${allChunks.length}`);
  console.log("⏳ Генерирую эмбеддинги...\n");

  const vectors = [];
  for (let i = 0; i < allChunks.length; i++) {
    try {
      const vector = await getEmbedding(allChunks[i].text);
      vectors.push({
        text: allChunks[i].text,
        source: allChunks[i].source,
        vector
      });
      const preview = allChunks[i].text.replace(/\n/g, " ").slice(0, 70);
      console.log(`  [${i + 1}/${allChunks.length}] ✅ ${preview}...`);
    } catch (e) {
      console.log(`  [${i + 1}/${allChunks.length}] ❌ ${e.message}`);
    }
  }

  const outPath = path.join(projectRoot, "knowledge", "processed", "vectors.json");
  fs.writeFileSync(outPath, JSON.stringify(vectors, null, 2));
  console.log(`\n💾 Сохранено ${vectors.length} векторов в ${outPath}`);
}

main().catch(console.error);
