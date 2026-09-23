import React, { useRef, useEffect } from 'react';

interface Node {
  x: number; y: number;
  vx: number; vy: number;
  label: string;
  r: number;
  phase: number;
  group: number;
}

interface Edge {
  from: number; to: number;
  baseOpacity: number;
}

const GROUPS = [
  { accent: 'oklch(0.5 0.16 240)',  dim: 'oklch(0.5 0.16 240 / 0.6)' },
  { accent: 'oklch(0.65 0.15 85)',   dim: 'oklch(0.65 0.15 85 / 0.6)' },
  { accent: 'oklch(0.55 0.2 145)',   dim: 'oklch(0.55 0.2 145 / 0.6)' },
];

const LABELS = [
  'AI', 'RAG', 'LLM', 'AGENTS',
  'VISION', 'NLP', 'AUDIO', 'ROBOT',
  'INFRA', 'OPS', 'VECTOR', 'GRAPH',
  'STREAM', 'TRAIN', 'INFER', 'DATA',
  'EDGE', 'CLOUD', 'API', 'SEARCH',
  'MEMORY', 'TOOLS', 'PLAN', 'CODE',
];

const InteractiveNeuralGraph: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let W = 0, H = 0;
    let time = 0;
    const mouse = { x: -9999, y: -9999, prevX: -9999, prevY: -9999 };

    const N = LABELS.length;

    const nodes: Node[] = Array.from({ length: N }, (_, i) => ({
      x: 0, y: 0, vx: 0, vy: 0,
      label: LABELS[i],
      r: 2.5 + Math.random() * 4,
      phase: Math.random() * Math.PI * 2,
      group: i < 4 ? 0 : i < 12 ? 1 : 2,
    }));

    const edges: Edge[] = [];
    for (let i = 0; i < N; i++) {
      const conn = 2 + Math.floor(Math.random() * 3);
      for (let c = 0; c < conn; c++) {
        let j = Math.floor(Math.random() * N);
        if (j === i) j = (j + 1) % N;
        const key = [Math.min(i, j), Math.max(i, j)].join(',');
        if (!edges.some(e => [e.from, e.to].sort().join(',') === key)) {
          edges.push({ from: i, to: j, baseOpacity: 0.06 + Math.random() * 0.2 });
        }
      }
    }

    const particles = edges.map((_, i) => ({
      edgeIdx: i, t: Math.random(), speed: 0.0015 + Math.random() * 0.0035,
    }));

    function resize() {
      const parent = canvas!.parentElement!;
      W = parent.clientWidth;
      H = parent.clientHeight;
      const dpr = window.devicePixelRatio || 1;
      canvas!.width = W * dpr;
      canvas!.height = H * dpr;
      canvas!.style.width = `${W}px`;
      canvas!.style.height = `${H}px`;
      ctx!.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function initPositions() {
      const pad = 60;
      for (const n of nodes) {
        n.x = pad + Math.random() * (W - pad * 2);
        n.y = pad + Math.random() * (H - pad * 2);
        n.vx = 0; n.vy = 0;
      }
    }

    resize();
    initPositions();

    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement!);
    window.addEventListener('resize', resize);

    function onMouse(e: MouseEvent) {
      const rect = canvas!.getBoundingClientRect();
      mouse.prevX = mouse.x;
      mouse.prevY = mouse.y;
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    }
    function onLeave() {
      mouse.prevX = mouse.x;
      mouse.prevY = mouse.y;
      mouse.x = -9999;
      mouse.y = -9999;
    }
    canvas.addEventListener('mousemove', onMouse);
    canvas.addEventListener('mouseleave', onLeave);

    function draw() {
      time += 0.016;
      ctx!.clearRect(0, 0, W, H);

      const REPEL = 800;
      const ATTRACT = 0.015;
      const CENTER = 0.003;
      const DAMP = 0.92;
      const MOUSE_REPEL = 8000;
      const IDEAL_EDGE = 120;

      // Physics
      for (let i = 0; i < N; i++) {
        const a = nodes[i];
        a.vx += (W/2 - a.x) * CENTER;
        a.vy += (H/2 - a.y) * CENTER;

        for (let j = i + 1; j < N; j++) {
          const b = nodes[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const distSq = Math.max(dx * dx + dy * dy, 1);
          const force = REPEL / distSq;
          a.vx += dx * force;
          a.vy += dy * force;
          b.vx -= dx * force;
          b.vy -= dy * force;
        }

        const mdx = a.x - mouse.x;
        const mdy = a.y - mouse.y;
        const mouseDistSq = Math.max(mdx * mdx + mdy * mdy, 1);
        if (mouseDistSq < 20000) {
          const mf = MOUSE_REPEL / mouseDistSq;
          a.vx += mdx * mf;
          a.vy += mdy * mf;
        }
      }

      for (const e of edges) {
        const a = nodes[e.from];
        const b = nodes[e.to];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        if (dist > IDEAL_EDGE) {
          const f = (dist - IDEAL_EDGE) * ATTRACT;
          const fx = (dx / dist) * f;
          const fy = (dy / dist) * f;
          a.vx += fx;
          a.vy += fy;
          b.vx -= fx;
          b.vy -= fy;
        }
      }

      for (const n of nodes) {
        n.vx *= DAMP;
        n.vy *= DAMP;
        n.x += n.vx;
        n.y += n.vy;
        n.x = Math.max(10, Math.min(W - 10, n.x));
        n.y = Math.max(10, Math.min(H - 10, n.y));
      }

      // Draw edges
      for (const e of edges) {
        const a = nodes[e.from];
        const b = nodes[e.to];
        const mx = (a.x + b.x) / 2;
        const my = (a.y + b.y) / 2;
        const dm = Math.sqrt((mx - mouse.x) ** 2 + (my - mouse.y) ** 2);
        const glow = Math.max(0, 1 - dm / 150);

        ctx!.beginPath();
        ctx!.moveTo(a.x, a.y);
        ctx!.lineTo(b.x, b.y);
        const alpha = e.baseOpacity + glow * 0.5;
        ctx!.strokeStyle = `oklch(0.5 0.16 240 / ${Math.min(alpha, 0.9)})`;
        ctx!.lineWidth = 0.4 + glow * 2.5;
        if (glow > 0.05) {
          ctx!.shadowColor = `oklch(0.5 0.16 240 / ${glow * 0.3})`;
          ctx!.shadowBlur = 12 * glow;
        } else {
          ctx!.shadowBlur = 0;
        }
        ctx!.stroke();
        ctx!.shadowBlur = 0;
      }

      // Particles
      for (const p of particles) {
        const e = edges[p.edgeIdx];
        if (!e) continue;
        const a = nodes[e.from];
        const b = nodes[e.to];
        p.t += p.speed;
        if (p.t > 1) p.t -= 1;
        const x = a.x + (b.x - a.x) * p.t;
        const y = a.y + (b.y - a.y) * p.t;
        const flash = Math.sin(p.t * Math.PI);
        ctx!.beginPath();
        ctx!.arc(x, y, 1 + flash * 0.5, 0, Math.PI * 2);
        ctx!.fillStyle = `oklch(0.65 0.15 85 / ${0.2 + flash * 0.5})`;
        ctx!.fill();
      }

      // Draw nodes
      for (const n of nodes) {
        const dm = Math.sqrt((n.x - mouse.x) ** 2 + (n.y - mouse.y) ** 2);
        const hover = Math.max(0, 1 - dm / 120);
        const pulse = 0.85 + 0.15 * Math.sin(time * 1.5 + n.phase);
        const r = n.r * pulse + hover * 5;
        const grp = GROUPS[n.group];

        if (hover > 0.05) {
          ctx!.beginPath();
          ctx!.arc(n.x, n.y, r + 12 * hover, 0, Math.PI * 2);
          ctx!.fillStyle = `oklch(0.5 0.16 240 / ${hover * 0.12})`;
          ctx!.fill();
        }

        ctx!.beginPath();
        ctx!.arc(n.x, n.y, r, 0, Math.PI * 2);
        ctx!.fillStyle = hover > 0.3 ? grp.accent : grp.dim;
        ctx!.fill();

        ctx!.beginPath();
        ctx!.arc(n.x - r * 0.15, n.y - r * 0.15, r * 0.35, 0, Math.PI * 2);
        ctx!.fillStyle = 'oklch(1 0 0 / 0.4)';
        ctx!.fill();

        if (hover > 0.4) {
          ctx!.font = '500 10px "JetBrains Mono", monospace';
          ctx!.fillStyle = 'oklch(0.15 0.01 260)';
          ctx!.fillText(n.label, n.x + r + 7, n.y + 3);
        }
      }

      animId = requestAnimationFrame(draw);
    }

    draw();

    return () => {
      cancelAnimationFrame(animId);
      ro.disconnect();
      window.removeEventListener('resize', resize);
      canvas.removeEventListener('mousemove', onMouse);
      canvas.removeEventListener('mouseleave', onLeave);
    };
  }, []);

  return <canvas ref={canvasRef} className="hero-graph" />;
};

export default InteractiveNeuralGraph;
