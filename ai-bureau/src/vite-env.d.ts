/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Базовый URL RAG-сервера (по умолчанию http://localhost:3001). */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
