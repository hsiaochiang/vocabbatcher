export interface VocabEntry {
  word: string;
  pos: string | null;
  zh_definition: string | null;
  frequency: number | null;
  source_page: number[];
  ipa_us: string | null;
  ipa_uk: string | null;
  parse_confidence: number;
  issues: string[];
}
