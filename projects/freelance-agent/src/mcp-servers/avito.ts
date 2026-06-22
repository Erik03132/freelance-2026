import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import * as dotenv from "dotenv";
import axios from "axios";

dotenv.config();

const AVITO_CLIENT_ID = process.env.AVITO_CLIENT_ID;
const AVITO_CLIENT_SECRET = process.env.AVITO_CLIENT_SECRET;

class AvitoMcpServer {
  private server: Server;
  private token: string | null = null;

  constructor() {
    this.server = new Server(
      { name: "avito-mcp", version: "1.0.0" },
      { capabilities: { tools: {} } }
    );
    this.setupHandlers();
  }

  // Авторизация и получение токена
  private async getAuthToken(): Promise<string> {
    if (this.token) return this.token; // Простейшее кэширование (в бою нужно проверять срок действия)
    
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
      return this.token!;
    } catch (error: any) {
      throw new McpError(ErrorCode.InternalError, `Avito Auth Error: ${error.message}`);
    }
  }

  // Обёртка для API запросов Авито
  private async callAvito(method: "GET" | "POST", endpoint: string, data?: any) {
    const token = await this.getAuthToken();
    try {
      const response = await axios({
        method,
        url: `https://api.avito.ru${endpoint}`,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        data,
      });
      return response.data;
    } catch (error: any) {
      console.error(`Avito API Error (${endpoint}):`, error.response?.data || error.message);
      throw new McpError(ErrorCode.InternalError, `Avito API error: ${error.message}`);
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
        if (name === "get_chats") {
          // Заглушка до получения реального user_id
          // const data = await this.callAvito("GET", `/messenger/v3/accounts/{user_id}/chats?limit=${args?.limit}`);
          return { content: [{ type: "text", text: JSON.stringify({ status: "success", data: "Здесь будет список чатов" }) }] };
        } 
        
        else if (name === "get_messages") {
          // const data = await this.callAvito("GET", `/messenger/v3/accounts/{user_id}/chats/${args?.chat_id}/messages`);
          return { content: [{ type: "text", text: JSON.stringify({ status: "success", data: `Сообщения чата ${args?.chat_id}` }) }] };
        }
        
        else if (name === "send_message") {
          // const data = await this.callAvito("POST", `/messenger/v1/accounts/{user_id}/chats/${args?.chat_id}/messages`, { message: { text: args?.text }});
          return { content: [{ type: "text", text: `Отправлено в Авито: ${args?.text}` }] };
        }
        
        else if (name === "get_items") {
          // const data = await this.callAvito("GET", `/core/v1/items`);
          return { content: [{ type: "text", text: JSON.stringify({ status: "success", data: "Список активных объявлений Авито" }) }] };
        }
        
        else if (name === "create_item") {
          // Логика автопостинга объявлений
          return { content: [{ type: "text", text: `Объявление создано: ${args?.title}` }] };
        }

        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
      } catch (error: any) {
        return { content: [{ type: "text", text: `Ошибка инструмента: ${error.message}` }], isError: true };
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
