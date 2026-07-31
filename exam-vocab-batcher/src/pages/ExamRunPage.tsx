import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { speakEn } from '../services/tts';
import type { ExamQuestion, ExamMode } from '../services/exam';
import type { ExamQuestionRecord } from '../types/exam';

interface ExamRunState {
  questions: ExamQuestion[];
  minPage: number;
  maxPage: number;
  mode: ExamMode;
}

export default function ExamRunPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state as ExamRunState | undefined;

  const [index, setIndex] = useState(0);
  const [records, setRecords] = useState<ExamQuestionRecord[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [answered, setAnswered] = useState(false);

  if (!state || state.questions.length === 0) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg-light px-4 text-center">
        <p className="text-gray-400">找不到考試資料，請重新設定考試</p>
        <button
          onClick={() => navigate('/exam')}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white"
        >
          回到考試設定
        </button>
      </div>
    );
  }

  const { questions, minPage, maxPage, mode } = state;
  const question = questions[index];
  const isLast = index === questions.length - 1;

  const handleSelect = (optionIndex: number) => {
    if (answered) return;
    setSelected(optionIndex);
    setAnswered(true);
  };

  const handleNext = () => {
    const correct = selected === question.correctIndex;
    const nextRecords: ExamQuestionRecord[] = [
      ...records,
      { word: question.word.word, type: question.type, correct },
    ];

    if (isLast) {
      navigate('/exam/result', {
        state: { questions, records: nextRecords, minPage, maxPage, mode },
      });
      return;
    }

    setRecords(nextRecords);
    setIndex(index + 1);
    setSelected(null);
    setAnswered(false);
  };

  const questionLabel =
    question.type === 'zh_to_en'
      ? '請選出正確英文單字'
      : question.type === 'en_to_zh'
        ? '請選出正確中文意思'
        : '請聽發音，選出正確中文意思';

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title={`第 ${index + 1} / ${questions.length} 題`}
        onBack={() => navigate('/exam')}
      />

      <main className="flex-1 px-4 py-6">
        <p className="mb-3 text-sm font-medium text-gray-500">{questionLabel}</p>

        <div className="mb-6 flex min-h-[96px] items-center justify-center rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          {question.type === 'listening' ? (
            <button
              onClick={() => speakEn(question.word.word)}
              className="flex min-h-[44px] min-w-[44px] items-center gap-2 rounded-full bg-primary/10 px-5 py-2.5 text-sm font-medium text-primary hover:bg-primary/20"
            >
              <span className="material-symbols-outlined text-[22px]">
                volume_up
              </span>
              播放發音
            </button>
          ) : question.type === 'zh_to_en' ? (
            <p className="text-2xl font-bold text-gray-900">
              {question.word.zh_definition}
            </p>
          ) : (
            <p className="text-2xl font-bold text-gray-900">
              {question.word.word}
            </p>
          )}
        </div>

        <div className="space-y-2">
          {question.options.map((opt, i) => {
            const isCorrect = i === question.correctIndex;
            const isSelected = i === selected;
            let style =
              'border-gray-200 bg-white text-gray-800 hover:bg-gray-50';
            if (answered) {
              if (isCorrect) {
                style = 'border-green-500 bg-green-50 text-green-700';
              } else if (isSelected) {
                style = 'border-red-400 bg-red-50 text-red-600';
              } else {
                style = 'border-gray-200 bg-white text-gray-400';
              }
            }
            return (
              <button
                key={i}
                onClick={() => handleSelect(i)}
                disabled={answered}
                className={`w-full rounded-xl border px-4 py-3 text-left text-base font-medium transition-colors ${style}`}
              >
                {opt}
              </button>
            );
          })}
        </div>
      </main>

      <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
        <button
          onClick={handleNext}
          disabled={!answered}
          className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isLast ? '看結果' : '下一題'}
        </button>
      </div>
    </div>
  );
}
