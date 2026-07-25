---
name: levitan-voice-agent
description: Голосовые агенты Levitan (Анжелла TurboFAQ) — baresip SIP auto-answer, aufile audio, Mango callback, VPS deployment. Все железобетонные настройки, выстраданные через баги baresip v1.0.0.
---

## SIP-регистрация (Mango Office → VPS)

### Аккаунт
```
<sip:user4@vpbx400161137.mangosip.ru>;auth_user=user4;auth_pass=k8&HR5z!aZ62G;answermode=auto;regint=60
```
- `answermode=auto` — **ОБЯЗАТЕЛЬНО** в URI параметрах, а не в глобальном конфиге
- `regint=60` — интервал регистрации 60с

### Mango callback (экстеншен → SIP)
Экстеншен 22 (Василич) маппится на `sip:user4@vpbx400161137.mangosip.ru`:
```
POST https://app.mango-office.ru/vpbx/commands/callback
{
  "command_id": "unique_id",
  "from": {"extension": "22"},
  "to_number": "7985XXXXXXX"
}
```

### Входящий INVITE
Mango шлёт INVITE на порт 5060 VPS. SDP содержит только audio (PCMA/G729/opus), без video.

---

## baresip v1.0.0 — баги и фиксы

### Баг #1: VIDMODE_ON вместо VIDMODE_OFF
**Файл:** `src/ua.c`, строка `call_answer(call, 200, VIDMODE_ON)`
**Симптом:** Входящий вызов → 180 Ringing → НЕТ 200 OK (висит, не отвечает)
**Причина:** baresip использует `VIDMODE_ON` при вызове `call_answer()`, но fakevideo не поддерживает video — вызов падает.
**Фикс:** заменить на `VIDMODE_OFF` во всех трёх местах в `src/ua.c`:
```c
(void)call_answer(call, 200, VIDMODE_OFF);  // ANSWERMODE_AUTO
ua_call_alloc(..., VIDMODE_OFF, ...);       // 2 вызова
```

### Баг #2: answermode не читается из глобального конфига
**Причина:** `ua.c` читает `ua->acc->answermode` (уровень аккаунта), а не `uacfg->answermode`.
Глобальный `answermode auto` в config бесполезен.
**Фикс:** Добавить `;answermode=auto` прямо в URI accounts файла (см. выше).

### Сборка из исходников (v1.0.0)
```bash
git clone https://github.com/baresip/baresip.git
# v1.0.0 не имеет git-тега — берите tarball release v1.0.0
make libbaresip.a USE_TLS= LIBRE_SO=/usr/lib/x86_64-linux-gnu \\
  LIBREM_SO=/usr/lib/x86_64-linux-gnu LIBREM_PATH=/usr SYSROOT=/usr
make baresip USE_TLS= ... # те же флаги
```

### Линковка libbaresip.a (Ubuntu 22.04)
```bash
export LIBRE_SO=/usr/lib/x86_64-linux-gnu
export LIBREM_SO=/usr/lib/x86_64-linux-gnu
export LIBREM_PATH=/usr
export SYSROOT=/usr
# USE_TLS= (пустое) критично — без него падает линковка с libre.so
```

---

## Системный сервис (systemd)

```
/etc/systemd/system/baresip-auto.service
```

```ini
[Unit]
Description=Baresip SIP Auto-Answer (Levitan Voice Agent)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/baresip-patched -f /etc/baresip -t 86400
Restart=always
RestartSec=5
User=root
Group=root

[Install]
WantedBy=multi-user.target
```

**ВАЖНО:** `-t 86400` = quit after 86400s (24ч — keepalive). Первый `-t` (telephone mode) НЕ ИСПОЛЬЗОВАТЬ — getopt съедает следующий аргумент.

---

## Аудио-пайплайн (aufile)

### Принцип
baresip использует модуль `aufile.so` для чтения WAV-файла и отправки в RTP:
- `audio_source aufile,/tmp/levitan_play.wav` — что слышит звонящий
- `audio_player aufile,/dev/null` — заглушка для входящего RTP (не используем)
- `/tmp/levitan_play.wav` — 8kHz, mono, PCM_16 (s16le), без WAV-хедера проблем не будет

### Формат WAV
```
sample rate: 8000
channels: 1  
sample format: s16le (PCM_16)
header: стандартный WAV (RIFF + fmt + data)
```

### Конвертация TTS → WAV (edge-tts)
```python
# edge-tts даёт mp3 → ffmpeg в wav 8kHz mono
subprocess.run([
    "ffmpeg", "-y", "-i", mp3_path,
    "-acodec", "pcm_s16le", "-ar", "8000", "-ac", "1",
    wav_path
])
```

### Лид-сайленс (0.8-1.0 сек)
Перед приветствием добавлять 0.8-1с тишины, чтобы RTP-стрим успел стартовать:
```python
# Склеить тишину + WAV через ffmpeg или sox
```

### Смена аудио на лету
1. Синтезировать новый WAV во временный файл
2. Скопировать поверх `/tmp/levitan_play.wav`
3. baresip подхватит при следующем чтении (aufile читает файл при старте стрима — для смены в текущем вызове нужен ре-инвайт или новый вызов)

---

## Конфиг baresip (продакшен)

```
/etc/baresip/config
```
```
module_path /usr/lib/baresip/modules
module g711.so
module account.so
module fakevideo.so
module aufile.so
module_app menu.so
sip_listen 0.0.0.0:5060
audio_source aufile,/tmp/levitan_play.wav
audio_player aufile,/dev/null
audio_codecs PCMU,PCMA
rtp_ports 20000-30000
```

```
/etc/baresip/accounts
```
```
<sip:user4@vpbx400161137.mangosip.ru>;auth_user=user4;auth_pass=k8&HR5z!aZ62G;answermode=auto;regint=60
```

---

## Диагностика

### Проверить что baresip жив и слушает
```bash
ss -tulpn | grep 5060
journalctl -u baresip-auto -n 20 --no-pager
```

### Лог успешного звонка
```
ua: using AF from sdp offer: af=AF_INET
call: answering call on line 1 from sip:79859XXXXXX@mangosip.ru with 200
stream: update 'audio'
audio: Set audio decoder: PCMA 8000Hz 1ch
audio: Set audio encoder: PCMA 8000Hz 1ch
Call established: sip:79859XXXXXX@mangosip.ru
```

### Если логов звонка нет
1. Проверить что `log_enable_stdout` не false (в сервисе journalctl всё ловит)
2. Убедиться что порт 5060 не занят системным baresip (`apt remove baresip`)
3. Проверить `answermode=auto` в accounts

### SIP-трейс
```bash
tcpdump -i eth0 -nn port 5060 -w sip.pcap
# Проверить: INVITE → 180 Ringing → 200 OK → ACK
tcpdump -r sip.pcap -vvv | grep -E 'INVITE|180|200|ACK'
```

---

## Антипаттерны (что НЕ РАБОТАЕТ)

- ❌ `answermode auto` в глобальном config → бесполезно, читается из accounts URI
- ❌ `-t` (telephone mode) → getopt путает аргументы, не использовать
- ❌ `VIDMODE_ON` в call_answer → баг v1.0.0, вызов не отвечается
- ❌ Ставить `audio_player aufile,...` + `audio_source aufile,...` одновременно → aufile перезаписывает входящий RTP, глотая DTMF
- ❌ Пытаться собрать baresip из git master → ANSWERMODE_AUTO удалён из кода

---

## Быстрый старт с нуля (VPS Timeweb Ubuntu 22.04)

```bash
# 1. Зависимости
apt install -y git build-essential cmake librem-dev libre-dev \
  libasound2-dev libavformat-dev libavdevice-dev libswscale-dev

# 2. Скачать baresip v1.0.0 (tar.gz, не git — тегов нет)
curl -sL https://github.com/baresip/baresip/archive/refs/tags/v1.0.0.tar.gz | tar xz
cd baresip-1.0.0

# 3. Пропатчить VIDMODE_ON → VIDMODE_OFF
sed -i 's/VIDMODE_ON/VIDMODE_OFF/g' src/ua.c

# 4. Собрать
export LIBRE_SO=/usr/lib/x86_64-linux-gnu
export LIBREM_SO=/usr/lib/x86_64-linux-gnu
export LIBREM_PATH=/usr
export SYSROOT=/usr
make -j$(nproc) libbaresip.a baresip USE_TLS= LIBRE_SO=$LIBRE_SO \
  LIBREM_SO=$LIBREM_SO SYSROOT=/usr LIBREM_PATH=/usr

# 5. Установить
cp baresip /usr/local/bin/baresip-patched

# 6. Конфиг (см. выше)
mkdir -p /etc/baresip
# ... создать config и accounts ...

# 7. Сервис
# ... создать baresip-auto.service ...

# 8. UFW
ufw allow 5060/udp
ufw allow 16384:32768/udp
```
