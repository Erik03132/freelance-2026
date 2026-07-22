---
name: apple-design
description: Apple's approach to interface design and fluid, physical motion, translated for the web. Use when building or reviewing gesture-driven UI, spring animations, drag/swipe/sheet interactions, momentum and interruptible transitions, translucent materials and depth, typography (optical sizing, tracking, leading), reduced-motion, or the design foundations (feedback, spatial consistency, restraint) behind Apple-style interfaces.
source: https://github.com/emilkowalski/skills (19.9k★)
---

# Apple Design

How Apple builds interfaces that stop feeling like a computer and start feeling like an extension of you. This knowledge comes from Apple's WWDC design talks — chiefly *Designing Fluid Interfaces* (WWDC 2018) — distilled and translated into the web platform (CSS, Pointer Events, `requestAnimationFrame`, spring libraries like Motion/Framer Motion).

The through-line: **an interface feels alive when motion starts from the current on-screen value, inherits the user's velocity, projects momentum forward, and can be grabbed and reversed at any instant.** Springs are the tool that makes all of this natural, because they are inherently interruptible and velocity-aware.

## The Core Idea

> "When we align the interface to the way we think and move, something magical happens — it stops feeling like a computer and starts feeling like a seamless extension of us."

Apple frames design as serving four human needs: **safety/predictability, understanding, achievement, and joy.** Every rule here serves one of them.

## 1. Response — kill latency

- **Respond on pointer-down, not on release.** Highlight a button the instant it's pressed.
- **Be vigilant about every latency.** Audit debounces, artificial timers, transition waits, ~300ms tap delay.
- **Feedback must be continuous *during* the interaction, not just at the end.**

```css
.button:active {
  transform: scale(0.97);
  transition: transform 100ms ease-out;
}
```

## 2. Direct manipulation — 1:1 tracking

- Use Pointer Events with `setPointerCapture`.
- Track velocity/position history (last few `pointermove` events).

## 3. Interruptibility — the single most important principle

- **Never lock out input during a transition.**
- **Always animate from the *presentation* (current) value, never the target value.**
- **Avoid CSS transitions and `@keyframes` for anything gesture-driven** — use springs.
- **When a gesture reverses, blend velocity — don't hard-cut it.**
- **Decompose 2D motion into independent X and Y springs.**

## 4. Behavior over animation — use springs

- **Damping ratio** — controls overshoot. `1.0` = critically damped (no bounce). `< 1.0` = oscillates.
- **Response** — how quickly the value reaches the target (seconds). Not "duration".

**Apple defaults:**

| Interaction | Damping | Response |
|---|---|---|
| Move / reposition | `1.0` | `0.4` |
| Rotation | `0.8` | `0.4` |
| Drawer / sheet | `0.8` | `0.3` |

```js
// Critically damped default
animate(el, { y: 0 }, { type: 'spring', bounce: 0, duration: 0.4 });
// Momentum interaction
animate(el, { y: target }, { type: 'spring', bounce: 0.2, duration: 0.4 });
```

## 5. Velocity handoff

```
relativeVelocity = gestureVelocity / (targetValue − currentValue)
```

## 6. Momentum projection

```js
function project(initialVelocity, decelerationRate = 0.998) {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate);
}
```

## 7. Spatial consistency

- Enter and exit along the same path.
- Anchor interactions to their source (set `transform-origin`).
- Mirror the easing on reversible transitions.

## 8. Hint in the direction of the gesture

## 9. Rubber-banding

```js
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

## 10. Gesture design details

- Tap: highlight on touch-down, commit on touch-up. ~10px hysteresis.
- Drag/swipe: ~10px threshold before committing direction, then 1:1.
- Detect all plausible gestures in parallel, cancel losers.

## 11. Frame-level smoothness

- Animate only `transform` and `opacity`. Use `will-change` hint.
- `requestAnimationFrame` for display-synced clock.

## 12. Materials & depth — translucency conveys hierarchy

```css
.toolbar {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
}
```

- Material weight encodes hierarchy (darker = structural, lighter = interactive).
- Never stack light translucent on another.
- Dim to focus (modal + scrim), separate to keep flow (translucent + no scrim).
- Scroll edge effects instead of hard dividers.
- Materialize: animate blur + scale together, not just opacity fade.

## 13. Multimodal feedback

1. Causality — trigger on causal event
2. Harmony — visual + sound + haptic on same frame
3. Utility — only for meaningful moments

## 14. Reduced motion & accessibility

```css
@media (prefers-reduced-motion: reduce) {
  .sheet { transition: opacity 200ms ease; transform: none !important; }
}
@media (prefers-reduced-transparency: reduce) {
  .toolbar { background: white; backdrop-filter: none; }
}
```

## 15. Typography

- Tracking (letter-spacing) is size-specific. Negative for large, near 0 for body.
- Leading (line-height) tracks size inversely. Tight on headings, loose on body.
- Build hierarchy from weight + size + leading as a set.
- Use `rem`/`em` spacing, not fixed px.
- Default to system font: `font: 100%/1.5 system-ui, sans-serif;`
- Display text: `font-size: clamp(2rem, 5vw, 4rem); line-height: 1.05; letter-spacing: -0.02em;`

## 16. Design foundations — eight principles

1. **Purpose** — make with intention; decide what not to build
2. **Agency** — keep people in control; offer choices, easy undo
3. **Responsibility** — act in user's interest; privacy, safety, AI guardrails
4. **Familiarity** — build on known metaphors; be consistent
5. **Flexibility** — adapt to platform, context, abilities; let users personalize
6. **Simplicity** — not minimalism; strip unnecessary, be concise and clear
7. **Craft** — every spacing, timing, alignment is deliberate
8. **Delight** — result of getting other seven right

## Quick Reference

| Need | Technique | Value |
|---|---|---|
| Default UI spring | Critically damped | `damping 1.0`, `response 0.3–0.4` |
| Momentum spring | Under-damped, slight bounce | `damping ~0.8`, `response 0.3–0.4` |
| Rubber-banding | Progressive resistance | `rubberband()` function |
| Translucent chrome | `backdrop-filter` | `blur(20px) saturate(180%)` |
| Type tracking | Size-specific | large: `-0.02em`, body: `0` |
| Reduced motion | Cross-fade | `@media (prefers-reduced-motion)` |
