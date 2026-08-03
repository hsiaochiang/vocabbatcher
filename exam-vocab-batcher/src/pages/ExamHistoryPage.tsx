import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { collection, getDocs, orderBy, query } from 'firebase/firestore';
import Header from '../components/Header';
import SpeakButton from '../components/SpeakButton';
import UserBadge from '../components/UserBadge';
import { onAuthStateChange, type User } from '../services/auth';
import { db } from '../services/firebase';
import { useApp } from '../store/AppContext';
import { VOCAB_SOURCE_LABEL, type VocabSource } from '../types/vocab';
import type { ExamQuestionRecord, ExamResult } from '../types/exam';

const MODE_LABEL: Record<ExamResult['mode'], string> = {
  mixed: '混合題',
  listening: '聽力題',
};

const TYPE_LABEL: Record<ExamQuestionRecord['type'], string> = {
  zh_to_en: '中→英',
  en_to_zh: '英→中',
  listening: '聽力',
  spelling: '拼字',
};

function formatDate(date: string) {
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return date;

  return parsed.toLocaleString('zh-TW', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function ExamHistoryPage() {
  const navigate = useNavigate();
  const { source } = useApp();
  const [user, setUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [results, setResults] = useState<ExamResult[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

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

    async function loadResults() {
      setIsLoading(true);
      try {
        const snapshot = await getDocs(
          query(
            collection(firestore, 'users', currentUser.uid, 'examResults'),
            orderBy('date', 'desc'),
          ),
        );
        setResults(
          snapshot.docs
            .map((docSnapshot) => normalizeExamResult(docSnapshot.id, docSnapshot.data()))
            .filter((result) => result.source === source),
        );
      } catch (err) {
        console.error('讀取成績歷史失敗:', err);
      } finally {
        setIsLoading(false);
      }
    }

    loadResults();
  }, [authReady, source, user]);

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title="成績歷史"
        onBack={() => navigate('/')}
        rightSlot={<UserBadge />}
      />

      <main className="flex-1 px-4 py-4">
        {!authReady || isLoading ? (
          <div className="flex justify-center py-16 text-sm text-gray-600">
            載入中…
          </div>
        ) : !user ? (
          <div className="rounded-xl border border-yellow-200 bg-yellow-50 px-4 py-4 text-sm text-yellow-700">
            請先登入，才看得到雲端保存的成績歷史。
          </div>
        ) : results.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-center">
            <span className="material-symbols-outlined mb-3 text-5xl text-gray-300">
              history
            </span>
            <p className="text-gray-600">
              還沒有{VOCAB_SOURCE_LABEL[source]}考試成績
            </p>
          </div>
        ) : (
          <section className="space-y-3">
            {results.map((result) => {
              const isExpanded = expandedId === result.id;
              const [minPage, maxPage] = result.pageRange;

              return (
                <article
                  key={result.id}
                  className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
                >
                  <button
                    onClick={() =>
                      setExpandedId(isExpanded ? null : result.id)
                    }
                    className="flex w-full items-center justify-between gap-3 text-left"
                  >
                    <div className="min-w-0">
                      <p className="font-semibold text-gray-900">
                        {formatDate(result.date)}
                      </p>
                      <p className="mt-1 text-sm text-gray-500">
                        {MODE_LABEL[result.mode]} · 第 {minPage}-{maxPage} 頁 ·{' '}
                        {result.questionCount} 題
                      </p>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600">
                        {VOCAB_SOURCE_LABEL[result.source]}
                      </span>
                      <span className="text-lg font-bold text-primary">
                        {result.score}/{result.questionCount}
                      </span>
                      <span className="material-symbols-outlined text-gray-300">
                        {isExpanded ? 'expand_less' : 'expand_more'}
                      </span>
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="mt-4 space-y-2 border-t border-gray-100 pt-3">
                      {result.questions.map((question, index) => (
                        <div
                          key={`${result.id}-${question.word}-${index}`}
                          className="flex items-center justify-between gap-3 rounded-lg bg-gray-50 px-3 py-2"
                        >
                          <div className="flex min-w-0 items-center gap-2">
                            <span
                              className={`material-symbols-outlined text-[18px] ${
                                question.correct
                                  ? 'text-green-500'
                                  : 'text-red-400'
                              }`}
                            >
                              {question.correct ? 'check_circle' : 'cancel'}
                            </span>
                            <div className="min-w-0">
                              <p className="truncate text-sm font-medium text-gray-900">
                                {question.word}
                              </p>
                              <p className="text-xs text-gray-500">
                                {TYPE_LABEL[question.type]}
                              </p>
                            </div>
                          </div>
                          <SpeakButton
                            word={question.word}
                            className="shrink-0"
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              );
            })}
          </section>
        )}
      </main>
    </div>
  );
}

function normalizeExamResult(id: string, data: unknown): ExamResult {
  const result = data as Partial<ExamResult>;
  return {
    ...(result as ExamResult),
    id,
    source: parseStoredSource(result.source),
  };
}

function parseStoredSource(rawSource: unknown): VocabSource {
  return rawSource === 'gsat' ? 'gsat' : 'cap';
}
