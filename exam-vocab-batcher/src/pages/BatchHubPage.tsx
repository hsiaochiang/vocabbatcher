import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';

export default function BatchHubPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { batches, updateBatch, deleteBatch } = useApp();

  const batch = batches.find((b) => b.id === id);

  // Update lastAccessedAt on mount
  useEffect(() => {
    if (id) {
      updateBatch(id, { lastAccessedAt: new Date().toISOString() });
    }
  }, [id, updateBatch]);

  if (!batch) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-light">
        <Header title="批次" onBack={() => navigate('/')} />
        <div className="flex flex-1 items-center justify-center">
          <p className="text-gray-400">找不到此批次</p>
        </div>
      </div>
    );
  }

  const progress =
    batch.words.length > 0
      ? Math.round((batch.flashcardIndex / batch.words.length) * 100)
      : 0;

  const features = [
    {
      icon: 'style',
      label: '翻牌學習',
      subtitle: `${batch.words.length} 個單字`,
      color: 'text-primary',
      bgColor: 'bg-primary/5',
      borderColor: 'border-primary/30',
      available: true,
      onClick: () => navigate(`/batch/${id}/flashcard`),
    },
    {
      icon: 'volume_up',
      label: '錄音播放',
      subtitle: '即將推出',
      color: 'text-amber-500',
      bgColor: 'bg-amber-50',
      borderColor: 'border-gray-200',
      available: false,
    },
    {
      icon: 'edit_note',
      label: '練習測驗',
      subtitle: '即將推出',
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-gray-200',
      available: false,
    },
    {
      icon: 'bar_chart',
      label: '學習統計',
      subtitle: '即將推出',
      color: 'text-violet-500',
      bgColor: 'bg-violet-50',
      borderColor: 'border-gray-200',
      available: false,
    },
  ];

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title={batch.name}
        onBack={() => navigate('/')}
        rightSlot={
          <button
            onClick={() => {
              if (confirm('確定刪除此批次？')) {
                deleteBatch(batch.id);
                navigate('/');
              }
            }}
            className="text-gray-400 hover:text-red-500"
            aria-label="刪除批次"
          >
            <span className="material-symbols-outlined">delete</span>
          </button>
        }
      />

      <main className="flex-1 px-4 pt-4">
        {/* Progress card */}
        <div className="mb-6 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-500">整體進度</p>
            <p className="text-2xl font-bold text-primary">{progress}%</p>
          </div>
          <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-2 text-xs text-gray-400">
            已完成 {batch.flashcardIndex} / {batch.words.length} 張翻牌
          </p>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-2 gap-3">
          {features.map((feat) => (
            <button
              key={feat.label}
              onClick={feat.available ? feat.onClick : undefined}
              className={`flex flex-col items-center justify-center gap-2 rounded-xl border ${feat.borderColor} ${feat.available ? feat.bgColor : 'bg-white'} p-6 shadow-sm transition-colors ${
                feat.available
                  ? 'hover:shadow-md'
                  : 'cursor-default opacity-60'
              }`}
            >
              <span className={`material-symbols-outlined text-3xl ${feat.color}`}>
                {feat.icon}
              </span>
              <span className="text-sm font-medium text-gray-700">
                {feat.label}
              </span>
              <span className={`text-xs ${feat.available ? feat.color : 'text-gray-400'}`}>
                {feat.subtitle}
              </span>
            </button>
          ))}
        </div>
      </main>
    </div>
  );
}
