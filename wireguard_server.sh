#!/usr/bin/env bash
# WireGuard SERVER setup — run ONCE on VPS 217.149.23.113 as root.
# Idempotent & safe: re-running updates config without dropping the tunnel.
# Usage:  bash wireguard_server.sh <MAC_PUBLIC_KEY>
set -euo pipefail

WG_PORT=51820
SERVER_WG_IP="10.0.0.1/24"
CLIENT_PUB="${1:-}"

if [[ -z "$CLIENT_PUB" ]]; then
  echo "❌ Pass the Mac WireGuard PUBLIC key:" >&2
  echo "   On Mac first:  wg genkey | tee ~/mac_wg_private | wg pubkey" >&2
  echo "   Then:          bash wireguard_server.sh <MAC_PUBKEY>" >&2
  exit 1
fi

echo "🔧 Installing wireguard..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y && apt-get install -y wireguard wireguard-tools

DIR=/etc/wireguard
mkdir -p "$DIR"
if [[ ! -f "$DIR/server_private.key" ]]; then
  echo "🔑 Generating server keys..."
  wg genkey | tee "$DIR/server_private.key" | wg pubkey > "$DIR/server_public.key"
  chmod 600 "$DIR/server_private.key"
fi
SERVER_PRIV=$(cat "$DIR/server_private.key")

echo "📝 Writing /etc/wireguard/wg0.conf..."
cat > "$DIR/wg0.conf" <<EOF
[Interface]
Address = $SERVER_WG_IP
ListenPort = $WG_PORT
PrivateKey = $SERVER_PRIV
SaveConfig = true

[Peer]
# Mac client
PublicKey = $CLIENT_PUB
AllowedIPs = 10.0.0.2/32
EOF
chmod 600 "$DIR/wg0.conf"

echo "🌐 Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1
grep -q '^net.ipv4.ip_forward=1' /etc/sysctl.conf || echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf

echo "🚀 Bringing up wg0..."
wg-quick down wg0 2>/dev/null || true
wg-quick up wg0
systemctl enable wg-quick@wg0 2>/dev/null || true

echo ""
echo "✅ DONE. Send this SERVER PUBLIC KEY to the Mac:"
cat "$DIR/server_public.key"
echo ""
echo "📊 Status:"
wg show
