import { PlaywrightCrawler } from 'crawlee';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL || 'redis://redis:6379/0');
const queue = process.env.CRAWL_QUEUE || 'hermes:crawler:jobs';
const resultPrefix = process.env.CRAWL_RESULT_PREFIX || 'hermes:crawler:result:';
const allowed = new Set((process.env.BROWSER_ALLOWED_DOMAINS || '').split(',').map(x => x.trim().toLowerCase()).filter(Boolean));

function allowedUrl(raw) {
  const url = new URL(raw);
  if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Only HTTP(S) URLs are allowed');
  if (allowed.size && ![...allowed].some(domain => url.hostname === domain || url.hostname.endsWith(`.${domain}`))) {
    throw new Error(`Domain is not allowlisted: ${url.hostname}`);
  }
  return url.toString();
}

async function processJob(job) {
  const items = [];
  const crawler = new PlaywrightCrawler({
    maxRequestsPerCrawl: Math.min(Number(job.max_requests || 100), 1000),
    maxConcurrency: Number(process.env.CRAWL_CONCURRENCY || 4),
    requestHandlerTimeoutSecs: 45,
    async requestHandler({ request, page, enqueueLinks }) {
      const selector = job.selector || 'body';
      const values = await page.locator(selector).allTextContents();
      items.push({ url: request.loadedUrl || request.url, title: await page.title(), text: values.join('\n').slice(0, 100000) });
      await enqueueLinks({ strategy: 'same-domain' });
    },
  });
  await crawler.run(job.start_urls.map(allowedUrl));
  await redis.set(`${resultPrefix}${job.id}`, JSON.stringify({ id: job.id, status: 'succeeded', items, count: items.length }), 'EX', 86400);
}

while (true) {
  const entry = await redis.blpop(queue, 5);
  if (!entry) continue;
  const job = JSON.parse(entry[1]);
  try { await processJob(job); }
  catch (error) { await redis.set(`${resultPrefix}${job.id}`, JSON.stringify({ id: job.id, status: 'failed', error: String(error) }), 'EX', 86400); }
}
