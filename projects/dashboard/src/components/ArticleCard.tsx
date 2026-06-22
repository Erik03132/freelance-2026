// dashboard/src/components/ArticleCard.tsx
import { useState } from 'react';
import type { Article } from '@prisma/client';
import PreviewModal from './PreviewModal';

function platformIcon(p: string) {
  return `/icons/${p}.svg`;
}

export default function ArticleCard({ article, refresh }: { article: Article; refresh: () => void }) {
  const [previewOpen, setPreviewOpen] = useState(false);

  const markPosted = async () => {
    await fetch(`/api/articles/${article.id}?action=mark-posted`, { method: 'POST' });
    refresh();
  };

  return (
    <div className="card backdrop-blur-lg bg-white/10 rounded-xl p-4 hover:shadow-xl transition-shadow">
      <h3 className="text-xl font-semibold">{article.title}</h3>
      <div className="flex gap-2 my-2">
        {article.platforms.map(p => (
          <img key={p} src={platformIcon(p)} alt={p} className="w-5 h-5" />
        ))}
      </div>
      <p className="text-sm text-gray-300">
        Запланировано: {new Date(article.scheduleAt).toLocaleString()}
      </p>
      <p className="mt-1">
        Статус:{' '}
        <span
          className={`font-medium ${
            article.status === 'Posted'
              ? 'text-green-400'
              : article.status === 'Ready'
              ? 'text-yellow-300'
              : 'text-gray-500'
          }`}
        >
          {article.status}
        </span>
      </p>
      {article.previewImg && (
        <img src={article.previewImg} alt="preview" className="mt-2 w-full h-32 object-cover rounded-lg" />
      )}
      <div className="flex justify-end gap-2 mt-3">
        <button onClick={() => setPreviewOpen(true)} className="bg-indigo-600 hover:bg-indigo-500 text-white py-1 px-3 rounded transition">
          Preview
        </button>
        {article.status !== 'Posted' && (
          <button onClick={markPosted} className="bg-emerald-600 hover:bg-emerald-500 text-white py-1 px-3 rounded transition">
            Mark as Posted
          </button>
        )}
      </div>
      {previewOpen && <PreviewModal articleId={article.id} onClose={() => setPreviewOpen(false)} />}
    </div>
  );
}
