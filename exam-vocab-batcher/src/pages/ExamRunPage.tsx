import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import UserBadge from '../components/UserBadge';
import type { VocabSource } from '../types/vocab';
import { speakEn } from '../services/tts';
import {
  isSpellingCorrect,
  type ExamQuestion,
  type ExamMode,
} from '../services/exam';
import type { ExamQuestionRecord } from '../types/exam';

interface ExamRunState {
  questions: ExamQuestion[];
  source?: VocabSource;
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
  const [spellingInput, setSpellingInput] = useState('');
  const [answered, setAnswered] = useState(false);
  const [answerCorrect, setAnswerCorrect] = useState<boolean | null>(null);

  if (!state || state.questions.length === 0) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-bg-light px-4 text-center">
        <p className="text-gray-600">找不到考試資料，請重新設定考試</p>
        <button
          onClick={() => navigate('/exam')}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white"
        >
          回到考試設定
        </button>
      </div>
    );
  }

  const { questions, source, minPage, maxPage, mode } = state;
  const question = questions[index];
  const isLast = index === questions.length - 1;

  const handleSelect = (optionIndex: number) => {
    if (answered) return;
    setSelected(optionIndex);
    setAnswerCorrect(optionIndex === question.correctIndex);
    setAnswered(true);
  };

  const handleSubmitSpelling = () => {
    if (answered) return;
    const correctAnswer = question.correctAnswer ?? question.word.word;
    setAnswerCorrect(isSpellingCorrect(spellingInput, correctAnswer));
    setAnswered(true);
  };

  const handleNext = () => {
    const correct = answerCorrect ?? false;
    const nextRecords: ExamQuestionRecord[] = [
      ...records,
      { word: question.word.word, type: question.type, correct },
    ];

    if (isLast) {
      navigate('/exam/result', {
        state: { questions, source, records: nextRecords, minPage, maxPage, mode },
      });
      return;
    }

    setRecords(nextRecords);
    setIndex(index + 1);
    setSelected(null);
    setSpellingInput('');
    setAnswered(false);
    setAnswerCorrect(null);
  };

  const questionLabel =
    question.type === 'spelling'
      ? '請拼出正確的英文單字'
      : question.type === 'zh_to_en'
      ? '請選出正確英文單字'
      : question.type === 'en_to_zh'
        ? '請選出正確中文意思'
        : '請聽發音，選出正確中文意思';

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title={`第 ${index + 1} / ${questions.length} 題`}
        onBack={() => navigate('/exam')}
        rightSlot={<UserBadge />}
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
          ) : question.type === 'zh_to_en' || question.type === 'spelling' ? (
            <p className="text-2xl font-bold text-gray-900">
              {question.word.zh_definition}
            </p>
          ) : (
            <p className="text-2xl font-bold text-gray-900">
              {question.word.word}
            </p>
          )}
        </div>

        {question.type === 'spelling' ? (
          <div className="space-y-3">
            <input
              type="text"
              value={spellingInput}
              onChange={(event) => setSpellingInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && spellingInput.trim()) {
                  handleSubmitSpelling();
                }
              }}
              disabled={answered}
              autoCapitalize="off"
              autoCorrect="off"
              spellCheck={false}
              placeholder="輸入英文單字"
              className="min-h-[48px] w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-base font-medium text-gray-900 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-1 focus:ring-primary disabled:bg-gray-50 disabled:text-gray-600"
            />
            {!answered ? (
              <button
                onClick={handleSubmitSpelling}
                disabled={!spellingInput.trim()}
                className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40"
              >
                送出答案
              </button>
            ) : (
              <div
                className={`rounded-xl border px-4 py-3 ${
                  answerCorrect
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-red-400 bg-red-50 text-red-600'
                }`}
              >
                <div className="flex items-center gap-2 font-semibold">
                  <span className="material-symbols-outlined text-[20px]">
                    {answerCorrect ? 'check_circle' : 'cancel'}
                  </span>
                  {answerCorrect ? '答對了' : '拼錯了'}
                </div>
                <p className="mt-1 text-sm">
                  正確拼法：{question.correctAnswer ?? question.word.word}
                </p>
                {!answerCorrect && (
                  <p className="mt-1 text-sm text-red-500">
                    你的答案：{spellingInput || '（空白）'}
                  </p>
                )}
              </div>
            )}
          </div>
        ) : (
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
                  style = 'border-gray-200 bg-white text-gray-500';
                }
              }
              const feedbackIcon =
                answered && isCorrect
                  ? 'check_circle'
                  : answered && isSelected
                    ? 'cancel'
                    : null;
              return (
                <button
                  key={i}
                  onClick={() => handleSelect(i)}
                  disabled={answered}
                  className={`flex w-full items-center justify-between gap-3 rounded-xl border px-4 py-3 text-left text-base font-medium transition-colors ${style}`}
                >
                  <span>{opt}</span>
                  {feedbackIcon && (
                    <span
                      className={`material-symbols-outlined text-[20px] ${
                        isCorrect ? 'text-green-500' : 'text-red-400'
                      }`}
                    >
                      {feedbackIcon}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}
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
