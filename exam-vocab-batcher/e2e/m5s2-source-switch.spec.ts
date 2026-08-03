import { expect, test } from '@playwright/test';

const GSAT_PAGE_1_WORDS = new Set([
  'accord',
  'invent',
  'paragraph',
  'passage',
  'process',
  'product',
  'reduce',
  'refer',
  'research',
  'researcher',
  'risk',
  'suffer',
]);

test('切換到學測後，批次、翻牌與考試都使用學測單字庫', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: '學測', exact: true }).click();
  await expect(
    page.getByRole('button', { name: '學測', exact: true }),
  ).toHaveAttribute('aria-pressed', 'true');

  await page.goto('/builder');
  await expect(page.getByText('學測批次建立器')).toBeVisible();
  await expect(page.getByText('顯示 1640 筆')).toBeVisible();

  await page.getByPlaceholder('搜尋英文單字…').fill('splendor');
  await expect(page.getByText('splendor').first()).toBeVisible();
  await page.getByPlaceholder('搜尋英文單字…').fill('');

  await page.getByRole('button', { name: '建立第 1 頁批次' }).click();
  await expect(page.getByText('批次 #1（學測第 1 頁）')).toBeVisible();
  await expect(page.getByText('12 個單字')).toBeVisible();

  await page.getByRole('button', { name: /翻牌學習/ }).click();
  await expect(page.getByText('accord').first()).toBeVisible();
  await page.getByLabel('返回').click();

  await page.getByRole('button', { name: /練習測驗/ }).click();
  await expect(page.locator('input[type="number"]').nth(0)).toHaveValue('1');
  await expect(page.locator('input[type="number"]').nth(1)).toHaveValue('1');
  await page.getByRole('button', { name: '5 題' }).click();
  await page.getByRole('button', { name: '開始考試' }).click();
  await expect(page).toHaveURL(/\/exam\/run$/);

  const questionWords = await page.evaluate(() => {
    const state = window.history.state as {
      usr?: { questions?: { word?: { word?: string } }[]; source?: string };
    };
    return {
      source: state.usr?.source,
      words: state.usr?.questions?.map((question) => question.word?.word) ?? [],
    };
  });
  expect(questionWords.source).toBe('gsat');
  expect(questionWords.words.length).toBeGreaterThan(0);
  expect(
    questionWords.words.every((word) => word && GSAT_PAGE_1_WORDS.has(word)),
  ).toBe(true);

  await page.goto('/');
  await page.getByRole('button', { name: '會考', exact: true }).click();
  await expect(page.getByText('批次 #1（學測第 1 頁）')).toHaveCount(0);

  await page.goto('/builder');
  await page.getByPlaceholder('搜尋英文單字…').fill('splendor');
  await expect(page.getByText('沒有符合條件的單字')).toBeVisible();
  await page.getByPlaceholder('搜尋英文單字…').fill('about');
  await expect(page.getByText('about').first()).toBeVisible();
});
