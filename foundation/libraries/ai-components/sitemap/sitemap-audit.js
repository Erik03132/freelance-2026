/**
 * Sitemap-First Audit — быстрый SEO-анализ без полного краулинга
 * 
 * Использование:
 *   node scripts/sitemap-audit.js example.com
 * 
 * Результат:
 *   - Отчёт в консоль
 *   - CSV файл: audit-report-{domain}-{date}.csv
 */

import { generateReport } from './sitemap-parser.js';
import { analyzePatterns, generateRecommendations } from './demand-matcher.js';
import fs from 'fs';

async function main() {
  const domain = process.argv[2];
  
  if (!domain) {
    console.error('❌ Укажите домен: node scripts/sitemap-audit.js example.com');
    process.exit(1);
  }
  
  console.log(`\n🚀 Sitemap-First Audit: ${domain}\n`);
  console.log('='.repeat(60));
  
  // 1. Парсим sitemap
  const report = await generateReport(domain);
  
  console.log(`\n📊 СТАТИСТИКА:`);
  console.log(`   Всего URL: ${report.totalUrls}`);
  console.log(`   Паттернов: ${report.patterns.length}`);
  
  // 2. Анализируем паттерны
  const analysis = analyzePatterns(report.patterns);
  
  console.log(`\n📈 АНАЛИЗ ПАТТЕРНОВ:`);
  console.log(`   💪 Сильные: ${analysis.strong.length}`);
  console.log(`   😐 Средние: ${analysis.medium.length}`);
  console.log(`   ⚠️  Слабые: ${analysis.weak.length}`);
  
  // 3. Показываем топ паттерны
  console.log(`\n🏆 ТОП-5 СИЛЬНЫХ ПАТТЕРНОВ:`);
  analysis.strong
    .sort((a, b) => b.avgScore - a.avgScore)
    .slice(0, 5)
    .forEach((p, i) => {
      console.log(`   ${i + 1}. [${p.avgScore}] ${p.pattern} (${p.count} URL, ${p.pageType})`);
    });
  
  console.log(`\n⚠️  ТОП-5 СЛАБЫХ ПАТТЕРНОВ:`);
  analysis.weak
    .sort((a, b) => a.avgScore - b.avgScore)
    .slice(0, 5)
    .forEach((p, i) => {
      console.log(`   ${i + 1}. [${p.avgScore}] ${p.pattern} (${p.count} URL, ${p.pageType})`);
    });
  
  // 4. Генерируем рекомендации
  const recommendations = generateRecommendations(analysis);
  
  console.log(`\n💡 РЕКОМЕНДАЦИИ:`);
  recommendations.forEach(rec => {
    console.log(`   ${rec}`);
  });
  
  // 5. Сохраняем CSV отчёт
  const date = new Date().toISOString().split('T')[0];
  const csvPath = `audit-report-${domain}-${date}.csv`;
  
  const csvContent = [
    'Pattern,PageType,Count,AvgScore,Status',
    ...report.patterns.map(p => {
      const evalResult = analysis.strong.find(a => a.pattern === p.pattern) ||
                        analysis.medium.find(a => a.pattern === p.pattern) ||
                        analysis.weak.find(a => a.pattern === p.pattern);
      return `${p.pattern},${p.pageType},${p.count},${evalResult?.avgScore || 0},${evalResult?.status || 'unknown'}`;
    }),
  ].join('\n');
  
  fs.writeFileSync(csvPath, csvContent, 'utf-8');
  console.log(`\n💾 Отчёт сохранён: ${csvPath}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ Аудит завершён!\n');
}

main().catch(error => {
  console.error('❌ Ошибка:', error);
  process.exit(1);
});
