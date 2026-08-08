import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import * as dotenv from "dotenv";
import axios, { AxiosError } from "axios";
import * as crypto from "crypto";

dotenv.config();

const AVITO_CLIENT_ID = process.env.AVITO_CLIENT_ID;
const AVITO_CLIENT_SECRET = process.env.AVITO_CLIENT_SECRET;
const AVITO_USER_ID = process.env.AVITO_USER_ID || process.env.AVITO_ACCOUNT_ID;
const PROXY_URL = process.env.HTTP_PROXY || process.env.HTTPS_PROXY;
const MAX_PROXY_ROTATIONS = 3;
const MAX_SESSION_ROTATIONS = 2;

interface EnvironmentState {
  proxyIndex: number;
  sessionRotations: number;
  lastError: string | null;
}

class AvitoMcpServer {
  private server: Server;
  private token: string | null = null;
  private tokenExpiry: number = 0;
  private envState: EnvironmentState = { proxyIndex: 0, sessionRotations: 0, lastError: null };

  constructor() {
    this.server = new Server(
      { name: "avito-mcp", version: "1.1.0" },
      { capabilities: { tools: {} } }
    );
    this.setupHandlers();
  }

  private async getAuthToken(): Promise<string> {
    if (this.token && Date.now() < this.tokenExpiry) return this.token;

    if (!AVITO_CLIENT_ID || !AVITO_CLIENT_SECRET) {
      throw new Error("AVITO_CLIENT_ID and AVITO_CLIENT_SECRET required in .env");
    }

    try {
      const response = await axios.post("https://api.avito.ru/token/", {
        grant_type: "client_credentials",
        client_id: AVITO_CLIENT_ID,
        client_secret: AVITO_CLIENT_SECRET,
      });
      this.token = response.data.access_token;
      this.tokenExpiry = Date.now() + ((response.data.expires_in || 86400) - 300) * 1000;
      return this.token!;
    } catch (error: any) {
      throw new McpError(ErrorCode.InternalError, `Avito Auth Error: ${error.message}`);
    }
  }

  // При 403: сначала меняем окружение (прокси → сессия), НЕ селекторы
  private async resolve403Environment(): Promise<boolean> {
    this.envState.lastError = "403";

    if (PROXY_URL && this.envState.proxyIndex < MAX_PROXY_ROTATIONS) {
      this.envState.proxyIndex++;
      console.error(`[avito] 403: rotating proxy (attempt ${this.envState.proxyIndex}/${MAX_PROXY_ROTATIONS})`);
      return true;
    }

    if (this.envState.sessionRotations < MAX_SESSION_ROTATIONS) {
      this.envState.sessionRotations++;
      this.token = null;
      this.tokenExpiry = 0;
      this.envState.proxyIndex = 0;
      console.error(`[avito] 403: rotating session (attempt ${this.envState.sessionRotations}/${MAX_SESSION_ROTATIONS})`);
      return true;
    }

    console.error("[avito] 403: environment rotations exhausted — NOT trying different selectors");
    return false;
  }

  private resetEnvironment(): void {
    this.envState = { proxyIndex: 0, sessionRotations: 0, lastError: null };
  }

  private async callAvito(method: "GET" | "POST", endpoint: string, data?: any, retryCount: number = 0): Promise<any> {
    const token = await this.getAuthToken();
    const maxRetries = MAX_PROXY_ROTATIONS + MAX_SESSION_ROTATIONS + 1;

    let effectiveEndpoint = endpoint;
    if (AVITO_USER_ID) {
      effectiveEndpoint = effectiveEndpoint.replace("{user_id}", AVITO_USER_ID);
    }

    const requestConfig: any = {
      method,
      url: `https://api.avito.ru${effectiveEndpoint}`,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      data,
    };

    if (this.envState.proxyIndex > 0 && PROXY_URL) {
      requestConfig.proxy = {
        protocol: "http",
        host: new URL(PROXY_URL).hostname,
        port: parseInt(new URL(PROXY_URL).port) || 8080,
      };
    }

    try {
      const response = await axios(requestConfig);
      if (retryCount > 0) {
        console.error(`[avito] ${effectiveEndpoint}: recovered after ${retryCount} environment rotations`);
      }
      return response.data;
    } catch (error: any) {
      const axiosError = error as AxiosError;
      const status = axiosError.response?.status || 0;
      const message = axiosError.message || "unknown";

      // 403 — проблема окружения, не селектора
      if (status === 403 || status === 429) {
        console.error(`[avito] ${status} on ${effectiveEndpoint}: environment issue, not selector`);
        if (retryCount < maxRetries && this.resolve403Environment()) {
          return this.callAvito(method, endpoint, data, retryCount + 1);
        }
      }

      // 5xx — retryable
      if (status >= 500 && retryCount < 2) {
        console.error(`[avito] ${status} on ${effectiveEndpoint}: retryable, attempt ${retryCount + 1}`);
        return this.callAvito(method, endpoint, data, retryCount + 1);
      }

      console.error(`Avito API Error (${effectiveEndpoint}):`, axiosError.response?.data || message);
      throw new McpError(
        ErrorCode.InternalError,
        `Avito API ${status ? `(${status}) ` : ""}on ${effectiveEndpoint}: ${message}`
      );
    }
  }

  private setupHandlers() {
    // 1. Регистрация доступных инструментов
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "get_chats",
          description: "Получить список активных чатов из Авито (мониторинг)",
          inputSchema: {
            type: "object",
            properties: {
              limit: { type: "number", description: "Количество чатов", default: 10 }
            }
          }
        },
        {
          name: "get_messages",
          description: "Получить последние сообщения из конкретного чата (аудит/чтение)",
          inputSchema: {
            type: "object",
            properties: {
              chat_id: { type: "string", description: "ID чата Авито" },
              limit: { type: "number", description: "Количество сообщений", default: 20 }
            },
            required: ["chat_id"]
          }
        },
        {
          name: "send_message",
          description: "Отправить сообщение клиенту в чат Авито",
          inputSchema: {
            type: "object",
            properties: {
              chat_id: { type: "string", description: "ID чата" },
              text: { type: "string", description: "Текст сообщения" }
            },
            required: ["chat_id", "text"]
          }
        },
        {
          name: "get_items",
          description: "Получить список объявлений аккаунта (для аудита и рекомендаций)",
          inputSchema: {
            type: "object",
            properties: {
              status: { type: "string", description: "Статус (active, old, etc)" }
            }
          }
        },
        {
          name: "create_item",
          description: "Создать новое объявление (только для аккаунта нового Битрикса!)",
          inputSchema: {
            type: "object",
            properties: {
              title: { type: "string", description: "Заголовок объявления" },
              description: { type: "string", description: "Текст объявления" },
              price: { type: "number", description: "Цена" }
            },
            required: ["title", "description", "price"]
          }
        }
      ]
    }));

    // 2. Обработка вызовов инструментов
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        this.resetEnvironment();

        if (name === "get_chats") {
          if (AVITO_USER_ID) {
            const data = await this.callAvito("GET", `/messenger/v3/accounts/{user_id}/chats?limit=${args?.limit || 10}`);
            return { content: [{ type: "text", text: JSON.stringify(data) }] };
          }
          return { content: [{ type: "text", text: JSON.stringify({ status: "no_user_id", message: "AVITO_USER_ID not set" }) }] };
        }

        else if (name === "get_messages") {
          if (AVITO_USER_ID) {
            const data = await this.callAvito("GET", `/messenger/v3/accounts/{user_id}/chats/${args?.chat_id}/messages?limit=${args?.limit || 20}`);
            return { content: [{ type: "text", text: JSON.stringify(data) }] };
          }
          return { content: [{ type: "text", text: JSON.stringify({ status: "no_user_id", message: "AVITO_USER_ID not set" }) }] };
        }

        else if (name === "send_message") {
          if (AVITO_USER_ID) {
            const data = await this.callAvito("POST", `/messenger/v1/accounts/{user_id}/chats/${args?.chat_id}/messages`, { message: { text: args?.text }});
            return { content: [{ type: "text", text: JSON.stringify(data) }] };
          }
          return { content: [{ type: "text", text: `[NO USER ID] Would send to chat ${args?.chat_id}: ${args?.text}` }] };
        }

        else if (name === "get_items") {
          const data = await this.callAvito("GET", `/core/v1/items?status=${args?.status || "active"}`);
          return { content: [{ type: "text", text: JSON.stringify(data) }] };
        }

        else if (name === "create_item") {
          const data = await this.callAvito("POST", "/core/v1/items", {
            title: args?.title,
            description: args?.description,
            price: args?.price,
          });
          return { content: [{ type: "text", text: JSON.stringify(data) }] };
        }

        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
      } catch (error: any) {
        const status = error.message?.match(/\((\d+)\)/)?.[1] || "unknown";
        return {
          content: [{ type: "text", text: `Error (${status}): ${error.message}` }],
          isError: true
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("🚀 Avito MCP Server running on stdio");
  }
}

const server = new AvitoMcpServer();
server.run().catch(console.error);
