import type { VocabEntry } from './vocab';
import type { VocabSource } from './vocab';

export interface Batch {
  id: string;
  name: string;
  source: VocabSource;
  createdAt: string;
  lastAccessedAt: string;
  words: VocabEntry[];
  flashcardIndex: number;
}
