export type QuestionType = 'zh_to_en' | 'en_to_zh' | 'listening' | 'spelling';

export interface ExamQuestionRecord {
  word: string;
  type: QuestionType;
  correct: boolean;
}

export interface ExamResult {
  id: string;
  date: string;
  mode: 'mixed' | 'listening';
  pageRange: [number, number];
  questionCount: number;
  score: number;
  questions: ExamQuestionRecord[];
}

export interface WordStat {
  word: string;
  attempts: number;
  wrong: number;
  wrongRate: number;
}
