// dashboard/src/pages/api/articles/index.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '../../../lib/prisma';

export default async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.method === 'GET') {
    const articles = await prisma.article.findMany({ orderBy: { scheduleAt: 'asc' } });
    return res.json(articles);
  }

  if (req.method === 'POST') {
    const { title, content, platforms, scheduleAt, previewImg } = req.body;
    const article = await prisma.article.create({
      data: {
        title,
        content,
        platforms,
        scheduleAt: new Date(scheduleAt),
        status: 'Planned',
        previewImg,
      },
    });
    return res.status(201).json(article);
  }

  res.setHeader('Allow', ['GET', 'POST']);
  res.status(405).end(`Method ${req.method} Not Allowed`);
};
