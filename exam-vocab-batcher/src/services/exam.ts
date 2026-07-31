import type { VocabEntry } from '../types/vocab';
import type { QuestionType } from '../types/exam';

export type ExamMode = 'mixed' | 'listening';

export interface ExamQuestion {
  word: VocabEntry;
  type: QuestionType;
  options: string[];
  correctIndex: number;
}

export interface GenerateExamOptions {
  minPage: number;
  maxPage: number;
  questionCount: number;
  mode: ExamMode;
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function pickDistractors(
  pool: VocabEntry[],
  exclude: VocabEntry,
  count: number,
): VocabEntry[] {
  const candidates = pool.filter((w) => w.word !== exclude.word);
  return shuffle(candidates).slice(0, count);
}

function buildQuestion(
  word: VocabEntry,
  type: QuestionType,
  pool: VocabEntry[],
): ExamQuestion | null {
  if (!word.zh_definition) return null;
  const distractors = pickDistractors(pool, word, 3);
  if (distractors.length < 3) return null;

  const candidates = [word, ...distractors];
  const shuffled = shuffle(candidates);

  const options =
    type === 'zh_to_en'
      ? shuffled.map((w) => w.word)
      : shuffled.map((w) => w.zh_definition ?? w.word);
  const correctIndex = shuffled.findIndex((w) => w.word === word.word);

  return { word, type, options, correctIndex };
}

const QUESTION_TYPES: QuestionType[] = ['zh_to_en', 'en_to_zh', 'listening'];

export function generateExam(
  allWords: VocabEntry[],
  options: GenerateExamOptions,
): ExamQuestion[] {
  const { minPage, maxPage, questionCount, mode } = options;

  const pool = allWords.filter(
    (w) =>
      w.zh_definition &&
      w.source_page.some((p) => p >= minPage && p <= maxPage),
  );

  const candidates = shuffle(pool).slice(0, questionCount);

  const questions: ExamQuestion[] = [];
  for (const word of candidates) {
    const type: QuestionType =
      mode === 'listening'
        ? 'listening'
        : QUESTION_TYPES[Math.floor(Math.random() * QUESTION_TYPES.length)];
    const q = buildQuestion(word, type, pool);
    if (q) questions.push(q);
  }
  return questions;
}

export function getPageRange(allWords: VocabEntry[]): [number, number] {
  let min = Infinity;
  let max = 0;
  for (const w of allWords) {
    for (const p of w.source_page) {
      if (p < min) min = p;
      if (p > max) max = p;
    }
  }
  if (!Number.isFinite(min)) return [1, 1];
  return [min, max];
}
