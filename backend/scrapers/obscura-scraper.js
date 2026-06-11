/**
 * Obscura-based scraper for LinkedIn people and signals
 * Signal-based targeting: Find people → Extract signals → Build profiles
 */

const puppeteer = require('puppeteer');

class ObscuraScraper {
  constructor(options = {}) {
    this.maxConcurrent = options.maxConcurrent || 5;
    this.antiDetection = options.antiDetection !== false;
    this.stealth = options.stealth !== false;
    this.browsers = [];
    this.queue = [];
    this.activeJobs = 0;
  }

  /**
   * Launch browsers with anti-detection settings
   */
  async initialize() {
    console.log(`[Obscura] Initializing ${this.maxConcurrent} browser instances...`);

    const browserPromises = [];
    for (let i = 0; i < this.maxConcurrent; i++) {
      browserPromises.push(
        puppeteer.launch({
          headless: 'new',
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--allow-running-insecure-content',
          ],
        })
      );
    }

    this.browsers = await Promise.all(browserPromises);
    console.log(`[Obscura] ${this.browsers.length} browsers ready`);
  }

  /**
   * Scrape LinkedIn PEOPLE matching criteria + extract their SIGNALS
   * Signal-based targeting: Find people → What they care about → Best angle to reach them
   */
  async scrapeLinkedInPeopleWithSignals(searchParams) {
    const {
      jobTitles = [],           // ["CMO", "VP Marketing"]
      industries = [],          // ["SaaS", "Ecommerce"]
      companySizes = [],        // [100, 5000]
      locations = [],           // ["UK", "US"]
      limit = 50,
    } = searchParams;

    console.log(`[LinkedIn] Searching for people: titles=${jobTitles}, industries=${industries}`);

    // Step 1: Find people matching criteria
    const peopleUrls = this._generateLinkedInPeopleSearchUrls({
      jobTitles,
      industries,
      companySizes,
      locations,
    });

    const people = [];
    for (const url of peopleUrls) {
      const results = await this._scrapeWithBrowser(url, async (page) => {
        await this._antiDetectDelay();
        return await this._extractLinkedInPeopleData(page);
      });
      people.push(...(results || []));
    }

    console.log(`[LinkedIn] Found ${people.length} people`);

    // Step 2: Extract signals for each person
    const peopleWithSignals = [];
    for (const person of people.slice(0, limit)) {
      try {
        console.log(`[LinkedIn] Extracting signals for ${person.name}...`);

        const signals = await this._scrapeWithBrowser(person.profileUrl, async (page) => {
          await this._antiDetectDelay();
          return await this._extractLinkedInSignals(page, person);
        });

        if (signals) {
          peopleWithSignals.push({
            ...person,
            signals,
          });
        }
      } catch (error) {
        console.error(`[LinkedIn] Error extracting signals for ${person.name}:`, error.message);
      }
    }

    console.log(`[LinkedIn] Extracted signals for ${peopleWithSignals.length} people`);
    return peopleWithSignals;
  }

  /**
   * Extract LinkedIn SIGNALS from a person's profile
   * Signals: companies followed, content engagement, articles shared, groups, skills
   */
  async _extractLinkedInSignals(page, person) {
    try {
      const signals = await page.evaluate(() => {
        return {
          // Companies they follow (shows competitive awareness)
          companiesFollowed: Array.from(
            document.querySelectorAll('[data-test-id="company-follow"] a') || []
          ).map(el => el.textContent?.trim()).filter(Boolean),

          // Content they engage with (shows interests)
          recentEngagements: Array.from(
            document.querySelectorAll('[data-test-id="feed-update__engagement"]') || []
          ).map(el => ({
            type: el.textContent?.includes('liked') ? 'like' : 'comment',
            content: el.closest('[data-test-id="feed-update"]')
              ?.querySelector('.feed-update__content')?.textContent?.trim()
              ?.substring(0, 100),
          })),

          // Articles/posts they've shared (shows expertise areas)
          articlesShared: Array.from(
            document.querySelectorAll('[data-test-id="feed-update__authored"]') || []
          ).map(el => ({
            title: el.querySelector('.feed-update__content-title')?.textContent?.trim(),
            topic: el.querySelector('.feed-update__hashtag')?.textContent?.trim(),
          })),

          // Groups they're in (shows community)
          groups: Array.from(
            document.querySelectorAll('[data-test-id="groups"] a') || []
          ).map(el => el.textContent?.trim()).filter(Boolean),

          // Skills/endorsements (shows expertise)
          skills: Array.from(
            document.querySelectorAll('[data-test-id="skills"] .skill-name') || []
          ).map(el => el.textContent?.trim()).filter(Boolean),

          // Headlines on articles/updates (shows messaging they care about)
          messageTopics: Array.from(
            document.querySelectorAll('.feed-update__headline') || []
          ).map(el => el.textContent?.trim())
            .filter(Boolean)
            .slice(0, 5),
        };
      });

      return signals;
    } catch (error) {
      console.error('[LinkedIn] Signal extraction error:', error.message);
      return null;
    }
  }

  /**
   * Extract basic LinkedIn people data from search results
   */
  async _extractLinkedInPeopleData(page) {
    try {
      const people = await page.evaluate(() => {
        return Array.from(
          document.querySelectorAll('[data-test-id="search-entity-result"]')
        ).map(el => ({
          name: el.querySelector('.entity-result__title-text a')?.textContent?.trim(),
          title: el.querySelector('.entity-result__subtitle')?.textContent?.trim(),
          company: el.querySelector('.entity-result__headline')?.textContent?.trim()?.split(' at ')?.[1],
          location: el.querySelector('[data-test-id="location"]')?.textContent?.trim(),
          profileUrl: el.querySelector('a.app-aware-link')?.href,
        }));
      });

      return people.filter(p => p.name && p.profileUrl);
    } catch (error) {
      console.error('[LinkedIn] People extraction error:', error.message);
      return [];
    }
  }

  /**
   * Internal: Get browser from pool and execute task
   */
  async _scrapeWithBrowser(url, extractFn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ url, extractFn, resolve, reject });
      this._processQueue();
    });
  }

  /**
   * Internal: Process queue with concurrency control
   */
  async _processQueue() {
    while (this.queue.length > 0 && this.activeJobs < this.maxConcurrent) {
      const { url, extractFn, resolve, reject } = this.queue.shift();
      this.activeJobs++;

      try {
        const browser = this.browsers[this.activeJobs % this.browsers.length];
        const page = await browser.newPage();

        // Anti-detection: randomize user agent
        await page.setUserAgent(
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        );

        // Set viewport
        await page.setViewport({ width: 1280, height: 720 });

        // Navigate with random delay
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

        // Extract data
        const data = await extractFn(page);

        await page.close();
        this.activeJobs--;

        resolve(data);
        this._processQueue();
      } catch (error) {
        console.error(`[Obscura] Error scraping ${url}:`, error.message);
        this.activeJobs--;
        reject(error);
        this._processQueue();
      }
    }
  }

  /**
   * Internal: Random delay for anti-detection
   */
  async _antiDetectDelay() {
    const delay = Math.random() * 3000 + 1000; // 1-4 seconds
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * Internal: Extract LinkedIn post data from page
   */
  async _extractLinkedInPostData(page) {
    try {
      const posts = await page.evaluate(() => {
        const elements = document.querySelectorAll('[data-id*="post"]');
        return Array.from(elements).map(el => ({
          author: el.querySelector('[data-test-id="feed-mini-update-card__actor"] a')?.textContent?.trim(),
          company: el.querySelector('.feed-mini-update-card__company')?.textContent?.trim(),
          content: el.querySelector('.feed-mini-update-card__content')?.textContent?.trim(),
          likes: el.querySelector('[data-test-id="social_counts_reaction"] span')?.textContent?.trim(),
          comments: el.querySelector('[data-test-id="social_counts_comment"] span')?.textContent?.trim(),
          shares: el.querySelector('[data-test-id="social_counts_share"] span')?.textContent?.trim(),
          timestamp: el.querySelector('time')?.getAttribute('datetime'),
        }));
      });

      return posts.filter(p => p.content && p.author);
    } catch (error) {
      console.error('[LinkedIn] Extraction error:', error.message);
      return [];
    }
  }

  /**
   * Internal: Extract Instagram video data from page
   */
  async _extractInstagramVideoData(page) {
    try {
      const videos = await page.evaluate(() => {
        const elements = document.querySelectorAll('article');
        return Array.from(elements).map(el => ({
          caption: el.querySelector('.caption')?.textContent?.trim(),
          likes: el.querySelector('[aria-label*="like"]')?.textContent?.trim(),
          comments: el.querySelector('[aria-label*="comment"]')?.textContent?.trim(),
          videoUrl: el.querySelector('video')?.src,
          posterUrl: el.querySelector('img[alt="Carousel"]')?.src,
          authorUsername: el.querySelector('.author')?.textContent?.trim(),
          timestamp: el.querySelector('time')?.getAttribute('datetime'),
        }));
      });

      return videos.filter(v => v.caption || v.videoUrl);
    } catch (error) {
      console.error('[Instagram] Extraction error:', error.message);
      return [];
    }
  }

  /**
   * Internal: Generate LinkedIn people search URLs by criteria
   * Searches for people matching job title, industry, company size, location
   */
  _generateLinkedInPeopleSearchUrls(criteria) {
    const {
      jobTitles = [],
      industries = [],
      companySizes = [],
      locations = [],
    } = criteria;

    const urls = [];

    // Generate search URLs for each job title + industry combination
    for (const title of jobTitles) {
      for (const industry of industries) {
        const query = encodeURIComponent(`${title} ${industry}`);
        urls.push(
          `https://www.linkedin.com/search/results/people/?keywords=${query}&geoUrn=%5B%22${locations[0] || 'gb'}\"%5D`
        );
      }
    }

    return urls.length > 0 ? urls : [
      'https://www.linkedin.com/search/results/people/'
    ];
  }

  /**
   * Cleanup: Close all browser instances
   */
  async close() {
    console.log('[Obscura] Closing browsers...');
    await Promise.all(this.browsers.map(b => b.close()));
  }
}

module.exports = ObscuraScraper;
