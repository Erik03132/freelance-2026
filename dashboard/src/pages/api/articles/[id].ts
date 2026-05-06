// dashboard/src/pages/api/articles/[id].ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '../../../lib/prisma';

export default async (req: NextApiRequest, res: NextApiResponse) => {
  const { id } = req.query;
  if (!id || typeof id !== 'string') {
    return res.status(400).json({ error: 'Invalid ID' });
  }

  if (req.method === 'GET') {
    const article = await prisma.article.findUnique({ where: { id } });
    return res.json(article);
  }

  if (req.method === 'PUT') {
    const data = req.body;
    const article = await prisma.article.update({
      where: { id },
      data: { ...data, updatedAt: new Date() },
    });
    return res.json(article);
  }

  if (req.method === 'POST' && req.query.action === 'mark-posted') {
    const article = await prisma.article.update({
      where: { id },
      data: { status: 'Posted', postedAt: new Date() },
    });
    return res.json(article);
  }

  if (req.method === 'GET' && req.query.action === 'preview') {
    const article = await prisma.article.findUnique({ where: { id } });
    return res.json({ title: article?.title, content: article?.content, previewImg: article?.previewImg });
  }

  res.setHeader('Allow', ['GET', 'PUT', 'POST']);
  res.status(405).end(`Method ${req.method} Not Allowed`);
};
