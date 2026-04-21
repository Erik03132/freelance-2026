const { chromium } = require('playwright');

(async () => {
  try {
    console.log('Launching browser...');
    const browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    console.log('Browser launched successfully!');
    const page = await browser.newPage();
    await page.goto('https://example.com');
    console.log('Title:', await page.title());
    await browser.close();
    console.log('Browser closed.');
  } catch (err) {
    console.error('Failed to launch browser:', err);
  }
})();
