import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { doc, increment, serverTimestamp, writeBatch } from 'firebase/firestore';
import Header from '../components/Header';
import SpeakButton from '../components/SpeakButton';
import UserBadge from '../components/UserBadge';
import { onAuthStateChange, type User } from '../services/auth';
import { db } from '../services/firebase';
import type { ExamQuestion, ExamMode } from '../services/exam';
import type { ExamQuestionRecord } from '../types/exam';

interface ExamResultState {
  questions: ExamQuestion[];
  records: ExamQuestionRecord[];
  minPage: number;
  maxPage: number;
  mode: ExamMode;
}

const TYPE_LABEL: Record<ExamQuestionRecord['type'], string> = {
  zh_to_en: '中→英',
  en_to_zh: '英→中',
  listening: '聽力',
  spelling: '拼字',
};

export default function ExamResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as ExamResultState | undefined;

  const [user, setUser] = useState<User | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChange(setUser);
    return unsubscribe;
  }, []);

  useEffect(() => {
    if (!state || !user || !db || saved) return;
    const firestore = db;
    const currentUser = user;
    const { records, minPage, maxPage, mode } = state;
    const score = records.filter((r) => r.correct).length;
    const id = crypto.randomUUID();

    async function saveResult() {
      const batch = writeBatch(firestore);

      batch.set(doc(firestore, 'users', currentUser.uid, 'examResults', id), {
        id,
        date: new Date().toISOString(),
        mode,
        pageRange: [minPage, maxPage],
        questionCount: records.length,
        score,
        questions: records,
        createdAt: serverTimestamp(),
      });

      records.forEach((record) => {
        batch.set(
          doc(firestore, 'users', currentUser.uid, 'wordStats', record.word),
          {
            word: record.word,
            attempts: increment(1),
            wrong: increment(record.correct ? 0 : 1),
          },
          { merge: true },
        );
      });

      await batch.commit();
      setSaved(true);
    }

    saveResult().catch((err) => console.error('儲存考試成績失敗:', err));
  }, [state, user, saved]);

  if (!state) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg-light px-4 text-center">
        <p className="text-gray-600">找不到考試結果</p>
        <button
          onClick={() => navigate('/exam')}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white"
        >
          回到考試設定
        </button>
      </div>
    );
  }

  const { questions, records } = state;
  const score = records.filter((r) => r.correct).length;

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title="考試結果"
        onBack={() => navigate('/')}
        rightSlot={<UserBadge />}
      />

      <main className="flex-1 space-y-4 px-4 py-4 pb-24">
        <section className="rounded-2xl border border-gray-200 bg-white p-6 text-center shadow-sm">
          <p className="text-sm text-gray-500">得分</p>
          <p className="mt-1 text-4xl font-bold text-primary">
            {score} / {records.length}
          </p>
        </section>

        {!user && (
          <div className="flex items-center gap-2 rounded-lg bg-yellow-50 px-4 py-3 text-sm text-yellow-700">
            <span className="material-symbols-outlined text-[18px]">info</span>
            訪客模式，成績不會保存
          </div>
        )}

        <section className="space-y-2">
          {records.map((record, i) => {
            const question = questions[i];
            return (
              <div
                key={`${record.word}-${i}`}
                className="flex items-center justify-between gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3"
              >
                <div className="flex min-w-0 items-center gap-2">
                  <span
                    className={`material-symbols-outlined text-[20px] ${
                      record.correct ? 'text-green-500' : 'text-red-400'
                    }`}
                  >
                    {record.correct ? 'check_circle' : 'cancel'}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate font-semibold text-gray-900">
                      {record.word}
                    </p>
                    <p className="text-xs text-gray-500">
                      {TYPE_LABEL[record.type]} ・ {question?.word.zh_definition}
                    </p>
                  </div>
                </div>
                <SpeakButton word={record.word} className="shrink-0" />
              </div>
            );
          })}
        </section>
      </main>

      <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
        <button
          onClick={() => navigate('/exam')}
          className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-primary/90"
        >
          再考一次
        </button>
      </div>
    </div>
  );
}
