/**
 * Demand Matcher — сопоставление URL с поисковым спросом
 * 
 * Анализирует URL-паттерны и определяет, есть ли на них поисковый спрос.
 * Помогает найти "пустые" посадочные страницы.
 */

/**
 * Извлекает ключевые слова из URL
 * @param {string} url - URL страницы
 * @returns {Array<string>} - ключевые слова
 */
export function extractKeywordsFromUrl(url) {
  try {
    const urlObj = new URL(url);
    const path = urlObj.pathname;
    
    // Убираем расширения (.html, .php)
    const cleanPath = path.replace(/\.(html?|php|aspx?)$/i, '');
    
    // Разбиваем на сегменты
    const segments = cleanPath.split('/').filter(s => s);
    
    // Берём последние 2-3 сегмента как ключевые слова
    const keywords = segments
      .slice(-3)
      .map(segment => {
        // Заменяем дефисы и подчёркивания на пробелы
        return segment.replace(/[-_]/g, ' ').trim();
      })
      .filter(s => s.length > 2); // Убираем короткие
    
    return keywords;
    
  } catch (error) {
    return [];
  }
}

/**
 * Генерирует поисковые запросы из URL
 * @param {string} url - URL страницы
 * @returns {Array<string>} - потенциальные поисковые запросы
 */
export function generateSearchQueries(url) {
  const keywords = extractKeywordsFromUrl(url);
  
  if (keywords.length === 0) return [];
  
  const queries = [];
  
  // Комбинируем ключевые слова
  if (keywords.length >= 2) {
    queries.push(keywords.join(' '));
  }
  
  // Добавляем отдельные ключевые слова
  queries.push(...keywords);
  
  return queries;
}

/**
 * Оценивает потенциал URL на основе структуры
 * @param {string} url - URL страницы
 * @param {Object} urlData - данные из sitemap (lastmod, priority)
 * @returns {Object} - оценка
 */
export function evaluateUrlPotential(url, urlData = {}) {
  const keywords = extractKeywordsFromUrl(url);
  const queries = generateSearchQueries(url);
  
  // Эвристики для оценки потенциала
  let score = 50; // Базовый скор
  
  // Длинные URL с ключевыми словами — хороший знак
  if (keywords.length >= 2) score += 20;
  if (keywords.some(k => k.length > 5)) score += 10;
  
  // Приоритет из sitemap
  if (urlData.priority) {
    const priority = parseFloat(urlData.priority);
    score += priority * 20; // 0-20 баллов
  }
  
  // Частота обновлений
  if (urlData.changefreq === 'daily' || urlData.changefreq === 'weekly') {
    score += 10;
  }
  
  // Дата последнего обновления
  if (urlData.lastmod) {
    const lastmod = new Date(urlData.lastmod);
    const daysSinceUpdate = (Date.now() - lastmod.getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceUpdate < 30) score += 15; // Свежий контент
    else if (daysSinceUpdate > 365) score -= 20; // Устаревший
  }
  
  // Определяем статус
  let status = 'medium';
  if (score >= 70) status = 'high';
  else if (score < 40) status = 'low';
  
  return {
    url,
    keywords,
    queries,
    score: Math.max(0, Math.min(100, score)),
    status,
  };
}

/**
 * Анализирует паттерны URL и находит слабые места
 * @param {Array<Object>} patterns - паттерны из sitemap-parser
 * @returns {Object} - анализ
 */
export function analyzePatterns(patterns) {
  const analysis = {
    strong: [],
    medium: [],
    weak: [],
  };
  
  patterns.forEach(pattern => {
    const avgScore = pattern.examples.reduce((sum, url) => {
      const evaluation = evaluateUrlPotential(url);
      return sum + evaluation.score;
    }, 0) / pattern.examples.length;
    
    const result = {
      pattern: pattern.pattern,
      pageType: pattern.pageType,
      count: pattern.count,
      avgScore: Math.round(avgScore),
      status: avgScore >= 70 ? 'strong' : avgScore >= 40 ? 'medium' : 'weak',
    };
    
    if (result.status === 'strong') analysis.strong.push(result);
    else if (result.status === 'medium') analysis.medium.push(result);
    else analysis.weak.push(result);
  });
  
  return analysis;
}

/**
 * Генерирует рекомендации по оптимизации
 * @param {Object} analysis - результат analyzePatterns
 * @returns {Array<string>} - рекомендации
 */
export function generateRecommendations(analysis) {
  const recommendations = [];
  
  // Слабые паттерны — нужно улучшить
  if (analysis.weak.length > 0) {
    recommendations.push(
      `⚠️ Найдено ${analysis.weak.length} слабых паттернов URL. ` +
      `Рекомендуется: улучшить контент, добавить ключевые слова в URL.`
    );
  }
  
  // Много страниц одного типа
  const largePatterns = analysis.medium.filter(p => p.count > 50);
  if (largePatterns.length > 0) {
    recommendations.push(
      `📊 Найдено ${largePatterns.length} больших паттернов (>50 URL). ` +
      `Проверьте: нет ли дублей, достаточно ли уникального контента.`
    );
  }
  
  // Мало сильных страниц
  if (analysis.strong.length < 5) {
    recommendations.push(
      `💡 Только ${analysis.strong.length} сильных паттернов. ` +
      `Рекомендуется: создать больше качественных посадочных страниц.`
    );
  }
  
  return recommendations;
}
