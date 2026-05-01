// ═══════════════════════════════════════════════════════════════
// 🛡️ ECOSYSTEM CONFIG v2.0 — Crash-loop protection
// ═══════════════════════════════════════════════════════════════
// КАЖДЫЙ процесс имеет:
//   max_restarts: 10       — остановка после 10 рестартов (не 661!)
//   min_uptime: "10s"      — считать крашем если жил < 10с
//   restart_delay: 5000    — 5с пауза между рестартами
//   exp_backoff_restart_delay: 100 — экспоненциальный бэкофф
// ═══════════════════════════════════════════════════════════════

// Общие настройки защиты от crash-loop
const CRASH_PROTECTION = {
  autorestart: true,
  max_restarts: 10,
  min_uptime: "10s",
  restart_delay: 5000,
  exp_backoff_restart_delay: 100,
  watch: false,
};

module.exports = {
  apps: [
    {
      name: "ptenchikova-bot",
      script: "ai-eggs/agent/feed_interactor.py",
      cwd: "/root/antigravity",
      interpreter: "/root/antigravity/angel-backend/.venv/bin/python",
      ...CRASH_PROTECTION,
      env: {
        PYTHONPATH: "/root/antigravity/angel-backend:/root/antigravity/ai-eggs/agent",
        BITRIX_WEBHOOK_URL: "https://b24-vskitj.bitrix24.ru/rest/15/vjoxv8u7p3q7x4p3/"
      }
    },
    {
      name: "angela-server",
      script: "angel-backend/server.py",
      cwd: "/root/antigravity",
      interpreter: "/root/antigravity/angel-backend/.venv/bin/python",
      ...CRASH_PROTECTION,
      env: {
        PORT: 5000,
        PYTHONPATH: "/root/antigravity/angel-backend"
      }
    },
    {
      name: "angela-scheduler",
      script: "ai-eggs/agent/scheduler.py",
      cwd: "/root/antigravity",
      interpreter: "/root/antigravity/ai-eggs/.server_venv/bin/python3",
      autorestart: false,
      watch: false,
      env: {
        PYTHONPATH: "/root/antigravity/ai-eggs/agent"
      }
    },
    {
      name: "vezem-web",
      script: "ai-eggs/vezem/dist/server/entry.mjs",
      cwd: "/root/antigravity",
      interpreter: "node",
      ...CRASH_PROTECTION,
      env: {
        HOST: "0.0.0.0",
        PORT: 4321,
        NODE_ENV: "production"
      }
    },
    {
      name: "angela-autopilot",
      script: "ai-eggs/agent/autopilot.py",
      cwd: "/root/antigravity",
      interpreter: "/root/antigravity/ai-eggs/.server_venv/bin/python3",
      ...CRASH_PROTECTION,
      env: {
        PYTHONPATH: "/root/antigravity/ai-eggs/agent"
      }
    },
    {
      name: "angela-bot",
      script: "ai-eggs/agent/tg_bot.py",
      cwd: "/root/antigravity",
      interpreter: "/root/antigravity/ai-eggs/.server_venv/bin/python3",
      ...CRASH_PROTECTION,
      env: {
        PYTHONPATH: "/root/antigravity/angel-backend:/root/antigravity/ai-eggs/agent"
      }
    }
  ]
};
