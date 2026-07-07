#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slideshow builder for Maria's 10th birthday.
Converts HEIC→JPEG, copies photos, generates HTML slideshow.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
SOURCE_DIR  = Path("/Users/igorvasin/Documents/Маша/download")
MUSIC_SRC   = Path("/Users/igorvasin/Downloads/Giorgia Fumanti - Ave Maria.mp3")
OUT_DIR     = Path("/Users/igorvasin/freelance-2026/my-project/media/masha")
PHOTOS_DIR  = OUT_DIR / "photos"
MUSIC_DIR   = OUT_DIR / "music"

# ─── Setup ────────────────────────────────────────────────────────────────────
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# Copy music
music_dest = MUSIC_DIR / "ave_maria.mp3"
if not music_dest.exists():
    shutil.copy2(MUSIC_SRC, music_dest)
    print(f"✓ Music copied: {music_dest.name}")
else:
    print(f"✓ Music already exists")

# ─── Collect & Convert ────────────────────────────────────────────────────────
SKIP_EXTS = {".mov", ".dng", ".mp4", ".avi"}
HEIC_EXTS  = {".heic"}
COPY_EXTS  = {".jpg", ".jpeg", ".png"}

photos = []
counter = 1

for f in sorted(SOURCE_DIR.iterdir()):
    ext = f.suffix.lower()
    if ext in SKIP_EXTS:
        continue

    out_name = f"photo_{counter:03d}.jpg"
    out_path = PHOTOS_DIR / out_name

    if out_path.exists():
        print(f"  skip (exists): {out_name}")
        photos.append(out_name)
        counter += 1
        continue

    if ext in HEIC_EXTS:
        # Convert HEIC → JPEG using macOS sips
        result = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85",
             str(f), "--out", str(out_path)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  ✓ HEIC→JPG: {f.name} → {out_name}")
            photos.append(out_name)
            counter += 1
        else:
            print(f"  ✗ FAILED: {f.name}: {result.stderr.strip()}")

    elif ext in COPY_EXTS:
        shutil.copy2(f, out_path)
        print(f"  ✓ copied: {f.name} → {out_name}")
        photos.append(out_name)
        counter += 1

print(f"\n✓ Total photos ready: {len(photos)}")

# ─── Generate HTML ────────────────────────────────────────────────────────────
# Ave Maria @ 70 BPM = 857ms/beat. 3/4 time → 1 bar = 2.57s.
# Slide duration: 6 bars = ~15.4s; crossfade: 2s
SLIDE_DURATION = 6000   # ms per slide (visible time excl. fade)
FADE_DURATION  = 2000   # ms crossfade

photos_js = ",\n        ".join([f'"{p}"' for p in photos])

html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Мария — 10 лет ✨</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Playfair+Display:ital,wght@0,400;1,400&display=swap" rel="stylesheet" />

  <style>
    /* ── Reset ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    html, body {{
      width: 100%; height: 100%;
      overflow: hidden;
      background: #1a0f06;
      font-family: 'Cormorant Garamond', Georgia, serif;
    }}

    /* ── Stage ── */
    #stage {{
      position: relative;
      width: 100vw; height: 100vh;
      overflow: hidden;
    }}

    /* ── Slides ── */
    .slide {{
      position: absolute;
      inset: 0;
      opacity: 0;
      transition: opacity {FADE_DURATION}ms ease-in-out;
      will-change: opacity;
    }}
    .slide.active  {{ opacity: 1; }}
    .slide.leaving {{ opacity: 0; }}

    /* ── Photo ── */
    .slide-photo {{
      position: absolute;
      inset: -8%;           /* room for Ken Burns zoom */
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      animation: none;
    }}
    .slide.active .slide-photo {{
      animation: kenBurns {SLIDE_DURATION + FADE_DURATION}ms ease-in-out forwards;
    }}

    @keyframes kenBurns {{
      0%   {{ transform: scale(1.08) translate(0%, 0%); }}
      100% {{ transform: scale(1.00) translate(0%, 0%); }}
    }}
    @keyframes kenBurnsR {{
      0%   {{ transform: scale(1.00) translate(0%, 0%); }}
      100% {{ transform: scale(1.08) translate(-2%, 1%); }}
    }}
    @keyframes kenBurnsU {{
      0%   {{ transform: scale(1.06) translate(1%, 1%); }}
      100% {{ transform: scale(1.00) translate(-1%, -1%); }}
    }}

    /* ── Cinematic overlay (letterbox + warm vignette) ── */
    .slide::after {{
      content: '';
      position: absolute;
      inset: 0;
      background:
        linear-gradient(to bottom,
          rgba(20,8,0,0.45) 0%,
          rgba(20,8,0,0.10) 18%,
          rgba(20,8,0,0.00) 35%,
          rgba(20,8,0,0.00) 65%,
          rgba(20,8,0,0.15) 82%,
          rgba(20,8,0,0.60) 100%),
        radial-gradient(ellipse at center,
          rgba(0,0,0,0) 40%,
          rgba(10,5,0,0.40) 100%);
      pointer-events: none;
      z-index: 2;
    }}

    /* Warm film grain */
    .slide::before {{
      content: '';
      position: absolute;
      inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
      background-repeat: repeat;
      mix-blend-mode: overlay;
      opacity: 0.6;
      pointer-events: none;
      z-index: 3;
    }}

    /* ── Warm color tint overlay ── */
    .warm-tint {{
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg,
        rgba(255,200,120,0.08) 0%,
        rgba(255,160,80,0.05) 100%);
      mix-blend-mode: screen;
      pointer-events: none;
      z-index: 4;
    }}

    /* ── UI Layer ── */
    #ui {{
      position: fixed;
      inset: 0;
      z-index: 10;
      pointer-events: none;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    /* Title block */
    #title-block {{
      text-align: center;
      padding: 3.5vh 5vw 0;
      opacity: 0;
      transform: translateY(-20px);
      transition: opacity 2s ease, transform 2s ease;
    }}
    #title-block.visible {{
      opacity: 1;
      transform: translateY(0);
    }}
    #title-block h1 {{
      font-family: 'Playfair Display', serif;
      font-size: clamp(2rem, 6vw, 5.5rem);
      font-weight: 400;
      font-style: italic;
      color: #fff8f0;
      letter-spacing: 0.12em;
      text-shadow:
        0 2px 30px rgba(255,160,60,0.6),
        0 0 80px rgba(255,200,100,0.3);
      line-height: 1.1;
    }}
    #title-block .subtitle {{
      font-size: clamp(0.9rem, 2vw, 1.6rem);
      color: rgba(255,235,195,0.85);
      letter-spacing: 0.35em;
      margin-top: 0.5em;
      font-weight: 300;
      text-transform: uppercase;
      text-shadow: 0 1px 15px rgba(255,150,50,0.5);
    }}
    #title-block .ornament {{
      color: rgba(255,210,140,0.7);
      font-size: 1.5em;
      margin: 0 0.3em;
    }}

    /* Bottom caption */
    #bottom-bar {{
      text-align: center;
      padding: 0 5vw 3.5vh;
    }}
    #slide-caption {{
      font-size: clamp(0.75rem, 1.5vw, 1.1rem);
      color: rgba(255,235,200,0.7);
      letter-spacing: 0.2em;
      font-weight: 300;
      font-style: italic;
      text-shadow: 0 1px 10px rgba(0,0,0,0.8);
      transition: opacity 0.6s ease;
    }}

    /* Progress dots */
    #progress {{
      display: flex;
      justify-content: center;
      gap: 6px;
      margin-top: 8px;
    }}
    .dot {{
      width: 5px; height: 5px;
      border-radius: 50%;
      background: rgba(255,220,170,0.35);
      transition: background 0.4s ease, transform 0.4s ease;
    }}
    .dot.active {{
      background: rgba(255,210,140,0.9);
      transform: scale(1.4);
    }}

    /* Start overlay */
    #start-overlay {{
      position: fixed;
      inset: 0;
      z-index: 100;
      background: #1a0f06;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: opacity 1.5s ease;
    }}
    #start-overlay.fade-out {{
      opacity: 0;
      pointer-events: none;
    }}
    #start-overlay .logo {{
      font-family: 'Playfair Display', serif;
      font-size: clamp(3rem, 10vw, 9rem);
      font-style: italic;
      color: #fff8f0;
      text-shadow:
        0 0 60px rgba(255,180,80,0.8),
        0 0 120px rgba(255,140,40,0.4);
      letter-spacing: 0.1em;
      animation: breathe 3s ease-in-out infinite;
    }}
    #start-overlay .tagline {{
      font-size: clamp(0.9rem, 2vw, 1.4rem);
      color: rgba(255,220,170,0.7);
      letter-spacing: 0.4em;
      text-transform: uppercase;
      margin-top: 1em;
      font-weight: 300;
    }}
    #start-overlay .play-btn {{
      margin-top: 3em;
      width: 70px; height: 70px;
      border-radius: 50%;
      border: 2px solid rgba(255,220,170,0.6);
      display: flex; align-items: center; justify-content: center;
      animation: pulse 2.5s ease-in-out infinite;
    }}
    #start-overlay .play-btn svg {{
      fill: rgba(255,220,170,0.9);
      width: 28px; height: 28px;
      margin-left: 4px;
    }}
    #start-overlay .hint {{
      margin-top: 1.5em;
      font-size: 0.85rem;
      color: rgba(255,200,140,0.5);
      letter-spacing: 0.2em;
    }}

    /* Floating particles */
    #particles {{
      position: fixed;
      inset: 0;
      z-index: 5;
      pointer-events: none;
      overflow: hidden;
    }}
    .particle {{
      position: absolute;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255,220,150,0.6), transparent);
      animation: float linear infinite;
      pointer-events: none;
    }}

    @keyframes float {{
      0%   {{ transform: translateY(110vh) rotate(0deg); opacity: 0; }}
      10%  {{ opacity: 1; }}
      90%  {{ opacity: 0.6; }}
      100% {{ transform: translateY(-10vh) rotate(360deg); opacity: 0; }}
    }}

    @keyframes breathe {{
      0%, 100% {{ text-shadow: 0 0 60px rgba(255,180,80,0.8), 0 0 120px rgba(255,140,40,0.4); }}
      50% {{ text-shadow: 0 0 80px rgba(255,200,100,1.0), 0 0 160px rgba(255,160,60,0.6); }}
    }}

    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); border-color: rgba(255,220,170,0.6); }}
      50% {{ transform: scale(1.08); border-color: rgba(255,220,170,1.0); }}
    }}

    /* ── Responsive letterbox ── */
    @media (max-width: 768px) {{
      #title-block h1 {{ font-size: 2.5rem; }}
    }}
  </style>
</head>
<body>

<!-- Start overlay -->
<div id="start-overlay">
  <div class="logo">Мария</div>
  <div class="tagline">10 лет — Особенный день</div>
  <div class="play-btn">
    <svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg>
  </div>
  <div class="hint">нажмите, чтобы начать</div>
</div>

<!-- Particle field -->
<div id="particles"></div>

<!-- Main stage -->
<div id="stage"></div>

<!-- UI overlay -->
<div id="ui">
  <div id="title-block">
    <h1><span class="ornament">✦</span> Мария <span class="ornament">✦</span></h1>
    <div class="subtitle">10 лет · С любовью</div>
  </div>
  <div id="bottom-bar">
    <div id="slide-caption">Ave Maria · Giorgia Fumanti</div>
    <div id="progress"></div>
  </div>
</div>

<!-- Audio -->
<audio id="music" loop>
  <source src="music/ave_maria.mp3" type="audio/mpeg" />
</audio>

<script>
// ─────────────────────────────────────────────────────────────
//  Config
// ─────────────────────────────────────────────────────────────
const PHOTOS = [
  {photos_js}
];

const SLIDE_MS  = {SLIDE_DURATION};   // visible time per slide
const FADE_MS   = {FADE_DURATION};    // crossfade duration
const TOTAL_MS  = SLIDE_MS + FADE_MS; // cycle per slide

const KEN_BURNS = ['kenBurns', 'kenBurnsR', 'kenBurnsU'];

const CAPTIONS = [
  'Каждый день — новое чудо…',
  'Маленькие радости большого сердца',
  'Улыбка, которая освещает всё вокруг',
  'Расти счастливой…',
  'С любовью и нежностью',
  'Самая любимая',
  'Детство — это золото',
  'Ты наше солнышко',
  'Маша, с Днём рождения! ✨',
  'Десять лет счастья…',
  'Пусть мечты сбываются',
  'Любимая доченька',
];

// ─────────────────────────────────────────────────────────────
//  Particles
// ─────────────────────────────────────────────────────────────
function createParticles() {{
  const container = document.getElementById('particles');
  for (let i = 0; i < 18; i++) {{
    const p = document.createElement('div');
    p.className = 'particle';
    const size = 2 + Math.random() * 5;
    p.style.cssText = `
      width: ${{size}}px; height: ${{size}}px;
      left: ${{Math.random() * 100}}vw;
      animation-duration: ${{15 + Math.random() * 25}}s;
      animation-delay: ${{-Math.random() * 30}}s;
      opacity: ${{0.3 + Math.random() * 0.4}};
    `;
    container.appendChild(p);
  }}
}}

// ─────────────────────────────────────────────────────────────
//  Slideshow
// ─────────────────────────────────────────────────────────────
const stage   = document.getElementById('stage');
const caption = document.getElementById('slide-caption');
const progress = document.getElementById('progress');
const music   = document.getElementById('music');

let currentIndex = 0;
let currentSlide = null;
let slides = [];
let timer  = null;

// Pre-create all slide DOM nodes
function initSlides() {{
  PHOTOS.forEach((src, i) => {{
    const slide = document.createElement('div');
    slide.className = 'slide';
    slide.innerHTML = `
      <div class="slide-photo" style="background-image:url('photos/${{src}}')"></div>
      <div class="warm-tint"></div>
    `;
    stage.appendChild(slide);
    slides.push(slide);

    // Progress dot
    const dot = document.createElement('div');
    dot.className = 'dot' + (i === 0 ? ' active' : '');
    progress.appendChild(dot);
  }});
}}

function showSlide(idx) {{
  const dots = progress.querySelectorAll('.dot');

  // Leave current
  if (currentSlide) {{
    currentSlide.classList.remove('active');
    currentSlide.classList.add('leaving');
    const leaving = currentSlide;
    setTimeout(() => leaving.classList.remove('leaving'), FADE_MS);
  }}

  // Show next
  const slide = slides[idx];
  const photo = slide.querySelector('.slide-photo');
  const kb    = KEN_BURNS[Math.floor(Math.random() * KEN_BURNS.length)];
  photo.style.animation = 'none';
  void photo.offsetHeight; // reflow
  photo.style.animation = `${{kb}} ${{SLIDE_MS + FADE_MS}}ms ease-in-out forwards`;

  slide.classList.add('active');
  slide.classList.remove('leaving');
  currentSlide  = slide;
  currentIndex  = idx;

  // Caption
  caption.style.opacity = '0';
  setTimeout(() => {{
    caption.textContent = CAPTIONS[idx % CAPTIONS.length];
    caption.style.opacity = '1';
  }}, FADE_MS / 2);

  // Dots
  dots.forEach((d, i) => d.classList.toggle('active', i === idx));
}}

function nextSlide() {{
  const next = (currentIndex + 1) % PHOTOS.length;
  showSlide(next);
}}

function startShow() {{
  showSlide(0);
  timer = setInterval(nextSlide, TOTAL_MS);

  // Fade in title
  setTimeout(() => {{
    document.getElementById('title-block').classList.add('visible');
  }}, FADE_MS);

  // Music
  music.volume = 0;
  music.play().catch(e => console.warn('Autoplay blocked', e));
  fadeVolume(0, 0.85, 3000);
}}

function fadeVolume(from, to, dur) {{
  const steps = 40;
  const dt    = dur / steps;
  const dv    = (to - from) / steps;
  let v = from;
  const iv = setInterval(() => {{
    v = Math.min(Math.max(v + dv, 0), 1);
    music.volume = v;
    if ((dv > 0 && v >= to) || (dv < 0 && v <= to)) clearInterval(iv);
  }}, dt);
}}

// ─────────────────────────────────────────────────────────────
//  Keyboard shortcuts
// ─────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight' || e.key === ' ') {{ nextSlide(); clearInterval(timer); timer = setInterval(nextSlide, TOTAL_MS); }}
  if (e.key === 'ArrowLeft')  {{ showSlide((currentIndex - 1 + PHOTOS.length) % PHOTOS.length); clearInterval(timer); timer = setInterval(nextSlide, TOTAL_MS); }}
  if (e.key === 'f') document.documentElement.requestFullscreen?.();
  if (e.key === 'Escape') document.exitFullscreen?.();
}});

// Click to advance
stage.addEventListener('click', () => {{
  nextSlide();
  clearInterval(timer);
  timer = setInterval(nextSlide, TOTAL_MS);
}});

// ─────────────────────────────────────────────────────────────
//  Start overlay
// ─────────────────────────────────────────────────────────────
const overlay = document.getElementById('start-overlay');
overlay.addEventListener('click', () => {{
  overlay.classList.add('fade-out');
  setTimeout(() => overlay.remove(), 1600);
  startShow();
}});

// ─────────────────────────────────────────────────────────────
//  Init
// ─────────────────────────────────────────────────────────────
createParticles();
initSlides();
</script>
</body>
</html>
'''

out_html = OUT_DIR / "index.html"
out_html.write_text(html, encoding="utf-8")
print(f"\n✅ Slideshow generated: {out_html}")
print(f"   Photos: {len(photos)}")
print(f"   Slide duration: {SLIDE_DURATION/1000}s + {FADE_DURATION/1000}s fade")
print(f"\n▶  Open in browser:")
print(f"   open '{out_html}'")
