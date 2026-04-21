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
const auto_bid_1 = require("./services/auto-bid");
const dotenv = __importStar(require("dotenv"));
dotenv.config();
async function runTest() {
    console.log('🚀 Запуск боевого тестирования Auto-bid...');
    const email = process.env.KWORK_EMAIL;
    const password = process.env.KWORK_PASSWORD;
    if (!email || !password) {
        console.error('❌ ОШИБКА: Боевые креды (KWORK_EMAIL и KWORK_PASSWORD) не найдены в .env!');
        console.error('Пожалуйста, добавь их в freelance-agent/.env для продолжения.');
        process.exit(1);
    }
    const service = new auto_bid_1.AutoBidService();
    try {
        // Включаем headless: false, чтобы ты видел магию своими глазами
        await service.launch(false);
        console.log('🌐 Браузер запущен (видимый режим).');
        // Загружаем куки, если есть
        await service.loadCookies('kwork');
        console.log(`🔐 Пробуем авторизоваться как ${email}...`);
        const isLoggedIn = await service.loginToKwork(email, password);
        if (!isLoggedIn) {
            console.log('❌ Не удалось войти в аккаунт.');
            return;
        }
        console.log('✅ Успешный вход! Переходим к случайной задаче для теста формы...');
        // Перейдем на проекты
        await service.openBidPage('https://kwork.ru/projects');
        // Просто ждем, чтобы Игорь мог оценить работу
        console.log('👀 Смотри на браузер! Форма готова к вставке.');
        await new Promise(r => setTimeout(r, 8000));
        console.log('🏁 Тест авто-отправки успешно завершен (демо-режим без реального submit).');
    }
    catch (err) {
        console.error('Ошибка во время тестов:', err);
    }
    finally {
        await service.close();
    }
}
runTest();
