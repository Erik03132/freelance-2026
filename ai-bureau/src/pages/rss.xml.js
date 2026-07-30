import rss from '@astrojs/rss';

const postEntries = Object.entries(import.meta.glob('../content/blog/*.md', { eager: true }));

export async function GET(context) {
  const items = postEntries.map(([path, post]) => {
    const slug = path.split('/').pop().replace('.md', '');
    return {
      title: post.frontmatter.title || slug,
      description: post.frontmatter.description || '',
      pubDate: post.frontmatter.pubDate ? new Date(post.frontmatter.pubDate) : new Date(),
      link: `/blog/${slug}/`,
    };
  });

  return rss({
    title: 'AI Bureau',
    description: 'AI-агенты, голосовые боты, RAG, приватные LLM',
    site: context.site || 'https://ai-bureau.pro',
    items,
    customData: `<language>ru</language>`,
  });
}
