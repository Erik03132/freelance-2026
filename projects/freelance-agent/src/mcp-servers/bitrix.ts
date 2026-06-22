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

// Загружаем ключи из .env (нужен BITRIX_WEBHOOK_URL)
dotenv.config();

const BITRIX_WEBHOOK_URL = process.env.BITRIX_WEBHOOK_URL;
if (!BITRIX_WEBHOOK_URL) {
  console.error("FATAL: BITRIX_WEBHOOK_URL is not defined in .env");
  process.exit(1);
}

class BitrixMcpServer {
  private server: Server;
  private baseUrl: string;

  constructor() {
    this.baseUrl = BITRIX_WEBHOOK_URL.replace(/\/$/, "");
    this.server = new Server(
      { name: "bitrix-mcp", version: "1.0.0" },
      { capabilities: { tools: {} } }
    );
    this.setupHandlers();
  }

  private async callBitrix(method: string, params: any = {}) {
    try {
      const url = `${this.baseUrl}/${method}`;
      const response = await axios.post(url, params);
      return response.data;
    } catch (error: any) {
      console.error(`Bitrix API Error (${method}):`, error.response?.data || error.message);
      throw new McpError(ErrorCode.InternalError, `Bitrix API error: ${error.message}`);
    }
  }

  private setupHandlers() {
    // 1. Регистрация доступных инструментов
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "get_deals",
          description: "Получить последние сделки из Битрикс24",
          inputSchema: {
            type: "object",
            properties: {
              status: { type: "string", description: "ID стадии воронки (STAGE_ID)" },
              limit: { type: "number", description: "Количество записей", default: 50 }
            }
          }
        },
        {
          name: "create_lead",
          description: "Создать новый лид(Lead) или сделку в Битрикс24",
          inputSchema: {
            type: "object",
            properties: {
              title: { type: "string", description: "Название лида" },
              name: { type: "string", description: "Имя клиента" },
              phone: { type: "string", description: "Номер телефона" },
              comments: { type: "string", description: "Комментарии/Детали заявки" },
              opportunity: { type: "number", description: "Сумма (стоимость) в рублях" },
              assigned_by_id: { type: "number", description: "ID ответственного сотрудника. Используй 15 для Анжелы в песочнице, 1 для себя или Игоря." }
            },
            required: ["title"]
          }
        },
        {
          name: "send_message",
          description: "Отправить сообщение в мессенджер/чат Битрикс24",
          inputSchema: {
            type: "object",
            properties: {
              dialog_id: { type: "string", description: "ID диалога или пользователя (например 'chat123' или '1')" },
              message: { type: "string", description: "Текст сообщения" }
            },
            required: ["dialog_id", "message"]
          }
        }
      ]
    }));

    // 2. Обработка вызовов инструментов
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      if (name === "get_deals") {
        const params: any = {
          "select[]": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "DATE_MODIFY"],
          "order[DATE_MODIFY]": "DESC"
        };
        if (args?.status) params["filter[STAGE_ID]"] = args.status;
        
        const data = await this.callBitrix("crm.deal.list", params);
        return {
          content: [{ type: "text", text: JSON.stringify(data.result, null, 2) }]
        };
      } 
      
      else if (name === "create_lead") {
        const fields: any = {
          TITLE: args?.title,
          NAME: args?.name || "",
          SOURCE_ID: "AI_AGENT",
          COMMENTS: args?.comments || "",
          ASSIGNED_BY_ID: args?.assigned_by_id || undefined
        };
        if (args?.phone) {
          fields["PHONE"] = [{ VALUE: args.phone, VALUE_TYPE: "WORK" }];
        }
        if (args?.opportunity) {
          fields["OPPORTUNITY"] = args.opportunity;
          fields["CURRENCY_ID"] = "RUB";
        }
        
        const data = await this.callBitrix("crm.lead.add", { FIELDS: fields });
        return {
          content: [{ type: "text", text: `Lead created successfully! ID: ${data.result}` }]
        };
      }
      
      else if (name === "send_message") {
        const data = await this.callBitrix("im.message.add.json", {
          DIALOG_ID: args?.dialog_id,
          MESSAGE: args?.message
        });
        return {
          content: [{ type: "text", text: `Message sent! Message ID: ${data.result}` }]
        };
      }

      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("🚀 Bitrix24 MCP Server running on stdio");
  }
}

const server = new BitrixMcpServer();
server.run().catch(console.error);
