import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';
import UserBadge from '../components/UserBadge';

export default function HomePage() {
  const { batches, activeBatchId, isLoading, setActiveBatch } = useApp();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">載入中…</p>
      </div>
    );
  }

  const activeBatch = batches.find((b) => b.id === activeBatchId);
  const sortedBatches = [...batches].sort(
    (a, b) =>
      new Date(b.lastAccessedAt).getTime() -
      new Date(a.lastAccessedAt).getTime(),
  );

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header title="國中會考單字準備" rightSlot={<UserBadge />} />

      <main className="flex-1 px-4 pb-24 pt-4">
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
              <p className="text-gray-400">還沒有批次，點下方按鈕開始</p>
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
                    <p className="mt-0.5 text-xs text-gray-400">
                      {new Date(batch.createdAt).toLocaleDateString('zh-TW')} ·{' '}
                      {batch.words.length} 字
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
      <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
        <button
          onClick={() => navigate('/builder')}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 font-semibold text-white shadow-sm hover:bg-primary/90"
        >
          <span className="material-symbols-outlined text-[20px]">add</span>
          建立新批次
        </button>
      </div>
    </div>
  );
}
