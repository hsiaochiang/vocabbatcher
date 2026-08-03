export type VocabSource = 'cap' | 'gsat';

export const VOCAB_SOURCE_LABEL: Record<VocabSource, string> = {
  cap: '會考',
  gsat: '學測',
};

export const VOCAB_SOURCE_FILE: Record<VocabSource, string> = {
  cap: 'data/vocab.cleaned.json',
  gsat: 'data/vocab.gsat.cleaned.json',
};

export interface VocabEntry {
  word: string;
  pos: string | null;
  zh_definition: string | null;
  frequency: number | null;
  level?: string | null;
  source_page: number[];
  ipa_us: string | null;
  ipa_uk: string | null;
  parse_confidence: number;
  issues: string[];
}
