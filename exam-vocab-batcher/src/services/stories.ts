import type { VocabSource } from '../types/vocab';

export interface StorySentence {
  index: number;
  text: string;
  zh: string;
  targetWords: string[];
}

export interface GsatStory {
  id: string;
  source: 'gsat';
  page: number;
  theme: 'minecraft';
  wordList: string[];
  generatedAt: string;
  sentences: StorySentence[];
}

export interface GsatStoriesData {
  schemaVersion: number;
  stories: GsatStory[];
}

export async function loadGsatStories(): Promise<GsatStoriesData> {
  const response = await fetch(`${import.meta.env.BASE_URL}data/stories.gsat.json`);
  if (!response.ok) {
    throw new Error(`Failed to load stories.gsat.json: HTTP ${response.status}`);
  }
  return (await response.json()) as GsatStoriesData;
}

export function findMinecraftStory(
  storiesData: GsatStoriesData | null,
  source: VocabSource,
  sourcePage: number | undefined,
): GsatStory | undefined {
  if (!storiesData || source !== 'gsat' || sourcePage == null) {
    return undefined;
  }

  return storiesData.stories.find(
    (story) =>
      story.source === 'gsat' &&
      story.page === sourcePage &&
      story.theme === 'minecraft',
  );
}
