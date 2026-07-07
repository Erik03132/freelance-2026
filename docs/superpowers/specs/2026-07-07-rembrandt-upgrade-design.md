# Rembrandt Upgrade: Universal Designer Agent

**Date:** 2026-07-07
**Status:** Draft
**Project:** ai-eggs / freelance-agent

## Problem

Rembrandt currently exists as two separate artifacts:
1. `freelance-agent/.agent/agents/rembrandt-designer.md` — a prompt-only agent profile that tells the LLM to "design well" but has no tooling
2. `ai-eggs/agent/rembrandt.py` — a standalone Leonardo.ai image generator script

There is no integration between these, no DESIGN.md generation, no component generation, and no shared design system.

## Goal

Transform Rembrandt into a universal designer agent that can:
1. Generate full DESIGN.md specs (like Refero Styles) from a design brief
2. Generate production-ready HTML/CSS components from DESIGN.md specs
3. Generate images via Leonardo.ai
4. Be used both as CLI (`python3 rembrandt.py`) and callable by other agents (Шекспир, Маркетолог)
5. Carry a default IncuBird brand system for consistent visual identity

## Architecture

```
rembrandt.py CLI
    │
    ├── --design "brief"    → DesignSystemGenerator → DESIGN.md + tokens.json
    ├── --component "spec"  → ComponentGenerator     → HTML/CSS file
    ├── --prompt "..."      → ImageGenerator         → PNG file (existing)
    │
    └── shared:
        ├── incubird-design.json  (default brand)
        └── refero-styles/        (reference library)
```

### Module Structure

```
agent/
├── rembrandt.py              # CLI entry point + orchestration
├── design_generator.py       # DESIGN.md generation from brief
├── component_generator.py    # HTML/CSS generation from spec
├── image_generator.py        # Leonardo.ai wrapper (extracted from rembrandt.py)
├── brand_system.py           # Brand system data model + loader
└── tokens.py                 # Design token definitions (colors, typography, spacing)
```

### 1. Brand System (brand_system.py)

A JSON-serializable data model that holds a complete design system:

```python
@dataclass
class DesignToken:
    name: str
    value: str
    token: str
    role: str

@dataclass 
class BrandSystem:
    name: str
    theme: str  # "light" | "dark"
    colors: list[DesignToken]
    typography: dict  # fonts, weights, scale, tracking
    spacing: dict     # spacing scale, radii, shadows
    components: dict  # component specs
    guidelines: list[str]  # do's and don'ts
```

Default `incubird-design.json`:
- **Theme:** light/warm (agricultural brand)
- **Colors:** Earth tones (olive, terracotta, wheat) + warm neutrals
- **Font:** Manrope, Inter, PT Serif for headings
- **Spacing:** 4px base, generous card padding, 8px/16px/24px/48px ladder
- **Shadows:** Soft, warm-toned

### 2. DESIGN.md Generator (design_generator.py)

Takes a natural language brief → produces full DESIGN.md in Refero-compatible format.

**Input:**
```bash
python3 rembrandt.py --design "Modern agricultural brand, warm earth tones, trustworthy"
```

**Output:** `output/design.md` + `output/tokens.json`

**Format:** Refero DESIGN.md format:
- Theme description
- Color palette (named colors, hex, tokens, roles)
- Typography (fonts, scale, weights, tracking)
- Spacing & shapes (scale, radii, shadows)
- Components (buttons, cards, inputs, nav, hero)
- Do's and don'ts
- CSS Custom Properties output
- Agent Prompt Guide

**Implementation:** Uses LLM calls via OpenRouter + deterministic token/output formatting.

### 3. Component Generator (component_generator.py)

Takes a component type + optional style reference → HTML/CSS.

**Input:**
```bash
python3 rembrandt.py --component "hero section with gradient background, CTA button, stats row" --style incubird
```

**Output:** `output/component.html` with embedded CSS

**Approach:** Uses LLM to generate based on the brand system's DESIGN.md spec. The LLM already knows HTML/CSS — the skill profile ensures it follows the design system.

**Supported components:** button, card, input, nav, hero, section, badge, stats, footer, modal, form

### 4. Image Generator (image_generator.py)

Extracted from current `rembrandt.py` — no changes needed functionally. Just refactored into a separate module for clean imports.

### 5. Agent Profile Update (rembrandt-designer.md)

**Skills to add:**
- `frontend-design` (already exists)
- `web-design-guidelines` (already exists)
- New: `refero-styles` — knowledge of DESIGN.md format
- New: `brand-systems` — brand system management

**Prompt enhancements:**
- Reference to Refero Styles as design reference library
- IncuBird brand system as default
- Knowledge of `--design`, `--component`, `--prompt` CLI commands
- Instructions for other agents on how to call Rembrandt

### 6. Refero Integration

Rembrandt's profile references `https://styles.refero.design/` as a living design library:
- "When asked for a design, first check Refero Styles for similar brand aesthetics"
- Can pull DESIGN.md from Refero as reference before generating
- Generated DESIGN.md follows Refero's format for cross-agent compatibility

## Data Flow

```
Agent (Шекспир/Маркетолог) 
    │
    └── calls rembrandt.py --component "hero section for IncuBird article"
            │
            ├── loads incubird-design.json → brand tokens
            ├── generates HTML/CSS with LLM
            └── returns file path → agent saves to project
```

## Edge Cases & Error Handling

- **No brand system provided:** Falls back to IncuBird default
- **Invalid component type:** Returns error with list of supported types
- **Leonardo API unavailable:** Returns None with clear error message
- **Empty brief for --design:** Prompts for more details (interactive mode)
- **Output directory doesn't exist:** Auto-creates `output/`
- **LLM token overflow:** Falls back to shorter prompts

## Constraints

- All generated HTML/CSS must be vanilla — no build tools, no framework dependencies
- Every design must have mobile + desktop versions
- No placeholder images in final output
- Generated files must be under 100KB
- Leonardo.ai image generation kept as optional (graceful fallback if no API key)

## Non-Goals

- NOT an image editor/manipulator (no PIL/Canvas processing pipeline)
- NOT a full design tool (Figma alternative)
- NOT a Tailwind/component library generator (vanilla CSS only)
- NOT responsible for deployment or asset hosting

## Future

- Refero MCP integration: connect to Refero's MCP server for real-time style search
- Design diff: compare two brand systems and suggest improvements
- Multi-brand: maintain multiple brand systems and switch between them
- Component CSS variables mode: output Tailwind v4 config alongside vanilla CSS
