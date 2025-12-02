# NewsGuard Scraper

A Playwright-based script to download NewsGuard reports as PDFs for personal use.

## Prerequisites

- Node.js (v16 or higher)
- A NewsGuard subscription with login credentials

## Setup

1. Navigate to the scraper directory:
   ```bash
   cd scraper
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Install Playwright browsers:
   ```bash
   npx playwright install chromium
   ```

## Usage

### Basic Usage

Run the scraper with the default CSV file:

```bash
npm run scrape
```

Or run directly:

```bash
node newsguard-scraper.js news-sources.csv pdfs
```

### Custom CSV File

You can provide your own CSV file with news source URLs:

```bash
node newsguard-scraper.js my-sources.csv output-folder
```

### CSV Format

The CSV file should contain URLs separated by commas and/or newlines. The script will automatically extract domains from full URLs.

Example:
```
https://www.nytimes.com,https://www.washingtonpost.com
https://www.bbc.com/news
https://www.cnn.com,https://www.foxnews.com
```

## How It Works

1. **Launch Browser**: The script opens a Chromium browser window (non-headless)
2. **Manual Login**: You manually log in to NewsGuard in the browser window
3. **Confirmation**: Press Enter in the terminal after logging in
4. **Automated Scraping**: The script visits each NewsGuard report URL and saves it as a PDF
5. **Results**: PDFs are saved in the output directory, organized by domain name

## Output

- **PDFs**: Saved in `pdfs/` directory (or custom output directory)
  - Format: `{domain}.pdf` (e.g., `nytimes.com.pdf`)
- **Results Log**: `scrape-results.json` contains success/failure information

## Notes

- The script runs at a respectful pace with 1-second delays between requests
- Failed scrapes are logged in the results file
- PDFs include full page content with background graphics
- Each PDF is named after the domain for easy identification

## Troubleshooting

**Browser doesn't open:**
- Ensure Playwright browsers are installed: `npx playwright install chromium`

**Login timeout:**
- Take your time logging in; the script waits for you to press Enter

**PDF generation fails:**
- Check that you're still logged in to NewsGuard
- Verify the domain exists in NewsGuard's database

**Missing domains:**
- Some URLs may redirect or have different primary domains
- Check the console output to see which domains are being processed
