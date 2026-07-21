module.exports = {
  apps: [
    {
      name: "angela-bot",
      script: "tg_bot.py",
      cwd: "/opt/levitan/projects/ai-eggs/agent",
      interpreter: "/opt/levitan/projects/ai-eggs/.server_venv/bin/python3",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        PYTHONPATH: "/opt/levitan/projects/angel-backend:/opt/levitan/projects/ai-eggs/agent"
      }
    },
    {
      name: "angela-server",
      script: "server.py",
      cwd: "/opt/levitan/projects/angel-backend",
      interpreter: "/opt/levitan/projects/angel-backend/.venv/bin/python3",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        PORT: 5000,
        PYTHONPATH: "/opt/levitan/projects/angel-backend"
      }
    },
    {
      name: "angela-autopilot",
      script: "autopilot.py",
      cwd: "/opt/levitan/projects/ai-eggs/agent",
      interpreter: "/opt/levitan/projects/ai-eggs/.server_venv/bin/python3",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        PYTHONPATH: "/opt/levitan/projects/ai-eggs/agent"
      }
    },
    {
      name: "angela-scheduler",
      script: "scheduler.py",
      cwd: "/opt/levitan/projects/ai-eggs/agent",
      interpreter: "/opt/levitan/projects/ai-eggs/.server_venv/bin/python3",
      autorestart: false,
      watch: false,
      env: {
        PYTHONPATH: "/opt/levitan/projects/ai-eggs/agent"
      }
    },
    {
      name: "ptenchikova-bot",
      script: "feed_interactor.py",
      cwd: "/opt/levitan/projects/ai-eggs/agent",
      interpreter: "/opt/levitan/projects/ai-eggs/.server_venv/bin/python3",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        PYTHONPATH: "/opt/levitan/projects/angel-backend:/opt/levitan/projects/ai-eggs/agent"
      }
    },
    {
      name: "a2a-dispatcher",
      script: "a2a_dispatcher.py",
      cwd: "/opt/levitan/projects/ai-eggs/agent",
      interpreter: "/opt/levitan/projects/ai-eggs/.server_venv/bin/python3",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        PYTHONPATH: "/opt/levitan/projects/ai-eggs/agent"
      }
    },
    {
      name: "mango-webhook",
      script: "mango_webhook.py",
      cwd: "/opt/levitan/projects/ai-eggs/agent",
      interpreter: "/opt/levitan/projects/ai-eggs/.server_venv/bin/python3",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        PYTHONPATH: "/opt/levitan/projects/ai-eggs/agent"
      }
    },
    {
      name: "dtmf-handler",
      script: "dtmf_handler.py",
      cwd: "/opt/levitan/projects/ai-eggs/agent",
      interpreter: "/opt/levitan/projects/ai-eggs/.server_venv/bin/python3",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        PYTHONPATH: "/opt/levitan/projects/ai-eggs/agent"
      }
    },
    {
      name: "vezem-web",
      script: "/opt/levitan/projects/ai-eggs/vezem/dist/server/entry.mjs",
      cwd: "/opt/levitan/projects/ai-eggs/vezem",
      interpreter: "node",
      autorestart: true,
      max_restarts: 10,
      min_uptime: "10s",
      restart_delay: 5000,
      exp_backoff_restart_delay: 100,
      watch: false,
      env: {
        HOST: "0.0.0.0",
        PORT: 4321,
        NODE_ENV: "production"
      }
    }
  ]
};
