import rss from '@astrojs/rss';
import { readdirSync, readFileSync } from 'fs';

const postsDir = new URL('../content/blog/', import.meta.url);
let posts = [];
try {
  const files = readdirSync(postsDir);
  posts = files.filter(f => f.endsWith('.md')).map(f => {
    const frontmatter = {};
    const content = readFileSync(new URL(f, postsDir), 'utf-8');
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (match) {
      match[1].split('\n').forEach(line => {
        const kv = line.match(/^(\w+):\s*(.+)$/);
        if (kv) frontmatter[kv[1]] = kv[2].replace(/^["']|["']$/g, '');
      });
    }
    return { slug: f.replace(/\.md$/, ''), ...frontmatter };
  });
} catch {}

export async function GET(context) {
  return rss({
    title: 'AI Bureau',
    description: 'AI-агенты, голосовые боты, RAG, приватные LLM',
    site: context.site || 'https://ai-bureau.pro',
    items: posts.map(p => ({
      title: p.title || p.slug,
      description: p.description || '',
      pubDate: p.pubDate ? new Date(p.pubDate) : new Date(),
      link: `/blog/${p.slug}/`,
    })),
    customData: `<language>ru</language>`,
  });
}
