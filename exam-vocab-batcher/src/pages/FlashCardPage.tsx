import { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';
import { speakEn, speakZh } from '../services/tts';

export default function FlashCardPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { batches, updateBatch } = useApp();

  const batch = batches.find((b) => b.id === id);
  const [index, setIndex] = useState(batch?.flashcardIndex ?? 0);
  const [flipped, setFlipped] = useState(false);

  // Sync index from batch on mount
  useEffect(() => {
    if (batch) setIndex(batch.flashcardIndex);
  }, [batch?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const persistIndex = useCallback(
    (newIndex: number) => {
      if (id) updateBatch(id, { flashcardIndex: newIndex });
    },
    [id, updateBatch],
  );

  if (!batch || batch.words.length === 0) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-light">
        <Header title="翻牌學習" onBack={() => navigate(`/batch/${id}`)} />
        <div className="flex flex-1 items-center justify-center">
          <p className="text-gray-400">此批次沒有單字</p>
        </div>
      </div>
    );
  }

  const total = batch.words.length;
  const isComplete = index >= total;
  const word = isComplete ? null : batch.words[index];
  const progressPct = Math.round((index / total) * 100);

  const goNext = () => {
    setFlipped(false);
    if (isComplete) {
      // Restart
      setIndex(0);
      persistIndex(0);
    } else {
      const newIdx = index + 1;
      setIndex(newIdx);
      persistIndex(newIdx);
    }
  };

  const goPrev = () => {
    if (index > 0) {
      setFlipped(false);
      setIndex(index - 1);
    }
  };

  const handleFlip = () => {
    if (isComplete) return;
    const willFlip = !flipped;
    setFlipped(willFlip);
    // Auto-speak Chinese when flipping to back
    if (willFlip && word?.zh_definition) {
      speakZh(word.zh_definition);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header title="翻牌學習" onBack={() => navigate(`/batch/${id}`)} />

      {/* Progress bar */}
      <div className="border-b border-gray-100 bg-white px-4 py-3">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            已看 {Math.min(index, total)} / {total} 張
          </span>
          <span>{progressPct}%</span>
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-gray-100">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Card area */}
      <main className="flex flex-1 items-center justify-center px-6 py-8">
        {isComplete ? (
          <div className="flex flex-col items-center text-center">
            <span className="material-symbols-outlined mb-4 text-6xl text-primary">
              celebration
            </span>
            <h2 className="text-2xl font-bold text-gray-900">這輪結束！</h2>
            <p className="mt-2 text-gray-500">
              你已經看完全部 {total} 張翻牌
            </p>
          </div>
        ) : (
          <div
            className="w-full max-w-sm cursor-pointer"
            style={{ perspective: '1000px' }}
            onClick={handleFlip}
          >
            <div
              className={`card-inner relative h-80 w-full ${flipped ? 'flipped' : ''}`}
            >
              {/* Front */}
              <div className="card-front flex flex-col items-center justify-center rounded-2xl border border-gray-200 bg-white p-6 shadow-md">
                <p className="text-3xl font-bold text-gray-900">
                  {word!.word}
                </p>
                {word!.ipa_us && (
                  <p className="mt-2 text-base text-gray-400">
                    {word!.ipa_us}
                  </p>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    speakEn(word!.word);
                  }}
                  className="mt-4 flex min-h-[44px] min-w-[44px] items-center gap-2 rounded-full bg-primary/10 px-5 py-2.5 text-sm font-medium text-primary hover:bg-primary/20"
                >
                  <span className="material-symbols-outlined text-[22px]">
                    volume_up
                  </span>
                  播放發音
                </button>
                <p className="mt-6 text-xs text-gray-300">點擊翻面</p>
              </div>

              {/* Back */}
              <div className="card-back flex flex-col items-center justify-center rounded-2xl border border-gray-200 bg-white p-6 shadow-md">
                <p className="text-sm text-gray-400">{word!.word}</p>
                <p className="mt-3 text-2xl font-bold text-gray-900">
                  {word!.zh_definition ?? '（無中文定義）'}
                </p>
                {word!.pos && (
                  <span className="mt-2 inline-block rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">
                    {word!.pos}
                  </span>
                )}
                {word!.zh_definition && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      speakZh(word!.zh_definition!);
                    }}
                    className="mt-4 flex min-h-[44px] min-w-[44px] items-center gap-2 rounded-full bg-primary/10 px-5 py-2.5 text-sm font-medium text-primary hover:bg-primary/20"
                  >
                    <span className="material-symbols-outlined text-[22px]">
                      volume_up
                    </span>
                    播放中文
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Bottom controls */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between gap-3">
          <button
            onClick={goPrev}
            disabled={index <= 0}
            className="flex items-center gap-1 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-30"
          >
            <span className="material-symbols-outlined text-[20px]">
              arrow_back
            </span>
            上一張
          </button>
          <button
            onClick={handleFlip}
            disabled={isComplete}
            className="rounded-lg bg-gray-100 px-6 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-30"
          >
            翻面
          </button>
          <button
            onClick={goNext}
            className="flex items-center gap-1 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary/90"
          >
            {isComplete ? '重新開始' : '下一張'}
            <span className="material-symbols-outlined text-[20px]">
              {isComplete ? 'replay' : 'arrow_forward'}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
