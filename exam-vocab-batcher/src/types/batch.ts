import type { VocabEntry } from './vocab';

export interface Batch {
  id: string;
  name: string;
  createdAt: string;
  lastAccessedAt: string;
  words: VocabEntry[];
  flashcardIndex: number;
}
