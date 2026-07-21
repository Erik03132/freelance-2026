"""Slides/presentation generation for Artemiy — Bolt Slides-inspired.

Generates interactive React-based slide decks as standalone HTML.
Each slide is a component with Build animations, Cover, Agenda layouts.
"""

from __future__ import annotations

from .llm_client import call_llm
from .frontend_config import DEFAULTS

SLIDES_PROMPT = """You are a senior frontend engineer. Build an interactive presentation as a **single, self-contained HTML file** about:

TOPIC: {topic}
Audience: {audience}
Framework style: {style}

Use this React + Vite component pattern (inline, transpiled via Babel standalone):

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{topic}</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    :root {{
      --primary: #6366f1;
      --bg: #0f0f1a;
      --text: #f1f1f1;
      --accent: #22d3ee;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); }}
    .deck {{ width: 100vw; height: 100vh; overflow: hidden; position: relative; }}
    .slide {{ width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 4rem; position: absolute; top: 0; left: 0; transition: opacity 0.4s, transform 0.4s; }}
    .slide.active {{ opacity: 1; transform: translateX(0); }}
    .slide.exit {{ opacity: 0; transform: translateX(-60px); }}
    .slide.enter {{ opacity: 0; transform: translateX(60px); }}
    .nav {{ position: fixed; bottom: 2rem; right: 2rem; display: flex; gap: 0.5rem; z-index: 100; }}
    .nav button {{ background: var(--primary); color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; font-size: 1rem; }}
    .nav button:disabled {{ opacity: 0.3; }}
    .slide-counter {{ position: fixed; bottom: 2rem; left: 2rem; font-size: 0.875rem; opacity: 0.6; z-index: 100; }}
    h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
    h2 {{ font-size: 2rem; margin-bottom: 0.75rem; }}
    p {{ font-size: 1.125rem; line-height: 1.6; max-width: 40rem; text-align: center; }}
    .badge {{ display: inline-block; background: var(--accent); color: #000; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 1rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; width: 100%; max-width: 48rem; }}
    .card {{ background: rgba(255,255,255,0.05); border-radius: 0.75rem; padding: 1.5rem; text-align: center; }}
    .build {{ transition: all 0.5s ease; }}
    .hidden {{ opacity: 0; transform: translateY(20px); }}
    .visible {{ opacity: 1; transform: translateY(0); }}
    @media (max-width: 640px) {{ h1 {{ font-size: 2rem; }} .slide {{ padding: 2rem; }} }}
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    const {{ useState, useEffect, useCallback, useRef }} = React;

    /* ---- Slide components ---- */
    function Cover({{ kicker, title, subtitle }}) {{
      return (
        <div className="slide" style={{textAlign: 'center'}}>
          {{kicker && <span className="badge">{{kicker}}</span>}}
          <h1>{{title}}</h1>
          {{subtitle && <p style={{opacity: 0.7}}>{{subtitle}}</p>}}
        </div>
      );
    }}

    function Slide({{ children, center, title }}) {{
      return (
        <div className="slide" style={{center ? {{textAlign: 'center'}} : {{alignItems: 'flex-start', paddingLeft: '6rem'}}}}>
          {{title && <h2 style={{marginBottom: '2rem'}}>{{title}}</h2>}}
          {{children}}
        </div>
      );
    }}

    function Build({{ children, at, step }}) {{
      return <div className={{"build": true, "visible": step >= at, "hidden": step < at}}>{{children}}</div>;
    }}

    /* ---- Slides data ---- */
    {slides_data}

    /* ---- App ---- */
    function App() {{
      const [current, setCurrent] = useState(0);
      const [step, setStep] = useState(0);
      const slides = SLIDES;
      const slide = slides[current];
      const totalBuilds = slide?.builds ?? 1;

      const next = useCallback(() => {{
        if (step + 1 < totalBuilds) {{
          setStep(s => s + 1);
        }} else if (current + 1 < slides.length) {{
          setCurrent(c => c + 1);
          setStep(0);
        }}
      }}, [current, step, totalBuilds, slides.length]);

      const prev = useCallback(() => {{
        if (step > 0) {{
          setStep(s => s - 1);
        }} else if (current > 0) {{
          setCurrent(c => c - 1);
          setStep(slides[c - 1]?.builds ?? 1);
        }}
      }}, [current, step]);

      useEffect(() => {{
        const handler = (e) => {{ if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') {{ e.preventDefault(); next(); }} if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{ e.preventDefault(); prev(); }} }};
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
      }}, [next, prev]);

      return (
        <div className="deck">
          <div className="slide-counter">{{current + 1}} / {{slides.length}}</div>
          <div className="slides-container">
            {{slides.map((s, i) => (
              <div key={{i}} className={{"slide": true, "active": i === current}} style={{display: i === current ? 'flex' : 'none'}}>
                {{s.render(step)}}
              </div>
            ))}}
          </div>
          <div className="nav">
            <button onClick={{prev}} disabled={{current === 0 && step === 0}}>←</button>
            <button onClick={{next}} disabled={{current === slides.length - 1 && step >= totalBuilds - 1}}>→</button>
          </div>
        </div>
      );
    }}

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
```

Requirements:
- Every slide must have a unique, engaging visual identity
- Use the color palette: primary=#6366f1, accent=#22d3ee, bg=#0f0f1a
- Include: Cover slide with topic, 4-6 content slides with title + content, 1 summary/CTA slide
- Use Build components for progressive reveals (at least 2 builds per content slide)
- Content must be substantive and specific to {topic}
- Return ONLY the complete HTML file, no explanation"""


def generate_slides(
    topic: str,
    audience: str = "general",
    api_key: str | None = None,
    learned_context: str = "",
) -> str | None:
    """Generate an interactive slide deck as a single HTML file."""
    prompt = SLIDES_PROMPT.format(
        topic=topic,
        audience=audience,
        style="dark modern interactive",
        slides_data="const SLIDES = [];",
    )
    if learned_context:
        prompt = prompt.replace("const SLIDES = [];", learned_context + "\nconst SLIDES = [];")
    return call_llm(prompt, max_tokens=8000, temperature=0.4, api_key=api_key)
