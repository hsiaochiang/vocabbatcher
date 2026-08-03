import { expect, test } from '@playwright/test';

async function createFirstPageBatch(page: import('@playwright/test').Page) {
  await page.goto('/builder');
  await page.getByRole('button', { name: '建立第 1 頁批次' }).click();
  await expect(page.getByText('批次 #1（會考第 1 頁）')).toBeVisible();
}

async function answerCurrentQuestion(page: import('@playwright/test').Page) {
  const spellingInput = page.getByPlaceholder('輸入英文單字');
  if (await spellingInput.isVisible()) {
    await spellingInput.fill('wrong');
    await page.getByRole('button', { name: '送出答案' }).click();
    return;
  }

  const answerButtons = page.locator('main .space-y-2 button');
  await answerButtons.first().click();
}

test('批次 Hub 入口接回考試與統計，並帶入批次頁碼範圍', async ({ page }) => {
  await createFirstPageBatch(page);

  await expect(page.getByRole('button', { name: /翻牌學習/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /練習測驗/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /學習統計/ })).toBeVisible();
  await expect(page.getByText('即將推出')).toHaveCount(0);
  await expect(page.getByText('錄音播放')).toHaveCount(0);

  await page.getByRole('button', { name: /練習測驗/ }).click();
  await expect(page).toHaveURL(/\/exam$/);
  await expect(page.locator('input[type="number"]').nth(0)).toHaveValue('1');
  await expect(page.locator('input[type="number"]').nth(1)).toHaveValue('1');

  await page.goBack();
  await page.getByRole('button', { name: /學習統計/ }).click();
  await expect(page).toHaveURL(/\/stats$/);
  await expect(page.getByText(/請先登入|載入中|還沒有單字統計/)).toBeVisible();
});

test('重複批次會提示，取消後不建立新批次', async ({ page }) => {
  await createFirstPageBatch(page);
  await page.goto('/builder');

  page.once('dialog', async (dialog) => {
    expect(dialog.message()).toContain('內容相同的批次');
    await dialog.dismiss();
  });
  await page.getByRole('button', { name: '建立第 1 頁批次' }).click();

  await expect(page).toHaveURL(/\/builder$/);
  const batchCount = await page.evaluate(() => {
    const raw = window.localStorage.getItem('batches');
    return raw ? JSON.parse(raw).length : 0;
  });
  expect(batchCount).toBe(1);
});

test('批次建立器保留空搜尋狀態、0 字建立保護與大型清單順暢捲動', async ({
  page,
}) => {
  await page.goto('/builder');
  await expect(page.getByText('顯示 1231 筆')).toBeVisible();
  await expect(page.getByRole('button', { name: /^建立批次/ })).toBeDisabled();

  await page.getByPlaceholder('搜尋英文單字…').fill('zzzz-not-found');
  await expect(page.getByText('沒有符合條件的單字')).toBeVisible();

  await page.getByPlaceholder('搜尋英文單字…').fill('');
  await expect(page.getByText('顯示 1231 筆')).toBeVisible();
  const duration = await page.evaluate(async () => {
    const start = performance.now();
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;

    for (let i = 0; i <= 20; i += 1) {
      window.scrollTo(0, (maxScroll * i) / 20);
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    }

    return Math.round(performance.now() - start);
  });
  console.log(`M4S2-S4 full list scroll probe: ${duration}ms`);
  expect(duration).toBeLessThan(1_500);
});

test('主要頁面 smoke test 無白屏，考試流程可走到結果頁', async ({ page }) => {
  await createFirstPageBatch(page);

  await page.getByRole('button', { name: /翻牌學習/ }).click();
  await expect(page.getByText('翻牌學習')).toBeVisible();
  await page.getByLabel('返回').click();

  await page.getByRole('button', { name: /練習測驗/ }).click();
  await page.getByRole('button', { name: '5 題' }).click();
  await page.getByRole('button', { name: '開始考試' }).click();
  await expect(page.getByText(/第 1 \/ \d+ 題/)).toBeVisible();

  for (let i = 0; i < 5; i += 1) {
    await answerCurrentQuestion(page);
    await page.getByRole('button', { name: i === 4 ? '看結果' : '下一題' }).click();
  }

  await expect(page).toHaveURL(/\/exam\/result$/);
  await expect(page.getByText('考試結果')).toBeVisible();
  await page.getByLabel('返回').click();
  await expect(page).toHaveURL(/\/$/);

  await page.goto('/stats');
  await expect(page.getByText(/請先登入|載入中|還沒有單字統計/)).toBeVisible();
  await page.goto('/history');
  await expect(page.getByText(/請先登入|載入中|還沒有保存的考試成績/)).toBeVisible();
});
