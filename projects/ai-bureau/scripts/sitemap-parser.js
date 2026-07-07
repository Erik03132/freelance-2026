/**
 * Sitemap Parser — извлечение URL из sitemap.xml
 * 
 * Парсит sitemap.xml и выделяет паттерны URL для анализа.
 * Быстрее полного краулинга в 5-10 раз.
 */

import { parseString } from 'xml2js';
import { promisify } from 'util';

const parseXML = promisify(parseString);

/**
 * Парсит sitemap.xml и возвращает все URL
 * @param {string} sitemapUrl - URL sitemap.xml
 * @returns {Promise<Array<{url: string, lastmod: string, changefreq: string, priority: string}>>}
 */
export async function parseSitemap(sitemapUrl) {
  try {
    const response = await fetch(sitemapUrl);
    const xml = await response.text();
    
    const result = await parseXML(xml);
    
    // Проверяем, это sitemap index или обычный sitemap
    if (result.sitemapindex) {
      // Sitemap index — нужно загрузить все дочерние sitemap
      const sitemaps = result.sitemapindex.sitemap || [];
      const allUrls = [];
      
      for (const sitemap of sitemaps) {
        const childUrl = sitemap.loc[0];
        const childUrls = await parseSitemap(childUrl);
        allUrls.push(...childUrls);
      }
      
      return allUrls;
    }
    
    // Обычный sitemap
    const urlset = result.urlset?.url || [];
    
    return urlset.map(urlObj => ({
      url: urlObj.loc[0],
      lastmod: urlObj.lastmod?.[0] || null,
      changefreq: urlObj.changefreq?.[0] || null,
      priority: urlObj.priority?.[0] || null,
    }));
    
  } catch (error) {
    console.error(`❌ Ошибка парсинга sitemap ${sitemapUrl}:`, error.message);
    return [];
  }
}

/**
 * Выделяет паттерны из URL
 * @param {Array<string>} urls - список URL
 * @returns {Object} - паттерны и их частота
 */
export function extractPatterns(urls) {
  const patterns = {};
  
  urls.forEach(url => {
    try {
      const urlObj = new URL(url);
      const path = urlObj.pathname;
      
      // Выделяем сегменты пути
      const segments = path.split('/').filter(s => s);
      
      if (segments.length === 0) {
        patterns['/'] = (patterns['/'] || 0) + 1;
        return;
      }
      
      // Создаём паттерн из первых 2-3 сегментов
      const pattern = '/' + segments.slice(0, Math.min(2, segments.length)).join('/');
      
      // Определяем тип страницы
      let pageType = 'other';
      if (pattern.includes('/product')) pageType = 'product';
      else if (pattern.includes('/category')) pageType = 'category';
      else if (pattern.includes('/blog') || pattern.includes('/article')) pageType = 'blog';
      else if (pattern.includes('/service')) pageType = 'service';
      else if (pattern.includes('/about')) pageType = 'about';
      
      if (!patterns[pattern]) {
        patterns[pattern] = {
          count: 0,
          pageType,
          examples: [],
        };
      }
      
      patterns[pattern].count++;
      
      // Сохраняем примеры (максимум 3)
      if (patterns[pattern].examples.length < 3) {
        patterns[pattern].examples.push(url);
      }
      
    } catch (error) {
      // Невалидный URL — пропускаем
    }
  });
  
  return patterns;
}

/**
 * Генерирует отчёт по sitemap
 * @param {string} domain - домен сайта
 * @returns {Promise<Object>} - отчёт
 */
export async function generateReport(domain) {
  const sitemapUrl = `https://${domain}/sitemap.xml`;
  
  console.log(`🔍 Парсинг sitemap: ${sitemapUrl}`);
  const urls = await parseSitemap(sitemapUrl);
  
  console.log(`✅ Найдено URL: ${urls.length}`);
  
  const patterns = extractPatterns(urls.map(u => u.url));
  
  // Сортируем паттерны по количеству
  const sortedPatterns = Object.entries(patterns)
    .sort((a, b) => b[1].count - a[1].count)
    .map(([pattern, data]) => ({
      pattern,
      ...data,
    }));
  
  return {
    domain,
    totalUrls: urls.length,
    patterns: sortedPatterns,
    urls,
  };
}
