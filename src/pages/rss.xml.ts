import { getCollection } from 'astro:content';

export async function GET() {
  const posts = await getCollection('blog');
  const sorted = posts.sort((a, b) =>
    new Date(b.data.date) - new Date(a.data.date)
  );

  return new Response(
    await generateRss(sorted),
    {
      headers: {
        'Content-Type': 'application/xml',
        'Cache-Control': 'public, max-age=3600',
      },
    }
  );
}

async function generateRss(posts) {
  const site = 'https://ai-bureau.pro';
  const items = posts
    .map((post) => `
    <item>
      <title>${escapeXml(post.data.title)}</title>
      <link>${site}/blog/${post.slug}/</link>
      <pubDate>${new Date(post.data.date).toUTCString()}</pubDate>
      <description>${escapeXml(post.data.description)}</description>
    </item>
  `)
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>AI Bureau — автономные AI-системы для бизнеса</title>
    <description>AI-агенты с RAG, голосовые боты, чат-боты с базой знаний, private LLM, AI-консалтинг.</description>
    <link>${site}</link>
    <language>ru-RU</language>
    <atom:link href="${site}/rss.xml" rel="self" type="application/rss+xml"/>
    ${items}
  </channel>
</rss>`;
}

function escapeXml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
