import { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';
import Toast from '../components/Toast';
import UserBadge from '../components/UserBadge';
import { generateExam, getPageRange, type ExamMode } from '../services/exam';

const QUICK_COUNTS = [5, 10, 20];

interface ExamSetupState {
  initialMinPage?: number;
  initialMaxPage?: number;
}

export default function ExamSetupPage() {
  const { allWords } = useApp();
  const location = useLocation();
  const navigate = useNavigate();
  const setupState = location.state as ExamSetupState | undefined;

  const [globalMin, globalMax] = useMemo(() => getPageRange(allWords), [allWords]);
  const [pageRange, setPageRange] = useState<{
    minPage: number;
    maxPage: number;
  } | null>(() =>
    setupState?.initialMinPage != null && setupState.initialMaxPage != null
      ? {
          minPage: setupState.initialMinPage,
          maxPage: setupState.initialMaxPage,
        }
      : null,
  );
  const [questionCount, setQuestionCount] = useState(10);
  const [mode, setMode] = useState<ExamMode>('mixed');
  const [toastVisible, setToastVisible] = useState(false);
  const minPage = pageRange?.minPage ?? globalMin;
  const maxPage = pageRange?.maxPage ?? globalMax;
  const pageRangeInvalid = minPage > maxPage;

  const handleStart = () => {
    if (pageRangeInvalid) return;

    const questions = generateExam(allWords, {
      minPage,
      maxPage,
      questionCount,
      mode,
    });
    if (questions.length === 0) {
      setToastVisible(true);
      return;
    }
    navigate('/exam/run', {
      state: {
        questions,
        minPage,
        maxPage,
        mode,
      },
    });
  };

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title="考試設定"
        onBack={() => navigate('/')}
        rightSlot={<UserBadge />}
      />

      <main className="flex-1 space-y-6 px-4 py-4">
        <section>
          <h2 className="mb-2 text-sm font-medium text-gray-500">頁數範圍</h2>
          <div className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-4">
            <input
              type="number"
              min={globalMin}
              max={maxPage}
              value={minPage}
              onChange={(e) =>
                setPageRange({ minPage: Number(e.target.value), maxPage })
              }
              className={`w-20 rounded-lg border px-3 py-2 text-center text-sm outline-none focus:ring-1 ${
                pageRangeInvalid
                  ? 'border-red-300 focus:border-red-400 focus:ring-red-300'
                  : 'border-gray-200 focus:border-primary focus:ring-primary'
              }`}
            />
            <span className="text-gray-500">至</span>
            <input
              type="number"
              min={minPage}
              max={globalMax}
              value={maxPage}
              onChange={(e) =>
                setPageRange({ minPage, maxPage: Number(e.target.value) })
              }
              className={`w-20 rounded-lg border px-3 py-2 text-center text-sm outline-none focus:ring-1 ${
                pageRangeInvalid
                  ? 'border-red-300 focus:border-red-400 focus:ring-red-300'
                  : 'border-gray-200 focus:border-primary focus:ring-primary'
              }`}
            />
            <span className="text-sm text-gray-500">
              頁（全書 {globalMin}~{globalMax} 頁）
            </span>
          </div>
          {pageRangeInvalid && (
            <p className="mt-2 text-sm text-red-600">
              最小頁不能大於最大頁，請調整頁數範圍。
            </p>
          )}
        </section>

        <section>
          <h2 className="mb-2 text-sm font-medium text-gray-500">題數</h2>
          <div className="flex gap-2">
            {QUICK_COUNTS.map((n) => (
              <button
                key={n}
                onClick={() => setQuestionCount(n)}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                  questionCount === n
                    ? 'border-primary bg-primary text-white'
                    : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {n} 題
              </button>
            ))}
            <input
              type="number"
              min={1}
              max={100}
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
              className="w-16 rounded-lg border border-gray-200 px-2 py-2 text-center text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>
        </section>

        <section>
          <h2 className="mb-2 text-sm font-medium text-gray-500">模式</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setMode('mixed')}
              className={`flex-1 rounded-lg border px-3 py-3 text-sm font-medium transition-colors ${
                mode === 'mixed'
                  ? 'border-primary bg-primary text-white'
                  : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              混合（中英交互＋聽力）
            </button>
            <button
              onClick={() => setMode('listening')}
              className={`flex-1 rounded-lg border px-3 py-3 text-sm font-medium transition-colors ${
                mode === 'listening'
                  ? 'border-primary bg-primary text-white'
                  : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              純聽力
            </button>
          </div>
        </section>
      </main>

      <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
        <button
          onClick={handleStart}
          disabled={pageRangeInvalid}
          className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          開始考試
        </button>
      </div>

      <Toast
        message="此頁數範圍內單字不足，無法出題"
        visible={toastVisible}
        onHide={() => setToastVisible(false)}
      />
    </div>
  );
}
