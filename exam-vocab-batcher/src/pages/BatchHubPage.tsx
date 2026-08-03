import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';
import UserBadge from '../components/UserBadge';
import { getPageRange } from '../services/exam';
import { VOCAB_SOURCE_LABEL } from '../types/vocab';

export default function BatchHubPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { source, setSource, batches, updateBatch, deleteBatch } = useApp();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const batch = batches.find((b) => b.id === id);

  // Update lastAccessedAt on mount
  useEffect(() => {
    if (id) {
      updateBatch(id, { lastAccessedAt: new Date().toISOString() });
    }
  }, [id, updateBatch]);

  useEffect(() => {
    if (batch && batch.source !== source) {
      setSource(batch.source);
    }
  }, [batch, setSource, source]);

  if (!batch) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-light">
        <Header
          title="批次"
          onBack={() => navigate('/')}
          rightSlot={<UserBadge />}
        />
        <div className="flex flex-1 items-center justify-center">
          <p className="text-gray-600">找不到此批次</p>
        </div>
      </div>
    );
  }

  if (batch.source !== source) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-light">
        <Header
          title="批次"
          onBack={() => navigate('/')}
          rightSlot={<UserBadge />}
        />
        <div className="flex flex-1 items-center justify-center">
          <p className="text-gray-600">
            切換到{VOCAB_SOURCE_LABEL[batch.source]}單字庫中…
          </p>
        </div>
      </div>
    );
  }

  const progress =
    batch.words.length > 0
      ? Math.round((batch.flashcardIndex / batch.words.length) * 100)
      : 0;
  const [batchMinPage, batchMaxPage] = getPageRange(batch.words);

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
      icon: 'edit_note',
      label: '練習測驗',
      subtitle: `第 ${batchMinPage}-${batchMaxPage} 頁`,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-200',
      available: true,
      onClick: () =>
        navigate('/exam', {
          state: {
            initialMinPage: batchMinPage,
            initialMaxPage: batchMaxPage,
          },
        }),
    },
    {
      icon: 'bar_chart',
      label: '學習統計',
      subtitle: '查看錯誤率',
      color: 'text-violet-500',
      bgColor: 'bg-violet-50',
      borderColor: 'border-violet-200',
      available: true,
      onClick: () => navigate('/stats'),
    },
  ];

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title={batch.name}
        onBack={() => navigate('/')}
        rightSlot={
          <div className="flex items-center gap-2">
            <UserBadge />
            <button
              onClick={() => setDeleteOpen(true)}
              className="flex min-h-[44px] min-w-[44px] items-center justify-center rounded-full text-gray-500 hover:bg-red-50 hover:text-red-500"
              aria-label="刪除批次"
            >
              <span className="material-symbols-outlined">delete</span>
            </button>
          </div>
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
          <p className="mt-2 text-xs text-gray-500">
            已完成 {batch.flashcardIndex} / {batch.words.length} 張翻牌
          </p>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-2 gap-3">
          {features.map((feat) => (
            <button
              key={feat.label}
              onClick={feat.onClick}
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
              <span className={`text-xs ${feat.available ? feat.color : 'text-gray-500'}`}>
                {feat.subtitle}
              </span>
            </button>
          ))}
        </div>
      </main>

      {deleteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-sm rounded-xl bg-white p-5 shadow-xl">
            <h2 className="text-lg font-bold text-gray-900">刪除批次</h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              確定要刪除「{batch.name}」嗎？裡面的翻牌進度也會一併刪除，無法復原。
            </p>
            <div className="mt-5 flex gap-3">
              <button
                onClick={() => setDeleteOpen(false)}
                className="flex-1 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                取消
              </button>
              <button
                onClick={() => {
                  deleteBatch(batch.id);
                  navigate('/');
                }}
                className="flex-1 rounded-lg bg-red-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-600"
              >
                確定刪除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
