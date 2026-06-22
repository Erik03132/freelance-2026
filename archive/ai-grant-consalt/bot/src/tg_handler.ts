import { Telegraf } from 'telegraf';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { transcribeVoice } from './whisper';
import { getAIAnswer } from './ai_logic';

/**
 * Инициализация обработчиков для Telegram
 * @param bot - инстанс Telegraf
 */
export function setupTelegramHandlers(bot: Telegraf) {
  // Обработка голосовых сообщений
  bot.on('voice', async (ctx) => {
    try {
      const voice = ctx.message.voice;
      const fileId = voice.file_id;
      
      const link = await ctx.telegram.getFileLink(fileId);
      const audioDir = path.join(__dirname, '../audio_tmp');
      if (!fs.existsSync(audioDir)) fs.mkdirSync(audioDir);
      
      const tempPath = path.join(audioDir, `${fileId}.ogg`);

      const response = await axios({
        method: 'GET',
        url: link.href,
        responseType: 'stream'
      });

      const writer = fs.createWriteStream(tempPath);
      response.data.pipe(writer);

      ctx.sendChatAction('typing');

      writer.on('finish', async () => {
        // 1. Транскрибация голоса
        const text = await transcribeVoice(tempPath);
        
        // 2. Получение ИИ-ответа
        const answer = await getAIAnswer(text);
        
        // 3. Отправляем ответ
        ctx.reply(answer);
        
        // Удаляем временный файл
        if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
      });

    } catch (error) {
      console.error('[TG Voice Handler Error]:', error);
      ctx.reply('Не удалось обработать голосовое сообщение.');
    }
  });

  // Обработка текстовых сообщений
  bot.on('text', async (ctx) => {
    if (ctx.message.text.startsWith('/')) return; // Игнорируем команды здесь
    
    try {
      ctx.sendChatAction('typing');
      const answer = await getAIAnswer(ctx.message.text);
      ctx.reply(answer);
    } catch (error) {
      console.error('[TG Text Handler Error]:', error);
      ctx.reply('Хьюстон, у нас проблемы с ИИ-мозгом.');
    }
  });

  // Базовая команда старт
  bot.start((ctx) => {
    ctx.reply('Здравствуйте! Я — Ульяна, ваш эксперт по грантам и IT-налогам. Присылайте ваши вопросы текстом или голосом, и мы разберемся в вашей ситуации.');
  });
}
