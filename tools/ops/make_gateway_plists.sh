#!/bin/bash
# Create launchd plists for hermes gateway profiles that lack one.
# Mirrors the proven ai.hermes.gateway-femida.plist structure.
set -e
AGENT_DIR="$HOME/Library/LaunchAgents"
VENV="$HOME/.hermes/hermes-agent/venv/bin/python"
for prof in marketer sherlock financier; do
  plist="$AGENT_DIR/ai.hermes.gateway-$prof.plist"
  if [ -f "$plist" ]; then
    echo "SKIP $prof (plist exists)"; continue
  fi
  echo "CREATE $plist"
  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.hermes.gateway-$prof</string>

    <key>ProgramArguments</key>
    <array>
        <string>$VENV</string>
        <string>-m</string>
        <string>hermes_cli.stderr_timestamp</string>
        <string>--error-log</string>
        <string>/Users/igorvasin/.hermes/profiles/$prof/logs/gateway.error.log</string>
        <string>--</string>
        <string>$VENV</string>
        <string>-m</string>
        <string>hermes_cli.main</string>
        <string>--profile</string>
        <string>$prof</string>
        <string>gateway</string>
        <string>run</string>
        <string>--external-supervisor</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/igorvasin/.hermes/profiles/$prof</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/igorvasin/.hermes/hermes-agent/venv/bin:/Users/igorvasin/.hermes/hermes-agent/node_modules/.bin:/usr/local/bin:/System/Cryptexes/App/usr/bin:/usr/bin:/bin:/usr/sbin:/sbin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/local/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/bin:/var/run/com.apple.security.cryptexd/codex.system/bootstrap/usr/appleinternal/bin:/pkg/env/global/bin:/usr/local/go/bin:/opt/homebrew/bin:/Users/igorvasin/.hermes/node/bin:/Users/igorvasin/.hermes/node:/Users/igorvasin/.antigravity-ide/antigravity-ide/bin:/Users/igorvasin/bin:/Users/igorvasin/.antigravity/antigravity/bin:/Users/igorvasin/.antigravity:/Users/igorvasin/.antigravity/bin:/Users/igorvasin/.bun/bin:/Users/igorvasin/.local/bin:/Users/igorvasin/.opencode/bin:/Users/igorvasin/.npm-global/bin:/opt/homebrew/sbin:/Users/igorvasin/.orbstack/bin:/usr/local/sbin:/Users/igorvasin/.hermes/bin</string>
        <key>VIRTUAL_ENV</key>
        <string>/Users/igorvasin/.hermes/hermes-agent/venv</string>
        <key>HERMES_HOME</key>
        <string>/Users/igorvasin/.hermes/profiles/$prof</string>
    </dict>

    <key>LimitLoadToSessionType</key>
    <array>
        <string>Aqua</string>
        <string>Background</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>ThrottleInterval</key>
    <integer>30</integer>

    <key>ExitTimeOut</key>
    <integer>25</integer>

    <key>SoftResourceLimits</key>
    <dict>
        <key>NumberOfFiles</key>
        <integer>4096</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/igorvasin/.hermes/profiles/$prof/logs/gateway.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/igorvasin/.hermes/profiles/$prof/logs/gateway.error.log</string>
</dict>
</plist>
EOF
  # load into launchd so it starts now AND on reboot
  launchctl load -w "$plist" 2>/dev/null || launchctl load "$plist"
  echo "LOADED $prof"
done
echo "DONE"
