"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.perplexitySearch = perplexitySearch;
exports.generateWithGemini = generateWithGemini;
exports.analyzeFileWithGemini = analyzeFileWithGemini;
const process = __importStar(require("process"));
const generative_ai_1 = require("@google/generative-ai");
/**
 * Исследовательский поиск через Perplexity API
 */
async function perplexitySearch(query) {
    const PERPLEXITY_API_KEY = process.env.PERPLEXITY_API_KEY || '';
    if (!PERPLEXITY_API_KEY) {
        console.warn('⚠️ PERPLEXITY_API_KEY is not set. Deep search features will be limited.');
        return '';
    }
    try {
        const resp = await fetch('https://api.perplexity.ai/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${PERPLEXITY_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'sonar-pro',
                messages: [
                    { role: 'system', content: 'Вы — исследовательский ИИ. Ваша задача — дать точный, детализированный и актуальный ответ с фактами на запрос пользователя, используя доступ в интернет.' },
                    { role: 'user', content: query }
                ]
            })
        });
        if (!resp.ok) {
            const errorText = await resp.text();
            console.warn(`Perplexity HTTP error: ${resp.status} - ${errorText}`);
            return '';
        }
        const data = await resp.json();
        if (data.choices && data.choices[0]) {
            return data.choices[0].message.content;
        }
    }
    catch (error) {
        console.error('Perplexity Search API error:', error);
    }
    return '';
}
/**
 * Генерация контента/кода через Gemini Pro
 */
async function generateWithGemini(prompt, systemPrompt) {
    const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
    if (!GEMINI_API_KEY) {
        console.warn('⚠️ GEMINI_API_KEY is not set.');
        return '';
    }
    try {
        const genAI = new generative_ai_1.GoogleGenerativeAI(GEMINI_API_KEY);
        const model = genAI.getGenerativeModel({
            model: 'gemini-2.0-flash',
            systemInstruction: systemPrompt
        });
        const result = await model.generateContent(prompt);
        const response = await result.response;
        return response.text();
    }
    catch (error) {
        console.error('Gemini API error:', error);
        return '';
    }
}
/**
 * Анализ файла (изображение или PDF) через Gemini
 */
async function analyzeFileWithGemini(buffer, mimeType, prompt) {
    const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
    if (!GEMINI_API_KEY)
        return '';
    try {
        const genAI = new generative_ai_1.GoogleGenerativeAI(GEMINI_API_KEY);
        const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        const result = await model.generateContent([
            prompt,
            {
                inlineData: {
                    data: buffer.toString('base64'),
                    mimeType
                }
            }
        ]);
        return result.response.text();
    }
    catch (error) {
        console.error('Gemini Multimodal API error:', error);
        return '';
    }
}
