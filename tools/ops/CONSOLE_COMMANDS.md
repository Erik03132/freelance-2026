# CONSOLE_COMMANDS.md — что вписать в консоль Timeweb (KVM / Web Console)

> Подготовлено агентом ночью 23.08.2026. SSH с Mac забанен (таймаут
> подтверждён вживую: `ssh root@217.149.23.113` → `Operation timed out`).
> Прямой shell недоступен. Два пути починки Грока + брутфорса.

## ⚠️ ПЕРЕД выключением пароля (пункт 2)
Сначала убедись, что твой публичный ключ на сервере. Иначе после
выключения PasswordAuthentication ты НЕ зайдёшь даже после разбана —
только через KVM-консоль.

```bash
ls -l /root/.ssh/authorized_keys && wc -l /root/.ssh/authorized_keys
```
Если файл пустой/нет — НЕ выключай пароль, сначала добавь ключ:
```bash
mkdir -p /root/.ssh && chmod 700 /root/.ssh
# вставь свою строку публичного ключа (с Mac: cat ~/.ssh/id_ed25519.pub)
echo "ssh-ed25519 AAAA...твой_публичный_ключ..." >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

---

## Ветка А — разбанил SSH в панели Timeweb
После снятия бана заходишь с Mac по ключу и применяешь патч:

```bash
ssh root@217.149.23.113 'bash -s' < /Users/igorvasin/freelance-2026/tools/ops/patch_vps_nightaudit.sh
```
(патч сам: заменяет grok→hy3-free, выключает пароль, рестарт ssh,
листинг гейтвеев). Перед этим — убедись, что ключ на месте (см. выше).

## Ветка Б — НЕ разбанивал, сидишь в KVM-консоли панели (root уже есть)
Вписывай по блокам. Безопаснее пошагово, чем запускать весь патч сразу.

```bash
# 0. Ключ на месте? (см. блок выше) — обязательно до пункта 2

# 1. Ночной аудит: grok (платный) -> бесплатная OpenRouter-модель
#    Грок платный — на аккаунте лежат деньги, не тратим.
#    Ставим z-ai/glm-5.2:free (фолбэк в скрипте: nemotron-3-super-120b, cohere/north-mini-code).
AUDIT_FILES=$(grep -rl -iE 'grok' /opt/levitan/projects/ai-eggs/ 2>/dev/null | grep -E '\.(py|sh|yaml|json)$' || true)
for f in $AUDIT_FILES; do
  sed -i -E 's#x-ai/grok-4\.5#z-ai/glm-5.2:free#gi' "$f"
  sed -i -E 's/Grok 4\.5/FREE LLM (glm-5.2:free)/gi' "$f"
  sed -i -E 's/\bGrok\b/FREE LLM/gi' "$f"
done
echo "Replaced in: $AUDIT_FILES"

# 2. Выключить пароль (ТОЛЬКО если ключ найден в п.0)
sed -i 's/^#*PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
grep -i PasswordAuthentication /etc/ssh/sshd_config | grep -v '^#'
systemctl restart ssh || service ssh restart

# 3. Гейтвеи (Mustay/Telegram) — подняты ли как systemd?
systemctl list-units --type=service | grep -iE 'hermes|gateway|batrak|bridge|personal' || echo "no hermes-gateway units found"
```

---

## После применения — проверка с Mac (когда разбанишь)
```bash
ssh -o ConnectTimeout=10 root@217.149.23.113 'uptime; systemctl is-active ssh; grep -i PasswordAuthentication /etc/ssh/sshd_config | grep -v "^#"'
```
Ожидаемо: `ssh active`, `PasswordAuthentication no`.

## Где лежит сам аудит (на сервере)
`/opt/levitan/projects/ai-eggs/` (скрипт `night_audit_vps.sh` + копия
локально в `tools/ops/`). Патч правит grok-ссылки внутри этого каталога.
Других мест с grok в проде (кроме упоминаний в chp.md/checkpoints) нет.
