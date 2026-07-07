#!/usr/bin/env python3
"""
Levitan — инициализация проекта.
"""
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: list[str], cwd: Path = None) -> bool:
    """Выполнить команду."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка: {' '.join(cmd)}")
            print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False


def main():
    """Основная функция инициализации."""
    project_dir = Path(__file__).resolve().parent.parent
    
    print("🔧 Инициализация проекта Levitan...")
    
    # 1. Создаём виртуальное окружение
    venv_path = project_dir / ".venv"
    if not venv_path.exists():
        print("📦 Создание виртуального окружения...")
        if not run_cmd([sys.executable, "-m", "venv", ".venv"], project_dir):
            return 1
    
    # 2. Устанавливаем зависимости
    pip_path = venv_path / "bin" / "pip"
    if not pip_path.exists():
        pip_path = venv_path / "Scripts" / "pip.exe"  # Windows
    
    print("📥 Установка зависимостей...")
    if not run_cmd([str(pip_path), "install", "--upgrade", "pip"], project_dir):
        return 1
    
    req_path = project_dir / "requirements.txt"
    if not run_cmd([str(pip_path), "install", "-r", str(req_path)], project_dir):
        return 1
    
    # 3. Проверяем .env
    env_path = project_dir / ".env"
    if not env_path.exists():
        print("📝 Создание .env из примера...")
        env_example = project_dir / "config" / ".env.example"
        if env_example.exists():
            env_path.write_text(env_example.read_text())
        else:
            env_path.write_text("# Levitan Environment Variables\n")
    
    print("✅ Инициализация завершена!")
    print(f"\nДля активации окружения:")
    print(f"  cd {project_dir}")
    print(f"  source .venv/bin/activate")
    print(f"\nДля запуска:")
    print(f"  python agent/main.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())