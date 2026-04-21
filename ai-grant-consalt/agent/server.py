"""
Ulyana AI Expert Backend — FastAPI сервер (порт 8000)
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Добавляем текущую директорию в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from marina_core import main_rag_pipeline

app = FastAPI(title="Ulyana AI Expert Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    source: str

# Хранилище истории (in-memory, per session)
sessions = {}

@app.get("/")
async def root():
    return {
        "message": "Ulyana AI Expert Backend is running",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        session_id = "default"
        if session_id not in sessions:
            sessions[session_id] = []

        history = sessions[session_id]
        final_answer = main_rag_pipeline(request.message, history)

        # Обновляем историю (последние 10 сообщений)
        history.append({"role": "user", "parts": [request.message]})
        history.append({"role": "model", "parts": [final_answer]})
        sessions[session_id] = history[-10:]

        return ChatResponse(answer=final_answer, source="hybrid_rag")

    except Exception as e:
        print(f"❌ Ошибка бэкенда: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok", "agent": "Ulyana"}

if __name__ == "__main__":
    print("\n👩‍💼 Ulyana AI Expert Backend v2.0")
    print(f"   Gemini:     {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}")
    print(f"   Perplexity: {'✅' if os.getenv('PERPLEXITY_API_KEY') else '❌'}")
    print(f"   OpenRouter: {'✅' if os.getenv('OPENROUTER_API_KEY') else '❌'}")
    print(f"   Neon DB:    {'✅' if os.getenv('NEON_DATABASE_URL') else '❌'}")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
