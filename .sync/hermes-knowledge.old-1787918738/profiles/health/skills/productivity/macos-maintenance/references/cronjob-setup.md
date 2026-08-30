# Cron Job Setup for Maintenance Agent

The maintenance agent can run daily via Hermes cronjob to report disk status and reclaimable space.

## Daily Report Job

```bash
cronjob(
    action="create",
    name="Maintenance Agent (daily)",
    prompt="Запусти агента обслуживания компьютера в сухом режиме и пришли краткий отчёт владельцу.\n\nКоманда:\n```\ncd ~/maintenance-agent && python3 maintenance_agent.py\n```\n\nПроанализируй вывод и сообщи владельцу (на русском, кратко):\n1. Загрузка диска (% и свободно ГБ)\n2. Сколько мусора (ГБ) накопилось в Корзине и кэшах старше 7 дней\n3. Если диск заполнен >90% — явно предупреди и предложи запустить очистку командой `python3 maintenance_agent.py --clean`\n4. Если всё в норме (<80%) — просто подтверди «система в порядке».\n\nНе удаляй ничего сам, только отчёт.",
    schedule="0 9 * * *",
    deliver="origin"
)
```

## Behavior

- Runs daily at 09:00 MSK
- Reports: disk usage, reclaimable cache/trash, alerts if >90%
- Does NOT auto-delete — user must approve `--clean` mode
- Delivers to origin chat

## Manual Run

```bash
# Dry run (report only)
cd ~/maintenance-agent && python3 maintenance_agent.py

# Clean mode (actually removes old junk)
cd ~/maintenance-agent && python3 maintenance_agent.py --clean
```

## Notes

- The agent lives at `~/maintenance-agent/maintenance_agent.py`
- Reports are saved to `~/maintenance-agent/reports/`
- Only files older than 7 days are touched (safe for active caches)
- System caches (`com.apple.*`) are protected
