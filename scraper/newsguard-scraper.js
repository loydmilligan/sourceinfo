const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

/**
 * Extract domain from a full URL
 * @param {string} url - Full URL like https://www.nytimes.com
 * @returns {string} - Domain like nytimes.com
 */
function extractDomain(url) {
  try {
    const urlObj = new URL(url);
    let hostname = urlObj.hostname;

    // Remove www. prefix if present
    hostname = hostname.replace(/^www\./, '');

    return hostname;
  } catch (error) {
    console.error(`Error parsing URL: ${url}`, error.message);
    return null;
  }
}

/**
 * Read domains from CSV file
 * @param {string} csvPath - Path to CSV file
 * @returns {string[]} - Array of domains
 */
function readDomainsFromCSV(csvPath) {
  const content = fs.readFileSync(csvPath, 'utf-8');

  // Split by comma and/or newline, trim whitespace
  const urls = content
    .split(/[,\n]+/)
    .map(url => url.trim())
    .filter(url => url.length > 0);

  // Extract domains from URLs
  const domains = urls
    .map(extractDomain)
    .filter(domain => domain !== null);

  return [...new Set(domains)]; // Remove duplicates
}

/**
 * Main scraping function
 */
async function scrapeNewsGuard() {
  const csvPath = process.argv[2] || './news-sources.csv';
  const outputDir = process.argv[3] || './pdfs';

  if (!fs.existsSync(csvPath)) {
    console.error(`CSV file not found: ${csvPath}`);
    console.log('Usage: node newsguard-scraper.js <csv-file> [output-directory]');
    process.exit(1);
  }

  // Create output directory if it doesn't exist
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const domains = readDomainsFromCSV(csvPath);
  console.log(`Found ${domains.length} unique domains to scrape`);
  console.log('Domains:', domains.slice(0, 5).join(', '), '...\n');

  // Launch browser in non-headless mode so user can login
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100 // Slow down a bit for visibility
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('Opening NewsGuard...');
  console.log('Please login to NewsGuard in the browser window that just opened.');

  // Navigate to NewsGuard with the first domain
  const firstUrl = `https://api.newsguardtech.com/label/${domains[0]}`;
  await page.goto(firstUrl);

  // Wait for user to login
  console.log('\nPress Enter in this terminal when you have successfully logged in...');
  await new Promise(resolve => {
    process.stdin.once('data', resolve);
  });

  console.log('\nStarting to scrape domains...\n');

  const results = {
    success: [],
    failed: []
  };

  // Iterate through all domains
  for (let i = 0; i < domains.length; i++) {
    const domain = domains[i];
    const url = `https://api.newsguardtech.com/label/${domain}`;
    const pdfPath = path.join(outputDir, `${domain}.pdf`);

    try {
      console.log(`[${i + 1}/${domains.length}] Processing: ${domain}`);

      await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

      // Wait a bit for any dynamic content to load
      await page.waitForTimeout(2000);

      // Save as PDF
      await page.pdf({
        path: pdfPath,
        format: 'A4',
        printBackground: true,
        margin: {
          top: '20px',
          right: '20px',
          bottom: '20px',
          left: '20px'
        }
      });

      console.log(`  ✓ Saved: ${pdfPath}`);
      results.success.push(domain);

    } catch (error) {
      console.error(`  ✗ Failed: ${domain} - ${error.message}`);
      results.failed.push({ domain, error: error.message });
    }

    // Small delay between requests to be respectful
    await page.waitForTimeout(1000);
  }

  await browser.close();

  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log('SCRAPING COMPLETE');
  console.log('='.repeat(50));
  console.log(`✓ Successfully scraped: ${results.success.length}`);
  console.log(`✗ Failed: ${results.failed.length}`);

  if (results.failed.length > 0) {
    console.log('\nFailed domains:');
    results.failed.forEach(({ domain, error }) => {
      console.log(`  - ${domain}: ${error}`);
    });
  }

  // Save results to JSON
  const resultsPath = path.join(outputDir, 'scrape-results.json');
  fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));
  console.log(`\nResults saved to: ${resultsPath}`);
}

// Run the scraper
scrapeNewsGuard().catch(console.error);
