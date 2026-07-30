# DESIGN.md — AI Bureau

> **Reference:** https://maritime-brokerage-23.aura.build/ (KL Maritime)
> **Generated:** 2026-07-29
> **Target:** AI Bureau website redesign

## Reference Analysis (KL Maritime)

### Color Palette
| Token | Value | Usage |
|-------|-------|-------|
| `--bg-dark` | `#071B2C` | Dark sections, footer |
| `--bg-light` | `#F7F9FB` | Light sections |
| `--bg-white` | `#ffffff` | Cards |
| `--text-primary` | `#071B2C` | Headings (light bg) |
| `--text-secondary` | `#5F7488` | Body text |
| `--accent-gold` | `#C9A227` | Buttons, highlights |
| `--accent-gold-light` | `#E8D9A3` | Labels, hover states |
| `--accent-blue` | `#0E4A7B` | Secondary accent |
| `--border` | `#D8E1EA` | Card borders |

### Typography
| Element | Family | Size | Weight | Tracking |
|---------|--------|------|--------|----------|
| Hero H1 | Manrope | `clamp(3rem, 8vw, 8xl)` | 600 | `-0.02em` |
| Section H2 | Manrope | `4xl-6xl` | 600 | `-0.02em` |
| Card H3 | Manrope | `xl-2xl` | 500-600 | `-0.02em` |
| Body | Inter | `sm-base` | 300 | normal |
| Labels | Inter | `xs` | 500 | `0.2-0.24em` |
| CTA | Inter | `sm` | 500 | normal |

### Key Design Patterns
1. **Glass-morphism header** — backdrop-blur, border, transparent → white on scroll
2. **Hero word animation** — each word animates from bottom via GSAP
3. **Background image** — full-bleed with gradient overlay + grid pattern
4. **Canvas animation** — bezier curves with interactive dots (mouse-follow)
5. **Smooth scroll** — Lenis with custom easing
6. **Scroll-reveal** — GSAP ScrollTrigger, `y: 42 → 0`, `power3.out`
7. **Cards** — white, rounded-2xl, top gradient accent line on hover, translateY(-2)
8. **Glass cards** — backdrop-blur, border, shadow, floating animation
9. **Stats bar** — dark, 4 columns, gold labels
10. **Testimonials** — glass cards with rotation transform, floating

### Animation Specs
| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Header nav | `y: -24 → 0, opacity: 0→1` | 0.9s | `power4.out` |
| Hero words | `yPercent: 105 → 0`, stagger 0.12s | 1.1s/word | `power4.out` |
| Hero content | `y: 24 → 0, opacity: 0→1`, stagger 0.08s | 0.75s | `power4.out` |
| Hero panel | `y: 40 → 0, scale: 0.96→1, opacity: 0→1` | 1s | `power4.out` |
| Scroll-reveal | `y: 42 → 0, opacity: 0→1` | 0.9s | `power3.out` |
| Glass cards | `y: -18 → 18`, stagger 0.25s, repeat -1 | 2.8s | `sine.inOut` |
| Hero parallax | `yPercent: 0 → -8`, scrub 1 | scroll | `none` |
| Smooth scroll | Lenis, duration 1.15 | — | custom expo |

---

## AI Bureau — Design Tokens (Adapted)

### Colors (Dark Theme)
```css
:root {
  --bg-primary: #071B2C;       /* deep navy (вместо #000) */
  --bg-secondary: #0a2540;     /* elevated sections */
  --bg-light: #F7F9FB;         /* light sections */
  --bg-card: #ffffff;          /* cards on light bg */
  --text-primary: #ffffff;
  --text-secondary: rgba(255,255,255,0.65);
  --text-muted: rgba(255,255,255,0.45);
  --accent-gold: #C9A227;
  --accent-gold-light: #E8D9A3;
  --accent-cyan: #00f0ff;      /* сохраняем AI-акцент */
  --border-subtle: rgba(255,255,255,0.10);
  --glass-bg: rgba(255,255,255,0.06);
}
```

### Layout
- Max width: `1280px` (max-w-7xl)
- Section padding: `py-20 lg:py-28`, `px-4 sm:px-6 lg:px-8`
- Card: `rounded-2xl`, `p-8`, shadow, border
- Header: `fixed top-0 z-50`, glass, rounded-2xl nav

### Components to Implement
1. **Header** — glass nav, logo left, nav center, CTA right → scroll-based color change
2. **Hero** — background image with overlay, large heading, subtitle, 2 CTAs, stats/metrics panel
3. **Services** — 5 cards (was 4 in reference, адаптируем), top hover accent line, hover translate
4. **Stats** — 4-column metrics bar (dark bg, gold labels)
5. **Testimonials** — glass cards with rotation
6. **CTA** — full-width with bg image and overlay
7. **Footer** — dark, column layout, gold accents
8. **Canvas** — neural network animation (AI-themed вместо ship routes)

### Scripts to Add
- GSAP + ScrollTrigger (via CDN or npm)
- Lenis for smooth scroll
- Inline canvas animation (neural network nodes)
