import { expect, test, type Page } from '@playwright/test';
import { mkdirSync } from 'node:fs';

const screenshotDir = 'e2e/screenshots';

function ensureScreenshotDir() {
  mkdirSync(screenshotDir, { recursive: true });
}

async function saveScreenshot(page: Page, name: string, fullPage = true) {
  ensureScreenshotDir();
  await page.screenshot({
    path: `${screenshotDir}/${name}.png`,
    fullPage,
  });
}

async function displayedCount(page: Page) {
  const text = await page.getByText(/顯示 \d+ 筆/).textContent();
  const match = text?.match(/\d+/);
  return match ? Number(match[0]) : 0;
}

test('首頁依批次狀態顯示主要 CTA', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('button', { name: /建立新批次/ })).toBeVisible();
  await saveScreenshot(page, 'home-empty-primary-cta');

  await page.evaluate(() => {
    const word = {
      word: 'about',
      pos: 'prep.',
      zh_definition: '關於',
      frequency: 10,
      source_page: [1],
      ipa_us: null,
      ipa_uk: null,
      parse_confidence: 1,
      issues: [],
    };
    window.localStorage.setItem(
      'batches',
      JSON.stringify([
        {
          id: 'pw-batch',
          name: 'Playwright 批次',
          source: 'cap',
          createdAt: new Date().toISOString(),
          lastAccessedAt: new Date().toISOString(),
          words: [word],
          flashcardIndex: 0,
        },
      ]),
    );
    window.localStorage.setItem('activeBatchId', JSON.stringify('pw-batch'));
  });

  await page.reload();
  await expect(page.getByRole('button', { name: /開始考試/ })).toBeVisible();
  await saveScreenshot(page, 'home-existing-batch-primary-cta');
});

test('批次建立器顯示可直接建立的課本頁碼按鈕', async ({ page }) => {
  await page.goto('/builder');
  await expect(page.getByText('快速建立：選課本頁碼')).toBeVisible();
  await expect(page.getByText('60 頁')).toBeVisible();
  await expect(
    page.getByRole('button', { name: '建立第 1 頁批次' }),
  ).toBeVisible();
  await expect(
    page.getByRole('button', { name: '建立第 60 頁批次' }),
  ).toBeVisible();
  await expect(page.getByText('19 字').first()).toBeVisible();
  await saveScreenshot(page, 'builder-page-buttons');
});

test('批次建立器在手機尺寸仍可操作頁碼按鈕', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/builder');
  await expect(page.getByText('快速建立：選課本頁碼')).toBeVisible();
  await expect(
    page.getByRole('button', { name: '建立第 1 頁批次' }),
  ).toBeVisible();
  await expect(page.getByRole('button', { name: /建立批次/ })).toBeVisible();
  await saveScreenshot(page, 'builder-page-buttons-mobile', false);
});

test('點選單一頁碼會建立該頁批次並進入批次頁', async ({ page }) => {
  await page.goto('/builder');
  await page.getByRole('button', { name: '建立第 1 頁批次' }).click();

  await expect(page.getByText('批次 #1（會考第 1 頁）')).toBeVisible();
  await expect(page.getByText('19 個單字')).toBeVisible();
  await expect(page.getByText('整體進度')).toBeVisible();
  await saveScreenshot(page, 'builder-one-page-created');
});

test('進階篩選仍可搜尋並手動建立批次', async ({ page }) => {
  await page.goto('/builder');
  await expect(page.getByText('進階篩選：手動選字')).toBeVisible();

  const initialCount = await displayedCount(page);
  await page.getByPlaceholder('搜尋英文單字…').fill('about');
  await expect
    .poll(() => displayedCount(page), { message: '搜尋後筆數應減少' })
    .toBeLessThan(initialCount);
  await expect(page.getByText('about').first()).toBeVisible();
  await page.getByText('about').first().click();
  await page.getByRole('button', { name: /建立批次/ }).click();

  await expect(page.getByText('批次 #1')).toBeVisible();
  await expect(page.getByText('1 個單字')).toBeVisible();
  await saveScreenshot(page, 'builder-advanced-filter');
});

test('考試設定顯示修正後的課本頁碼範圍', async ({ page }) => {
  await page.goto('/exam');
  await expect(page.getByText('頁數範圍')).toBeVisible();
  await expect(page.getByText('頁（全書 1~60 頁）')).toBeVisible();
  await expect(page.getByRole('button', { name: '開始考試' })).toBeVisible();
  await saveScreenshot(page, 'exam-setup-corrected-page-range');
});
