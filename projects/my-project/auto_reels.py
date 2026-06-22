import os
import random
import numpy as np
from PIL import Image, ImageFilter
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
    vfx
)

# --- КОНФИГУРАЦИЯ ---
TARGET_RES = (1080, 1920)  # Формат 9:16 (Tik-Tok, Reels, Shorts)
CLIP_DURATION = 4.0        # Длительность одного слайда/видео по умолчанию
TRANSITION = 0.5           # Длительность перехода (crossfade)
MEDIA_DIR = "media"
AUDIO_FILE = "track.mp3"
OUTPUT_FILE = "final_reel.mp4"

def process_to_916(clip, target_res=TARGET_RES):
    """
    Превращает любой клип (фото или видео) в вертикальный формат 9:16.
    Если оригинал горизонтальный — добавляет размытый фон.
    """
    w, h = clip.size
    target_w, target_h = target_res
    target_ratio = target_w / target_h
    current_ratio = w / h

    if abs(current_ratio - target_ratio) < 0.01:
        # Уже 9:16, просто ресайзим
        return clip.resize(height=target_h)
    
    # 1. Создаем размытый фон (увеличенный и размытый оригинал)
    bg = clip.resize(height=target_h)
    # Зеркалим и блюрим (через фильтры PIL или эффекты moviepy)
    # Для видео мы просто увеличим его так, чтобы оно закрыло весь экран
    bg = bg.resize(width=target_w * 1.5) # Немного запаса
    bg = bg.set_position('center').crop(x_center=bg.w/2, y_center=bg.h/2, width=target_w, height=target_h)
    bg = bg.fl_image(lambda image: np.array(Image.fromarray(image).filter(ImageFilter.GaussianBlur(radius=20))))
    bg = bg.multiply_alpha(0.4) # Делаем фон потемнее

    # 2. Основной контент (вписываем по ширине)
    fg = clip.resize(width=target_w)
    if fg.h > target_h:
        fg = fg.resize(height=target_h)
    
    fg = fg.set_position('center')
    
    return CompositeVideoClip([bg, fg], size=target_res)

def get_random_cut(video_path, duration=CLIP_DURATION):
    """
    Вырезает случайный фрагмент из видео.
    """
    clip = VideoFileClip(video_path)
    if clip.duration <= duration:
        return clip
    
    start = random.uniform(0, clip.duration - duration)
    return clip.subclip(start, start + duration)

def build_reel():
    print("🚀 Запуск Auto Reels Maker...")
    
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Файл {AUDIO_FILE} не найден! Положите музыку в корень проекта.")
        return

    # 1. Загружаем аудио
    audio = AudioFileClip(AUDIO_FILE)
    total_duration = audio.duration
    print(f"🎵 Аудио: {total_duration:.2f} сек.")

    # 2. Собираем медиа
    all_files = [os.path.join(MEDIA_DIR, f) for f in os.listdir(MEDIA_DIR) if not f.startswith('.')]
    photos = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    videos = [f for f in all_files if f.lower().endswith(('.mp4', '.mov', '.avi'))]
    
    if not photos and not videos:
        print("❌ В папке media нет файлов!")
        return

    print(f"📸 Найдено фото: {len(photos)}, видео: {len(videos)}")

    clips = []
    current_time = 0
    
    # Перемешиваем ресурсы
    pool = photos + videos
    random.shuffle(pool)

    print("🎬 Сборка таймлайна...")
    while current_time < total_duration:
        source = random.choice(pool)
        
        try:
            if source in photos:
                clip = ImageClip(source).set_duration(CLIP_DURATION)
            else:
                clip = get_random_cut(source, CLIP_DURATION)
            
            # Обработка формата 9:16
            clip_916 = process_to_916(clip)
            
            # Эффект наезда (Zoom) для фото
            if source in photos:
                clip_916 = clip_916.resize(lambda t: 1 + 0.04 * t) # Плавный зум 4%
            
            # Переход
            if clips:
                clip_916 = clip_916.crossfadein(TRANSITION)
            
            clips.append(clip_916)
            current_time += (CLIP_DURATION - TRANSITION)
            print(f"   [+] Добавлен фрагмент {len(clips)} ({source})")
            
        except Exception as e:
            print(f"⚠️ Ошибка при обработке {source}: {e}")

    # 3. Склеиваем
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio)
    final_video = final_video.set_duration(total_duration)

    # 4. Рендер
    print(f"🏗️ Рендеринг финального видео {TARGET_RES[0]}x{TARGET_RES[1]}...")
    final_video.write_videofile(OUTPUT_FILE, fps=24, codec="libx264", audio_codec="aac")
    print(f"✨ ГОТОВО! Результат: {OUTPUT_FILE}")

if __name__ == "__main__":
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)
        print(f"📁 Создана папка {MEDIA_DIR}. Положите туда фото и видео.")
    else:
        build_reel()
