# Hermes Skills Sync — Global Synchronization Solution

## Overview

Hermes Skills Sync — это централизованная система для управления конфигурацией, скиллами и профилями Hermes Agent across all environments (macOS Desktop, VPS instances, cloud environments, OpenCode, ZCode/Claude IDEs).

### Key Features

1. **Канонический репозиторий** — `freelance-2026` — основной источник истины для всех скиллов агентов
2. **Event-driven sync** — автоматическое обновление runtime cache при изменениях
3. **Кросс-инфраструктурная синхронизация** — macOS ↔ VPS ↔ Cloud instances
4. **Full control workflows** — manual review + auto-merge
5. **Git-долгая история** — ветки, коммиты, ругбаки, QA

### Directory Structure

```
hermes-skills-sync/
├── .git/                                    ← канонический репозиторий (git)
├── skills/                                  ← all agent skills (main source)
│   ├── jobhunter/                           ← batrak skills (from freelance-2026)
│   ├── femida/                              ← femida skills
│   ├── sherlock/                            ← sherlock skills
│   └── ...                                  ← all other agents
├── .hermes/profiles/                         ← runtime cache (symlinks)
│   ├── batrak/skills/                        ← symlinked → ../skills/batrak
│   ├── femida/skills/                        ← symlinked → ../skills/femida
│   └── ...
├── sync/                                    ← automation scripts & configs
│   ├── daemon/                               ← watchdog + cron daemon
│   ├── vps/                                  ← remote VPS sync
│   └── mac/                                  ← local macOS sync
├── hooks/                                   ← git hooks + validation
│   ├── pre-commit.d/                         ← validation scripts
│   ├── post-merge.d/                         ← post-merge sync
│   └── ...
├── scripts/                                  ← utility scripts
│   ├── sync-daemon.sh                         ← main sync daemon
│   ├── vps-sync.sh                           ← remote sync to VPS
│   └── mac-sync.sh                           ← local sync from Mac
├── cron/                                     ← cron jobs
├── logs/                                     ← logs & monitoring
└── config.yaml                               ← sync configuration
```

## Quick Start

### 1. Setup Canon Repository

```bash
# Initialize the main repository
cd freelance-2026/hermes-skills-sync
git init

# Copy current skills to canon
mkdir -p skills/batrak
cp -r /Users/igorvasin/freelance-2026/skills/jobhunter/* skills/batrak/

# Add other agents
# ... (repeat for other agents)

# Commit initial state
git add skills/
git commit -m "Initial sync: Canon skills source"
```

### 2. Setup Local Runtime Cache

```bash
# Setup runtime cache for batrak profile
cd /Users/igorvasin/.hermes/profiles/batrak
rm -rf skills/
mkdir -p skills/batrak
cp -r /Users/igorvasin/freelance-2026/hermes-skills-sync/skills/batrak/* skills/batrak/
```

### 3. Setup Synchronization Daemon

```bash
# Start the sync daemon
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
cat > sync/daemon/sync-daemon.sh << 'EOF'
#!/bin/bash

# Configuration
CANON_DIR="/Users/igorvasin/freelance-2026/hermes-skills-sync/skills"
RUNTIME_DIR="/Users/igorvasin/.hermes/profiles"
VPS_HOST="user@vps-217-149-23-113"
LOG_FILE="/Users/igorvasin/freelance-2026/hermes-skills-sync/logs/sync.log"

# Function: sync canon to runtime
function sync_canon_to_runtime() {
    local agent=$1
    local canon_path="$CANON_DIR/$agent"
    local runtime_path="$RUNTIME_DIR/$agent/skills/$agent"
    
    if [ ! -d "$canon_path" ]; then
        echo "[$(date)] WARN: Canon directory $agent not found" >> "$LOG_FILE"
        return 1
    fi
    
    # Create runtime directory structure
    mkdir -p "$(dirname "$runtime_path")"
    
    # Sync with rsync for efficiency
    rsync -av --delete "$canon_path/" "$runtime_path/" >> "$LOG_FILE" 2>&1
    
    echo "[$(date)] Sync completed: $agent → runtime" >> "$LOG_FILE"
}

# Function: sync to VPS via SSH
function sync_to_vps() {
    local agent=$1
    local canon_path="$CANON_DIR/$agent"
    
    if [ ! -d "$canon_path" ]; then
        return 1
    fi
    
    # Sync to VPS
    rsync -av --delete "$canon_path/" "$VPS_HOST:/home/user/freelance-2026/skills/$agent/" >> "$LOG_FILE" 2>&1
    
    echo "[$(date)] VPS sync completed: $agent" >> "$LOG_FILE"
}

# Main sync loop
while true; do
    # Sync all agents
    for agent in "$(ls -d $CANON_DIR/*/ | xargs -n1 basename)"; do
        sync_canon_to_runtime "$agent"
        sync_to_vps "$agent"
    done
    
    # Wait before next iteration
    sleep 300  # 5 minutes
    
done
EOF

chmod +x sync/daemon/sync-daemon.sh
```

### 4. Setup Cron Jobs

```bash
# Add cron jobs
cat > /Users/igorvasin/freelance-2026/hermes-skills-sync/cron/sync-cron << 'EOF'
# Sync daemon (every 5 minutes)
*/5 * * * * cd /Users/igorvasin/freelance-2026/hermes-skills-sync && ./sync/daemon/sync-daemon.sh

# Daily backup of canon repository
0 2 * * * cd /Users/igorvasin/freelance-2026/hermes-skills-sync && git archive -o "backups/hermes-skills-sync-$(date +%Y%m%d).tar.gz" main

# Weekly validation
0 0 * * 0 cd /Users/igorvasin/freelance-2026/hermes-skills-sync && ./hooks/pre-commit.d/validate-all.sh
EOF

# Install cron (macOS uses launchd, not cron)
# For macOS:
launchctl load -w /Users/igorvasin/freelance-2026/hermes-skills-sync/cron/sync-cron.plist

# For systemd (Linux/VPS):
sudo cp /Users/igorvasin/freelance-2026/hermes-skills-sync/cron/sync-cron /etc/cron.d/hermes-skills-sync
sudo chmod 644 /etc/cron.d/hermes-skills-sync
sudo systemctl restart cron
```

### 5. Setup Git Hooks

```bash
# Pre-commit validation hook
cat > /Users/igorvasin/freelance-2026/hermes-skills-sync/hooks/pre-commit.d/validate-all.sh << 'EOF'
#!/bin/bash

echo "=== Validating skills sync ==="

# Check for broken symlinks in runtime
for profile in /Users/igorvasin/.hermes/profiles/*/skills/; do
    if [ -L "$profile" ]; then
        target="$(readlink "$profile")"
        if [ ! -e "$target" ]; then
            echo "ERROR: Broken symlink in $profile -> $target"
            exit 1
        fi
    fi
done

# Validate that all profiles have their skills
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
for agent in $(ls skills/); do
    if [ ! -d "skills/$agent" ]; then
        echo "ERROR: Missing skills/$agent directory"
        exit 1
    fi
    
done

echo "=== Validation passed ==="
EOF

chmod +x /Users/igorvasin/freelance-2026/hermes-skills-sync/hooks/pre-commit.d/validate-all.sh
```

### 6. Start Services

```bash
# Start sync daemon (background)
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
./sync/daemon/sync-daemon.sh &

# Setup monitoring
cat > /Users/igorvasin/freelance-2026/hermes-skills-sync/scripts/monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="/Users/igorvasin/freelance-2026/hermes-skills-sync/logs/sync.log"

# Show recent logs
tail -f "$LOG_FILE" &

# Check if daemon is running
if ! pgrep -f "sync-daemon.sh" > /dev/null; then
    echo "ERROR: Sync daemon is not running"
    exit 1
fi

# Check for sync errors
if [ -f "$LOG_FILE" ] && grep -q "ERROR" "$LOG_FILE"; then
    echo "WARNING: Found errors in sync logs"
fi

# Check VPS connectivity
if ! ssh -o ConnectTimeout=5 "$VPS_HOST" "echo VPS reachable" > /dev/null 2>&1; then
    echo "ERROR: Cannot connect to VPS"
    exit 1
fi

echo "=== Monitoring active ==="
EOF

chmod +x /Users/igorvasin/freelance-2026/hermes-skills-sync/scripts/monitor.sh
```

## Management Commands

### Sync Operations

```bash
# Manual sync (canon → runtime)
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
./scripts/sync-scripts/sync-mac.sh

# Sync to VPS
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
./scripts/sync-scripts/vps-sync.sh

# Check sync status
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
./scripts/monitor.sh
```

### Git Operations

```bash
# Review changes in canon
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
git status
git diff HEAD

# Create feature branch for changes
git checkout -b feature/agent-updates

# Make changes to skills/
git add skills/
git commit -m "Add agent updates"

# Merge feature branch after review
git checkout main
git merge feature/agent-updates

# Rollback if needed
git reset --hard main~1
```

### Validation & Testing

```bash
# Validate all profiles
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
./hooks/pre-commit.d/validate-all.sh

# Test VPS sync
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
./scripts/sync-scripts/vps-sync-test.sh

# Check for missing skills
cd /Users/igorvasin/freelance-2026/hermes-skills-sync
./scripts/validate-missing-skills.sh
```

## Monitoring & Troubleshooting

### Log Files

- **Sync logs:** `/Users/igorvasin/freelance-2026/hermes-skills-sync/logs/sync.log`
- **Git logs:** `/Users/igorvasin/freelance-2026/hermes-skills-sync/.git/logs/refs/heads/main`
- **Service logs:** `~/Library/LaunchAgents/com.hermes-skills-sync.plist`

### Common Issues & Solutions

1. **Symlink broken**
   ```bash
   # Fix broken symlink
   cd /Users/igorvasin/.hermes/profiles/batrak
   rm -rf skills/batrak
   mkdir -p skills/batrak
   rsync -av /Users/igorvasin/freelance-2026/hermes-skills-sync/skills/batrak/ skills/batrak/
   ```

2. **Sync daemon not running**
   ```bash
   # Check if daemon is running
   ps aux | grep sync-daemon.sh
   
   # Restart if not running
   cd /Users/igorvasin/freelance-2026/hermes-skills-sync
   ./sync/daemon/sync-daemon.sh &
   ```

3. **VPS sync failed**
   ```bash
   # Check VPS connectivity
   ssh -i ~/.ssh/id_rsa user@vps-217-149-23-113 "echo 'VPS accessible'"
   
   # Check SSH config
   cat ~/.ssh/config | grep vps-217-149-23-113
   ```

## Contributing

### Adding New Agent Skills

1. Create skills directory: `mkdir -p skills/<agent-name>`
2. Copy agent skills: `cp -r /path/to/source/skills/<agent-name> skills/<agent-name>/`
3. Validate structure: Check for `SKILL.md`, `scripts/`, `references/`
4. Commit changes: `git add skills/<agent-name>`

### Updating Runtime Profiles

1. After committing to canon, run sync: `./sync/daemon/sync-daemon.sh`
2. Or manual sync: `./scripts/sync-scripts/sync-mac.sh`

## Support

For issues or questions, check the logs:
- Sync logs: `/Users/igorvasin/freelance-2026/hermes-skills-sync/logs/sync.log`
- Configuration: `/Users/igorvasin/freelance-2026/hermes-skills-sync/config.yaml`
- Scripts: `/Users/igorvasin/freelance-2026/hermes-skills-sync/scripts/`

## License

This project is part of the Hermes Agent ecosystem and is licensed under the MIT License.
