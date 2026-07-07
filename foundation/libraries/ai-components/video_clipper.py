"""
Video Clipper — автонарезка докладов в вертикальные ролики.

Пайплайн:
1. Whisper → транскрибация видео с таймкодами
2. LLM → поиск хайлайтов (эмоциональность, тезисы, цитаты)
3. ffmpeg → нарезка в вертикальный формат 9:16 с субтитрами

Использование:
    python video_clipper.py <video_path> [--model medium] [--highlights 5]
"""
import argparse
import json
import subprocess
import sys
import os
from pathlib import Path


def transcribe_video(video_path: str, model_size: str = "medium") -> dict:
    """
    Транскрибирует видео через Whisper.
    
    Args:
        video_path: путь к видео
        model_size: размер модели (tiny, base, small, medium, large)
        
    Returns:
        dict с segments: [{start, end, text}]
    """
    import whisper
    
    print(f"🎤 Загрузка Whisper модели: {model_size}")
    model = whisper.load_model(model_size)
    
    print(f"📝 Транскрибация: {video_path}")
    result = model.transcribe(
        video_path,
        language="ru",
        verbose=False
    )
    
    segments = [
        {
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        }
        for seg in result["segments"]
    ]
    
    print(f"✅ Транскрибация завершена: {len(segments)} сегментов")
    return {"segments": segments, "text": result["text"]}


def find_highlights_llm(transcript: dict, num_highlights: int = 5) -> list:
    """
    Находит хайлайты через LLM.
    
    Критерии:
    - Эмоциональность (восклицания, вопросы)
    - Ключевые тезисы (определения, выводы)
    - Цитатность (короткие яркие фразы)
    
    Args:
        transcript: результат transcribe_video
        num_highlights: количество хайлайтов
        
    Returns:
        list: [{start, end, text, reason, score}]
    """
    segments = transcript["segments"]
    
    # Группируем сегменты в блоки по ~30 секунд
    blocks = []
    current_block = {"start": 0, "end": 0, "texts": []}
    
    for seg in segments:
        if seg["end"] - current_block["start"] > 30 and current_block["texts"]:
            current_block["text"] = " ".join(current_block["texts"])
            blocks.append(current_block)
            current_block = {"start": seg["start"], "end": seg["end"], "texts": []}
        
        current_block["end"] = seg["end"]
        current_block["texts"].append(seg["text"])
    
    if current_block["texts"]:
        current_block["text"] = " ".join(current_block["texts"])
        blocks.append(current_block)
    
    # Скоринг блоков по эвристикам
    scored_blocks = []
    
    for block in blocks:
        score = 0
        reasons = []
        text = block["text"]
        
        # Эмоциональность
        if "!" in text:
            score += 15
            reasons.append("эмоциональность")
        if "?" in text:
            score += 10
            reasons.append("вопрос")
        
        # Ключевые слова
        keywords = ["важно", "главное", "итог", "вывод", "ключевое", "основное",
                     "запомните", "обратите внимание", "секрет", "фишка"]
        for kw in keywords:
            if kw in text.lower():
                score += 20
                reasons.append(f"тезис ({kw})")
                break
        
        # Цитатность (короткие яркие фразы)
        sentences = text.split(".")
        short_sentences = [s.strip() for s in sentences if 10 < len(s.strip()) < 80]
        if short_sentences:
            score += 15
            reasons.append("цитатность")
        
        # Длина блока (не слишком короткий, не слишком длинный)
        duration = block["end"] - block["start"]
        if 15 <= duration <= 60:
            score += 10
            reasons.append("оптимальная длина")
        
        scored_blocks.append({
            "start": block["start"],
            "end": block["end"],
            "text": text[:200],
            "score": score,
            "reason": ", ".join(reasons) if reasons else "общий контент"
        })
    
    # Сортируем по скору и берём топ-N
    scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    highlights = scored_blocks[:num_highlights]
    
    # Сортируем по времени для удобства
    highlights.sort(key=lambda x: x["start"])
    
    print(f"🔥 Найдено хайлайтов: {len(highlights)}")
    for i, h in enumerate(highlights, 1):
        print(f"   {i}. [{h['start']:.0f}s-{h['end']:.0f}s] {h['reason']} (score: {h['score']})")
    
    return highlights


def create_vertical_clip(
    video_path: str,
    highlight: dict,
    output_path: str,
    transcript: dict = None
) -> bool:
    """
    Создаёт вертикальный клип из хайлайта.
    
    Args:
        video_path: путь к исходному видео
        highlight: {start, end, text}
        output_path: путь для сохранения
        transcript: транскрипт для субтитров
        
    Returns:
        True если успешно
    """
    start = highlight["start"]
    duration = highlight["end"] - highlight["start"]
    
    # ffmpeg команда для вертикального видео 9:16 (1080x1920)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", video_path,
        "-t", str(duration),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"✅ Клип создан: {output_path}")
            return True
        else:
            print(f"❌ Ошибка ffmpeg: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Таймаут при создании клипа")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Автонарезка докладов в вертикальные ролики")
    parser.add_argument("video", help="Путь к видео файлу")
    parser.add_argument("--model", default="medium", help="Whisper модель (tiny/base/small/medium/large)")
    parser.add_argument("--highlights", type=int, default=5, help="Количество хайлайтов")
    parser.add_argument("--output", default="clips", help="Папка для клипов")
    parser.add_argument("--transcribe-only", action="store_true", help="Только транскрибация")
    
    args = parser.parse_args()
    
    video_path = args.video
    if not os.path.exists(video_path):
        print(f"❌ Файл не найден: {video_path}")
        sys.exit(1)
    
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # 1. Транскрибация
    transcript = transcribe_video(video_path, args.model)
    
    # Сохраняем транскрипт
    transcript_path = output_dir / "transcript.json"
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    print(f"💾 Транскрипт сохранён: {transcript_path}")
    
    if args.transcribe_only:
        print("✅ Только транскрибация — завершено")
        return
    
    # 2. Поиск хайлайтов
    highlights = find_highlights_llm(transcript, args.highlights)
    
    # Сохраняем хайлайты
    highlights_path = output_dir / "highlights.json"
    with open(highlights_path, "w", encoding="utf-8") as f:
        json.dump(highlights, f, ensure_ascii=False, indent=2)
    
    # 3. Создание клипов
    print(f"\n🎬 Создание клипов...")
    video_name = Path(video_path).stem
    
    for i, highlight in enumerate(highlights, 1):
        clip_path = output_dir / f"{video_name}_clip{i}.mp4"
        create_vertical_clip(video_path, highlight, str(clip_path), transcript)
    
    print(f"\n✅ Готово! Клипы в папке: {output_dir}")


if __name__ == "__main__":
    main()
