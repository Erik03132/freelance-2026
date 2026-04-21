import OpenAI from 'openai';
import * as dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

dotenv.config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

/**
 * Основная логика ответов бота с использованием базы знаний (RAG-lite)
 * @param userMessage - текст запроса пользователя
 */
export async function getAIAnswer(userMessage: string): Promise<string> {
  try {
    // 1. Читаем системные промпты (объединяем личность, правила и инструкции)
    const promptsPath = path.join(__dirname, '../knowledge-base/prompts');
    let systemPrompt = '';
    if (fs.existsSync(promptsPath)) {
      const promptFiles = fs.readdirSync(promptsPath);
      for (const file of promptFiles) {
        if (file.endsWith('.md')) {
          systemPrompt += fs.readFileSync(path.join(promptsPath, file), 'utf8') + '\n\n';
        }
      }
    }
    if (!systemPrompt) systemPrompt = 'Вы — эксперт Ульяна по грантам и налогам для IT-бизнеса.';

    // 2. Читаем дополнительные знания (законы, регламенты, кейсы)
    const knowledgeDirs = ['laws', 'manuals', 'cases'];
    let context = '';
    
    for (const dirName of knowledgeDirs) {
      const dirPath = path.join(__dirname, `../knowledge-base/${dirName}`);
      if (fs.existsSync(dirPath)) {
        const files = fs.readdirSync(dirPath);
        for (const file of files) {
          if (file.endsWith('.md')) {
            context += `--- ГРУППА: ${dirName.toUpperCase()} (${file}) ---\n`;
            context += fs.readFileSync(path.join(dirPath, file), 'utf8') + '\n\n';
          }
        }
      }
    }

    // 3. Формируем запрос к GPT
    const response = await openai.chat.completions.create({
      model: 'gpt-4o', 
      messages: [
        { role: 'system', content: `${systemPrompt}\n\nКонтекст (твои знания):\n${context}` },
        { role: 'user', content: userMessage }
      ],
      temperature: 0.7,
    });

    return response.choices[0].message?.content || 'Извините, я не смогла сформировать ответ. Попробуйте уточнить вопрос.';
  } catch (error) {
    console.error('[AI Logic Error]:', error);
    return 'Произошла ошибка при обращении к моему ИИ-центру. Я скоро это исправлю!';
  }
}
