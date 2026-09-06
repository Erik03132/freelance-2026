#!/bin/bash
set -e

LOG_DIR=/Users/igorvasin/freelance-2026/projects/levitan/logs
events_file=$LOG_DIR/events.jsonl

# Очистим предыдущие логи
> $events_file
> $LOG_DIR/webhook.log

echo "=== Запуск теста Recon ==="

echo "1. Отправка callback в Mango (проверка формата from)..."
echo "2. Проверка webhook-получателя (raw HTTP) на 217.149.23.113:8087..."

echo "3. Проверка внутреннего диалога Levitan FAQ agent..."
