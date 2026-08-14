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
    const voices = [
      {
        default: true,
        lang: 'en-US',
        localService: true,
        name: 'Mock US Local',
        voiceURI: 'mock-us-local',
      },
      {
        default: false,
        lang: 'en-GB',
        localService: true,
        name: 'Mock UK Local',
        voiceURI: 'mock-uk-local',
      },
      {
        default: false,
        lang: 'en-GB',
        localService: false,
        name: 'Mock UK High Quality',
        voiceURI: 'mock-uk-remote',
      },
    ] as SpeechSynthesisVoice[];

    Object.defineProperty(window, 'speechSynthesis', {
      configurable: true,
      value: {
        cancel: () => undefined,
        speak: (utterance: SpeechSynthesisUtterance) => {
          window.localStorage.setItem(
            'lastSpoken',
            JSON.stringify({
              text: utterance.text,
              lang: utterance.lang,
              voice: utterance.voice?.name ?? null,
            }),
          );
        },
        pause: () => undefined,
        resume: () => undefined,
        getVoices: () => voices,
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
        voice: SpeechSynthesisVoice | null = null;

        constructor(text: string) {
          this.text = text;
        }
      },
    });
  });
}

async function mockCloudTtsFailure(page: Page) {
  await page.route('**/synthesizeSpeech**', async (route) => {
    await route.abort();
  });
}

test('發音設定可切換、測試發音、三種發音引擎並重新整理持久化', async ({
  page,
}) => {
  await mockSpeechSynthesis(page);
  await mockCloudTtsFailure(page);
  const pageErrors: string[] = [];
  page.on('pageerror', (err) => pageErrors.push(err.message));

  await page.goto('/');
  await page.getByLabel('發音設定').click();
  await expect(page).toHaveURL(/\/settings$/);
  await expect(page.getByRole('heading', { name: '發音設定' })).toBeVisible();
  await expect(page.getByRole('button', { name: /美式發音/ })).toHaveAttribute(
    'aria-pressed',
    'true',
  );

  await page.getByRole('button', { name: /英式發音/ }).click();
  await expect(page.getByRole('button', { name: /英式發音/ })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  await page.getByRole('button', { name: /測試發音/ }).click();
  await expect
    .poll(() =>
      page.evaluate(() => JSON.parse(localStorage.getItem('lastSpoken') ?? '{}')),
    )
    .toMatchObject({
      text: 'hello',
      lang: 'en-GB',
      voice: 'Mock UK Local',
    });

  await page
    .getByRole('button', { name: /優先高品質裝置語音/ })
    .click();
  await expect(
    page.getByRole('button', { name: /優先高品質裝置語音/ }),
  ).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: /測試發音/ }).click();
  await expect
    .poll(() =>
      page.evaluate(() => JSON.parse(localStorage.getItem('lastSpoken') ?? '{}')),
    )
    .toMatchObject({
      text: 'hello',
      lang: 'en-GB',
      voice: 'Mock UK High Quality',
    });

  await page.getByRole('button', { name: /Google 雲端語音/ }).click();
  await expect(
    page.getByRole('button', { name: /Google 雲端語音/ }),
  ).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('button', { name: /測試發音/ }).click();
  await expect
    .poll(() =>
      page.evaluate(() => JSON.parse(localStorage.getItem('lastSpoken') ?? '{}')),
    )
    .toMatchObject({
      text: 'hello',
      lang: 'en-GB',
      voice: 'Mock UK Local',
    });

  await page.reload();
  await expect(page.getByRole('button', { name: /英式發音/ })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  await expect(
    page.getByRole('button', { name: /Google 雲端語音/ }),
  ).toHaveAttribute('aria-pressed', 'true');
  expect(pageErrors).toEqual([]);
  await saveScreenshot(page, 'tts-settings-persisted');
});

test('套用設定後，故事模式既有發音按鈕仍可播放且不報錯', async ({ page }) => {
  await mockSpeechSynthesis(page);
  await mockCloudTtsFailure(page);
  const pageErrors: string[] = [];
  page.on('pageerror', (err) => pageErrors.push(err.message));

  await page.goto('/settings');
  await page.getByRole('button', { name: /英式發音/ }).click();
  await page.getByRole('button', { name: /Google 雲端語音/ }).click();

  await page.goto('/');
  await page.getByRole('button', { name: '學測', exact: true }).click();
  await page.goto('/builder');
  await page.getByRole('button', { name: '建立第 16 頁批次' }).click();
  await page.getByRole('button', { name: /故事模式/ }).click();
  await expect(page.getByText('Minecraft 故事')).toBeVisible();

  await page.getByRole('button', { name: /播放 Alex opened her diary/ }).click();
  await expect
    .poll(() =>
      page.evaluate(() => JSON.parse(localStorage.getItem('lastSpoken') ?? '{}')),
    )
    .toMatchObject({
      lang: 'en-GB',
      voice: 'Mock UK Local',
    });
  expect(pageErrors).toEqual([]);
  await saveScreenshot(page, 'tts-story-button-after-settings');
});

test('套用設定後，翻牌卡既有發音按鈕仍可播放且不報錯', async ({ page }) => {
  await mockSpeechSynthesis(page);
  await mockCloudTtsFailure(page);
  const pageErrors: string[] = [];
  page.on('pageerror', (err) => pageErrors.push(err.message));

  await page.goto('/settings');
  await page.getByRole('button', { name: /英式發音/ }).click();
  await page.getByRole('button', { name: /Google 雲端語音/ }).click();

  await page.goto('/');
  await page.getByRole('button', { name: '學測', exact: true }).click();
  await page.goto('/builder');
  await page.getByRole('button', { name: '建立第 16 頁批次' }).click();
  await page.getByRole('button', { name: /翻牌學習/ }).click();
  await expect(page.getByRole('heading', { name: '翻牌學習' })).toBeVisible();

  await page.getByRole('button', { name: /播放 .* 的英文發音/ }).first().click();
  await expect
    .poll(() =>
      page.evaluate(() => JSON.parse(localStorage.getItem('lastSpoken') ?? '{}')),
    )
    .toMatchObject({
      lang: 'en-GB',
      voice: 'Mock UK Local',
    });
  expect(pageErrors).toEqual([]);
  await saveScreenshot(page, 'tts-flashcard-button-after-settings');
});
