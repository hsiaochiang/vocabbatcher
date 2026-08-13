import { expect, test, type Page } from '@playwright/test';
import { mkdirSync } from 'node:fs';

const screenshotDir = 'e2e/screenshots';

function ensureScreenshotDir() {
  mkdirSync(screenshotDir, { recursive: true });
}

async function saveScreenshot(page: Page, name: string) {
  ensureScreenshotDir();
  await page.screenshot({
    path: `${screenshotDir}/${name}.png`,
    fullPage: true,
  });
}

async function mockSpeechSynthesis(page: Page) {
  await page.addInitScript(() => {
    Object.defineProperty(window, 'speechSynthesis', {
      configurable: true,
      value: {
        cancel: () => undefined,
        speak: () => undefined,
        pause: () => undefined,
        resume: () => undefined,
        getVoices: () => [],
        addEventListener: () => undefined,
        removeEventListener: () => undefined,
        dispatchEvent: () => true,
        paused: false,
        pending: false,
        speaking: false,
        onvoiceschanged: null,
      },
    });

    Object.defineProperty(window, 'SpeechSynthesisUtterance', {
      configurable: true,
      value: class {
        text: string;
        lang = '';
        rate = 1;

        constructor(text: string) {
          this.text = text;
        }
      },
    });
  });
}

test('學測第16頁頁碼批次會出現故事模式並可點發音', async ({ page }) => {
  await mockSpeechSynthesis(page);
  const pageErrors: string[] = [];
  page.on('pageerror', (err) => pageErrors.push(err.message));

  await page.goto('/');
  await page.getByRole('button', { name: '學測', exact: true }).click();
  await page.goto('/builder');
  await page.getByRole('button', { name: '建立第 16 頁批次' }).click();

  await expect(page.getByText('批次 #1（學測第 16 頁）')).toBeVisible();
  await expect(page.getByRole('button', { name: /故事模式/ })).toBeVisible();
  await saveScreenshot(page, 'gsat-story-page16-hub');

  await page.getByRole('button', { name: /故事模式/ }).click();
  await expect(page).toHaveURL(/\/batch\/\d+\/story$/);
  await expect(page.getByText('Minecraft 故事')).toBeVisible();
  await expect(page.getByText('學測第 16 頁')).toBeVisible();
  await expect(page.getByText(/Alex opened her diary/)).toBeVisible();

  await page.getByRole('button', { name: /播放 Alex opened her diary/ }).click();
  await page.getByRole('button', { name: '播放 cognitive 的英文發音' }).click();
  expect(pageErrors).toEqual([]);
  await saveScreenshot(page, 'gsat-story-page16-list');
});

test('手動選字建立的學測批次不顯示故事模式', async ({ page }) => {
  await mockSpeechSynthesis(page);

  await page.goto('/');
  await page.getByRole('button', { name: '學測', exact: true }).click();
  await page.goto('/builder');
  await page.getByPlaceholder('搜尋英文單字…').fill('accord');
  await page.getByText('accord').first().click();
  await page.getByRole('button', { name: /建立批次/ }).click();

  await expect(page.getByText('批次 #1（學測）')).toBeVisible();
  await expect(page.getByRole('button', { name: /故事模式/ })).toHaveCount(0);
  await saveScreenshot(page, 'gsat-story-manual-batch-no-card');
});
