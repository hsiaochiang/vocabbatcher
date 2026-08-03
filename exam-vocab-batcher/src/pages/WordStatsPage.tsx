import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { collection, getDocs } from 'firebase/firestore';
import Header from '../components/Header';
import SpeakButton from '../components/SpeakButton';
import Toast from '../components/Toast';
import UserBadge from '../components/UserBadge';
import { generateReviewExam } from '../services/exam';
import { onAuthStateChange, type User } from '../services/auth';
import { db } from '../services/firebase';
import { useApp } from '../store/AppContext';
import type { WordStat } from '../types/exam';

const REVIEW_QUESTION_COUNT = 10;

function formatRate(rate: number) {
  return `${Math.round(rate * 100)}%`;
}

export default function WordStatsPage() {
  const navigate = useNavigate();
  const { allWords, isLoading: vocabLoading } = useApp();
  const [user, setUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [stats, setStats] = useState<WordStat[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [toastVisible, setToastVisible] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChange((nextUser) => {
      setUser(nextUser);
      setAuthReady(true);
    });
    return unsubscribe;
  }, []);

  useEffect(() => {
    if (!authReady || !user || !db) return;
    const firestore = db;
    const currentUser = user;

    async function loadStats() {
      setIsLoading(true);
      try {
        const snapshot = await getDocs(
          collection(firestore, 'users', currentUser.uid, 'wordStats'),
        );
        const nextStats = snapshot.docs
          .map((docSnapshot) => {
            const data = docSnapshot.data();
            const attempts = Number(data.attempts ?? 0);
            const wrong = Number(data.wrong ?? 0);

            return {
              word: String(data.word ?? docSnapshot.id),
              attempts,
              wrong,
              wrongRate: attempts > 0 ? wrong / attempts : 0,
            };
          })
          .filter((stat) => stat.attempts > 0)
          .sort((a, b) => {
            if (b.wrongRate !== a.wrongRate) {
              return b.wrongRate - a.wrongRate;
            }
            if (b.wrong !== a.wrong) return b.wrong - a.wrong;
            if (b.attempts !== a.attempts) return b.attempts - a.attempts;
            return a.word.localeCompare(b.word);
          });

        setStats(nextStats);
      } catch (err) {
        console.error('讀取單字統計失敗:', err);
      } finally {
        setIsLoading(false);
      }
    }

    loadStats();
  }, [authReady, user]);

  const wrongStats = stats.filter((stat) => stat.wrong > 0);
  const canStartReview =
    Boolean(user) && wrongStats.length > 0 && allWords.length > 0 && !vocabLoading;

  const handleStartReview = () => {
    if (!canStartReview) {
      setToastVisible(true);
      return;
    }

    const questions = generateReviewExam(allWords, stats, {
      questionCount: REVIEW_QUESTION_COUNT,
    });

    if (questions.length === 0) {
      setToastVisible(true);
      return;
    }

    const pages = questions.flatMap((question) => question.word.source_page);
    const minPage = pages.length > 0 ? Math.min(...pages) : 1;
    const maxPage = pages.length > 0 ? Math.max(...pages) : 1;

    navigate('/exam/run', {
      state: {
        questions,
        minPage,
        maxPage,
        mode: 'mixed',
      },
    });
  };

  const reviewButtonLabel =
    wrongStats.length === 0
      ? '還沒有錯題可以複習'
      : vocabLoading || allWords.length === 0
        ? '單字資料載入中…'
        : '錯題複習';

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title="單字統計"
        onBack={() => navigate('/')}
        rightSlot={<UserBadge />}
      />

      <main className="flex-1 px-4 py-4 pb-24">
        {!authReady || isLoading ? (
          <div className="flex justify-center py-16 text-sm text-gray-600">
            載入中…
          </div>
        ) : !user ? (
          <div className="rounded-xl border border-yellow-200 bg-yellow-50 px-4 py-4 text-sm text-yellow-700">
            請先登入，才看得到雲端累積的單字錯誤統計。
          </div>
        ) : stats.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-center">
            <span className="material-symbols-outlined mb-3 text-5xl text-gray-300">
              bar_chart
            </span>
            <p className="text-gray-600">還沒有單字統計資料</p>
          </div>
        ) : (
          <section className="space-y-2">
            {stats.map((stat) => (
              <article
                key={stat.word}
                className="flex items-center justify-between gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="truncate font-semibold text-gray-900">
                      {stat.word}
                    </p>
                    <SpeakButton word={stat.word} className="shrink-0" />
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    錯 {stat.wrong} 次 / 考 {stat.attempts} 次
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <p className="text-lg font-bold text-red-500">
                    {formatRate(stat.wrongRate)}
                  </p>
                  <p className="text-xs text-gray-500">錯誤率</p>
                </div>
              </article>
            ))}
          </section>
        )}
      </main>

      {authReady && user && !isLoading && (
        <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
          <button
            onClick={handleStartReview}
            disabled={!canStartReview}
            className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {reviewButtonLabel}
          </button>
        </div>
      )}

      <Toast
        message="目前還沒有可用的錯題複習資料"
        visible={toastVisible}
        onHide={() => setToastVisible(false)}
      />
    </div>
  );
}
