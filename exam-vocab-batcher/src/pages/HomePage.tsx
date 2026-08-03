import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';
import UserBadge from '../components/UserBadge';
import { VOCAB_SOURCE_LABEL, type VocabSource } from '../types/vocab';

export default function HomePage() {
  const {
    source,
    setSource,
    batches,
    activeBatchId,
    isLoading,
    loadError,
    setActiveBatch,
  } = useApp();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">載入中…</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-light">
        <Header title="英文單字準備" rightSlot={<UserBadge />} />
        <main className="flex flex-1 items-center justify-center px-6 text-center">
          <div className="max-w-sm">
            <span className="material-symbols-outlined mb-4 text-5xl text-red-400">
              cloud_off
            </span>
            <h2 className="text-xl font-bold text-gray-900">
              單字庫載入失敗
            </h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              請檢查網路連線後重新載入。單字庫沒有載入完成時，無法建立批次或開始考試。
            </p>
            <button
              onClick={() => window.location.reload()}
              className="mt-5 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-primary/90"
            >
              重新載入
            </button>
          </div>
        </main>
      </div>
    );
  }

  const sourceBatches = batches.filter((batch) => batch.source === source);
  const activeBatch = sourceBatches.find((b) => b.id === activeBatchId);
  const hasBatches = sourceBatches.length > 0;
  const sortedBatches = [...sourceBatches].sort(
    (a, b) =>
      new Date(b.lastAccessedAt).getTime() -
      new Date(a.lastAccessedAt).getTime(),
  );

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header title="英文單字準備" rightSlot={<UserBadge />} />

      <main className="flex-1 px-4 pb-24 pt-4">
        <section className="mb-4 rounded-xl border border-gray-200 bg-white p-2 shadow-sm">
          <div className="grid grid-cols-2 gap-2">
            {(['cap', 'gsat'] as VocabSource[]).map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setSource(option)}
                className={`rounded-lg px-4 py-3 text-sm font-semibold transition-colors ${
                  source === option
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
                aria-pressed={source === option}
              >
                {VOCAB_SOURCE_LABEL[option]}
              </button>
            ))}
          </div>
        </section>

        {/* Primary action */}
        <section className="mb-6">
          <button
            onClick={() => navigate(hasBatches ? '/exam' : '/builder')}
            className="flex w-full items-center justify-between rounded-xl bg-primary px-4 py-4 text-left text-white shadow-sm transition-colors hover:bg-primary/90"
          >
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-2xl">
                {hasBatches ? 'quiz' : 'add'}
              </span>
              <div>
                <p className="font-semibold">
                  {hasBatches ? '開始考試' : '建立新批次'}
                </p>
                <p className="mt-0.5 text-xs text-white/80">
                  {hasBatches
                    ? `用${VOCAB_SOURCE_LABEL[source]}單字庫頁數範圍出題`
                    : `先選最多 25 個${VOCAB_SOURCE_LABEL[source]}單字`}
                </p>
              </div>
            </div>
            <span className="material-symbols-outlined text-white/80">
              chevron_right
            </span>
          </button>

          <div className="mt-3 flex divide-x divide-gray-200 rounded-xl border border-gray-200 bg-white shadow-sm">
            <button
              onClick={() => navigate('/history')}
              className="flex flex-1 items-center justify-center gap-2 px-3 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              <span className="material-symbols-outlined text-[20px] text-gray-500">
                history
              </span>
              成績歷史
            </button>

            <button
              onClick={() => navigate('/stats')}
              className="flex flex-1 items-center justify-center gap-2 px-3 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              <span className="material-symbols-outlined text-[20px] text-gray-500">
                bar_chart
              </span>
              單字統計
            </button>
          </div>
        </section>

        {/* Continue last batch */}
        {activeBatch && (
          <section className="mb-6">
            <h2 className="mb-3 text-sm font-medium text-gray-500">
              繼續上次
            </h2>
            <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-900">
                    {activeBatch.name}
                  </p>
                  <p className="mt-1 text-sm text-gray-500">
                    已學 {activeBatch.flashcardIndex} / {activeBatch.words.length} 張
                  </p>
                </div>
              </div>
              {/* Progress bar */}
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-gray-100">
                <div
                  className="h-full rounded-full bg-primary transition-all"
                  style={{
                    width: `${activeBatch.words.length > 0 ? (activeBatch.flashcardIndex / activeBatch.words.length) * 100 : 0}%`,
                  }}
                />
              </div>
              <button
                onClick={() => navigate(`/batch/${activeBatch.id}`)}
                className="mt-3 w-full rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
              >
                繼續
              </button>
            </div>
          </section>
        )}

        {/* Batch history */}
        <section>
          <h2 className="mb-3 text-sm font-medium text-gray-500">
            歷史批次
          </h2>

          {sortedBatches.length === 0 ? (
            <div className="flex flex-col items-center py-16 text-center">
              <span className="material-symbols-outlined mb-3 text-5xl text-gray-300">
                library_books
              </span>
              <p className="text-gray-600">還沒有批次，點上方按鈕開始</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sortedBatches.map((batch) => (
                <button
                  key={batch.id}
                  onClick={() => {
                    setActiveBatch(batch.id);
                    navigate(`/batch/${batch.id}`);
                  }}
                  className="flex w-full items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3 text-left shadow-sm transition-colors hover:bg-gray-50"
                >
                  <div>
                    <p className="font-medium text-gray-900">{batch.name}</p>
                  <p className="mt-0.5 text-xs text-gray-500">
                      {new Date(batch.createdAt).toLocaleDateString('zh-TW')} ·{' '}
                      {VOCAB_SOURCE_LABEL[batch.source]} · {batch.words.length} 字
                    </p>
                  </div>
                  <span className="material-symbols-outlined text-gray-300">
                    chevron_right
                  </span>
                </button>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Fixed bottom button */}
      {hasBatches && (
        <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
          <button
            onClick={() => navigate('/builder')}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-3 font-semibold text-gray-700 shadow-sm hover:bg-gray-50"
          >
            <span className="material-symbols-outlined text-[20px]">add</span>
            建立新批次
          </button>
        </div>
      )}
    </div>
  );
}
