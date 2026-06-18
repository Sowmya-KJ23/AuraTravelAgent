import Parser from 'rss-parser';

const parser = new Parser({
  customFields: {
    item: ['source'],
  }
});

/**
 * Builds the Google News or Official Blog RSS URL based on parameters.
 * @param {Object} options
 * @param {string} [options.query] - Search query.
 * @param {string} [options.topic] - News topic (e.g., TECHNOLOGY, BUSINESS).
 * @param {boolean} [options.official] - Whether to fetch from the official Google Blog.
 * @param {string} [options.geo] - Geolocation country code (e.g., US, IN, GB).
 * @param {string} [options.lang] - Language code (e.g., en, es, fr).
 * @returns {string} The formatted RSS feed URL.
 */
export function getFeedUrl({ query, topic, official, geo = 'US', lang = 'en' } = {}) {
  if (official) {
    return 'https://blog.google/rss/';
  }

  const ceid = `${geo}:${lang}`;
  const baseUrl = 'https://news.google.com';

  if (query) {
    const encodedQuery = encodeURIComponent(query);
    return `${baseUrl}/rss/search?q=${encodedQuery}&hl=${lang}&gl=${geo}&ceid=${ceid}`;
  }

  if (topic) {
    const upperTopic = topic.toUpperCase();
    return `${baseUrl}/news/rss/headlines/section/topic/${upperTopic}?hl=${lang}&gl=${geo}&ceid=${ceid}`;
  }

  // Default: Top Headlines
  return `${baseUrl}/rss?hl=${lang}&gl=${geo}&ceid=${ceid}`;
}

/**
 * Fetches and parses news from the calculated RSS feed.
 * @param {Object} options - Feed URL building options.
 * @returns {Promise<Object>} The parsed feed containing title and items.
 */
export async function fetchNews(options = {}) {
  const url = getFeedUrl(options);
  try {
    const feed = await parser.parseURL(url);
    
    // Process items for consistency
    const items = feed.items.map(item => {
      // Extract publisher source name
      // Google News items usually end with " - Publisher Name"
      let publisher = '';
      let cleanTitle = item.title || '';
      
      if (!options.official) {
        const hyphenIdx = cleanTitle.lastIndexOf(' - ');
        if (hyphenIdx !== -1) {
          publisher = cleanTitle.substring(hyphenIdx + 3).trim();
          cleanTitle = cleanTitle.substring(0, hyphenIdx).trim();
        } else if (item.source && item.source.$) {
          publisher = item.source._ || item.source.$ || '';
        }
      } else {
        publisher = 'Official Google Blog';
      }

      return {
        title: cleanTitle,
        link: item.link,
        pubDate: item.pubDate ? new Date(item.pubDate) : null,
        publisher: publisher || 'Unknown',
        contentSnippet: item.contentSnippet || '',
      };
    });

    return {
      title: feed.title,
      description: feed.description,
      link: feed.link,
      items,
    };
  } catch (error) {
    throw new Error(`Failed to fetch news from ${url}: ${error.message}`);
  }
}
