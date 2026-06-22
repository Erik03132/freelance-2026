// dashboard/src/pages/scheduler.tsx
import { useEffect, useState } from 'react';
import ArticleCard from '../components/ArticleCard';
import ArticleForm from '../components/ArticleForm';
import StatsPanel from '../components/StatsPanel';
import type { Article } from '@prisma/client';

export default function Scheduler() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [showForm, setShowForm] = useState(false);

  const load = async () => {
    const res = await fetch('/api/articles');
    const data = await res.json();
    setArticles(data);
  };

  useEffect(() => {
    load();
  }, []);

  const onCreate = async (newArticle: Partial<Article>) => {
    await fetch('/api/articles', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newArticle),
    });
    setShowForm(false);
    load();
  };

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold mb-6">📅 Планировщик статей</h1>

      <StatsPanel articles={articles} />

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Запланированные материалы</h2>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 hover:bg-indigo-500 text-white py-2 px-4 rounded transition"
        >
          + Новая статья
        </button>
      </div>

      <section className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map(a => (
          <ArticleCard key={a.id} article={a} refresh={load} />
        ))}
      </section>

      {showForm && <ArticleForm onClose={() => setShowForm(false)} onSave={onCreate} />}
    </main>
  );
}
