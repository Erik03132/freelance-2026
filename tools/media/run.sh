#!/bin/bash
# Запуск beat-slideshow с автоматическим venv
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/venv"
if [ ! -d "$VENV" ]; then
    echo "Виртуальное окружение не найдено. Установка..."
    python3 -m venv "$VENV"
    source "$VENV/bin/activate"
    pip install librosa numpy opencv-python dlib face_recognition "setuptools<70"
fi
source "$VENV/bin/activate"

if [ "$1" = "smart" ]; then
    shift
    python3 "$SCRIPT_DIR/smart_slideshow.py" "$@"
elif [ "$1" = "direct" ]; then
    shift
    python3 "$SCRIPT_DIR/direct_slideshow.py" "$@"
else
    python3 "$SCRIPT_DIR/beat_slideshow.py" "$@"
fi
