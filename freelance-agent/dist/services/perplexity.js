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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.perplexitySearch = perplexitySearch;
const dotenv = __importStar(require("dotenv"));
const path_1 = __importDefault(require("path"));
// Загружаем глобальный .env если он есть (чуть выше по иерархии или в текущей папке)
dotenv.config();
dotenv.config({ path: path_1.default.join(__dirname, '../../.env') });
const PERPLEXITY_API_KEY = process.env.PERPLEXITY_API_KEY || '';
/**
 * Perform a deep web research search using Perplexity API (Sonar model)
 * Useful for the "Scout" agent (Шерлок) to gather real-time facts from the web.
 */
async function perplexitySearch(query) {
    if (!PERPLEXITY_API_KEY) {
        return '❌ Perplexity API Key is not set in .env';
    }
    try {
        const resp = await fetch('https://api.perplexity.ai/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${PERPLEXITY_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'sonar-reasoning', // Оптимальная модель для глубокого анализа
                messages: [
                    { role: 'system', content: 'Вы — элитный фриланс-аналитик Шерлок. Ваша задача — дать точный, детализированный и актуальный ответ с фактами на запрос пользователя, используя доступ в интернет. Дайте самую свежую информацию (практики 2025-2026).' },
                    { role: 'user', content: query }
                ]
            })
        });
        if (!resp.ok) {
            throw new Error(`HTTP error! status: ${resp.status}`);
        }
        const data = (await resp.json());
        if (data.choices && data.choices[0]) {
            return data.choices[0].message.content;
        }
        return `❌ Ошибка парсинга ответа от Perplexity.`;
    }
    catch (error) {
        return `❌ Ошибка выполнения запроса к Perplexity: ${error.message}`;
    }
}
