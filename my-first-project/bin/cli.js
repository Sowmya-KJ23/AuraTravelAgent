#!/usr/bin/env node

import { program } from 'commander';
import chalk from 'chalk';
import open from 'open';
import readline from 'readline';
import { fetchNews } from '../src/news-service.js';

// Helper to format "time ago"
function timeAgo(date) {
  if (!date) return '';
  const seconds = Math.floor((new Date() - date) / 1000);
  
  if (seconds < 0) return 'just now'; // handles minor clock skew
  
  let interval = Math.floor(seconds / 31536000);
  if (interval >= 1) return `${interval}y ago`;
  interval = Math.floor(seconds / 2592000);
  if (interval >= 1) return `${interval}mo ago`;
  interval = Math.floor(seconds / 86400);
  if (interval >= 1) return `${interval}d ago`;
  interval = Math.floor(seconds / 3600);
  if (interval >= 1) return `${interval}h ago`;
  interval = Math.floor(seconds / 60);
  if (interval >= 1) return `${interval}m ago`;
  return 'just now';
}

async function main() {
  program
    .name('google-news')
    .description('A command-line tool to fetch the latest news from Google')
    .version('1.0.0')
    .option('-s, --search <query>', 'search Google News for specific keywords')
    .option('-t, --topic <topic>', 'filter by topic (e.g. TECHNOLOGY, BUSINESS, SCIENCE, HEALTH, SPORTS, ENTERTAINMENT)')
    .option('-o, --official', 'fetch news from the official Google Blog')
    .option('-l, --limit <number>', 'limit the number of articles to display', '10')
    .option('-g, --geo <country>', 'country code for localized news (e.g., US, IN, GB, CA)', 'US')
    .option('-hl, --lang <language>', 'language code for localized news (e.g., en, es, hi)', 'en')
    .option('-j, --json', 'output raw JSON data')
    .action(async (options) => {
      const limit = parseInt(options.limit, 10);
      if (isNaN(limit) || limit <= 0) {
        console.error(chalk.red('Error: Limit must be a positive number.'));
        process.exit(1);
      }

      const geo = options.geo.toUpperCase();
      const lang = options.lang.toLowerCase();

      try {
        if (!options.json) {
          console.log(chalk.cyan('Fetching news...'));
        }

        const feed = await fetchNews({
          query: options.search,
          topic: options.topic,
          official: options.official,
          geo,
          lang
        });

        const articles = feed.items.slice(0, limit);

        if (options.json) {
          console.log(JSON.stringify({
            feedTitle: feed.title,
            feedDescription: feed.description,
            feedLink: feed.link,
            articles: articles.map(a => ({
              title: a.title,
              publisher: a.publisher,
              pubDate: a.pubDate,
              link: a.link,
              snippet: a.contentSnippet
            }))
          }, null, 2));
          return;
        }

        if (articles.length === 0) {
          console.log(chalk.yellow('\nNo articles found matching the criteria.'));
          return;
        }

        // Print header
        console.clear();
        console.log(chalk.bold.gradient ? chalk.bold.cyan(' Google News CLI ') : chalk.bold.cyan('=== Google News CLI ==='));
        console.log(chalk.gray(`Source: ${feed.title}`));
        if (feed.description) {
          console.log(chalk.gray(`Description: ${feed.description}`));
        }
        console.log(chalk.gray('========================================================\n'));

        // Print articles
        articles.forEach((article, index) => {
          const num = chalk.cyan(`[${index + 1}]`);
          const title = chalk.white.bold(article.title);
          const meta = chalk.dim(`(Source: ${chalk.green(article.publisher)} | ${timeAgo(article.pubDate)})`);
          
          console.log(`${num} ${title}`);
          console.log(`    ${meta}`);
          // Add terminal-friendly link (clickable in many modern terminals)
          console.log(`    Link: ${chalk.blue.underline(article.link)}\n`);
        });

        // Interactive open prompt
        const rl = readline.createInterface({
          input: process.stdin,
          output: process.stdout
        });

        const askToOpen = () => {
          rl.question(chalk.yellow('Enter an article number to open it in your browser, or press Enter to exit: '), async (input) => {
            const trimmed = input.trim();
            if (trimmed === '') {
              rl.close();
              process.exit(0);
            }

            const selection = parseInt(trimmed, 10);
            if (isNaN(selection) || selection < 1 || selection > articles.length) {
              console.log(chalk.red(`Please enter a number between 1 and ${articles.length}.\n`));
              askToOpen();
            } else {
              const selectedArticle = articles[selection - 1];
              console.log(chalk.green(`Opening: "${selectedArticle.title}"...`));
              await open(selectedArticle.link);
              console.log();
              askToOpen();
            }
          });
        };

        askToOpen();

      } catch (error) {
        console.error(chalk.red('\nAn error occurred:'), error.message);
        process.exit(1);
      }
    });

  program.parse(process.argv);
}

main();
