"use strict";
/**
 * Специализированные агенты-исполнители
 *
 * Экспорт всех агентов и Router для маршрутизации задач.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AdsSpecialist = exports.ArchitectureAgent = exports.DevOpsAgent = exports.ContentAgent = exports.DataAgent = exports.DesignAgent = exports.BotAgent = exports.WebDevAgent = exports.routeTask = exports.BaseSpecialist = void 0;
exports.getAgent = getAgent;
exports.getAvailableAgents = getAvailableAgents;
// Base
var base_1 = require("./base");
Object.defineProperty(exports, "BaseSpecialist", { enumerable: true, get: function () { return base_1.BaseSpecialist; } });
// Router
var router_1 = require("./router");
Object.defineProperty(exports, "routeTask", { enumerable: true, get: function () { return router_1.routeTask; } });
// Agents
var webdev_1 = require("./webdev");
Object.defineProperty(exports, "WebDevAgent", { enumerable: true, get: function () { return webdev_1.WebDevAgent; } });
var bot_1 = require("./bot");
Object.defineProperty(exports, "BotAgent", { enumerable: true, get: function () { return bot_1.BotAgent; } });
var design_1 = require("./design");
Object.defineProperty(exports, "DesignAgent", { enumerable: true, get: function () { return design_1.DesignAgent; } });
var data_1 = require("./data");
Object.defineProperty(exports, "DataAgent", { enumerable: true, get: function () { return data_1.DataAgent; } });
var content_1 = require("./content");
Object.defineProperty(exports, "ContentAgent", { enumerable: true, get: function () { return content_1.ContentAgent; } });
var devops_1 = require("./devops");
Object.defineProperty(exports, "DevOpsAgent", { enumerable: true, get: function () { return devops_1.DevOpsAgent; } });
var architecture_1 = require("./architecture");
Object.defineProperty(exports, "ArchitectureAgent", { enumerable: true, get: function () { return architecture_1.ArchitectureAgent; } });
var ads_1 = require("./ads");
Object.defineProperty(exports, "AdsSpecialist", { enumerable: true, get: function () { return ads_1.AdsSpecialist; } });
const webdev_2 = require("./webdev");
const bot_2 = require("./bot");
const design_2 = require("./design");
const data_2 = require("./data");
const content_2 = require("./content");
const devops_2 = require("./devops");
const architecture_2 = require("./architecture");
const ads_2 = require("./ads");
const agentRegistry = {
    'webdev': () => new webdev_2.WebDevAgent(),
    'bot': () => new bot_2.BotAgent(),
    'design': () => new design_2.DesignAgent(),
    'data': () => new data_2.DataAgent(),
    'content': () => new content_2.ContentAgent(),
    'devops': () => new devops_2.DevOpsAgent(),
    'architecture': () => new architecture_2.ArchitectureAgent(),
    'ads': () => new ads_2.AdsSpecialist(),
};
/**
 * Получить экземпляр специализированного агента по типу
 */
function getAgent(type) {
    const factory = agentRegistry[type];
    if (!factory) {
        // Fallback на WebDev Agent для неизвестных типов
        console.warn(`Agent type "${type}" not found, falling back to WebDev Agent`);
        return new webdev_2.WebDevAgent();
    }
    return factory();
}
/**
 * Получить список доступных агентов
 */
function getAvailableAgents() {
    return Object.entries(agentRegistry).map(([type, factory]) => {
        const agent = factory();
        return { type, name: agent.agentName, emoji: agent.emoji };
    });
}
