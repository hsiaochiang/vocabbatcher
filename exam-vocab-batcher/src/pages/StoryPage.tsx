import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Header from '../components/Header';
import SpeakButton from '../components/SpeakButton';
import UserBadge from '../components/UserBadge';
import { speakEn } from '../services/tts';
import {
  findMinecraftStory,
  loadGsatStories,
  type GsatStory,
} from '../services/stories';
import { useApp } from '../store/AppContext';

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function renderEnglish(text: string, targetWords: string[]) {
  const words = targetWords
    .filter(Boolean)
    .sort((a, b) => b.length - a.length)
    .map(escapeRegExp);

  if (words.length === 0) return text;

  const pattern = new RegExp(`\\b(${words.join('|')})\\b`, 'gi');
  const parts = text.split(pattern);
  const targetSet = new Set(targetWords.map((word) => word.toLowerCase()));

  return parts.map((part, index) =>
    targetSet.has(part.toLowerCase()) ? (
      <strong key={`${part}-${index}`} className="font-bold text-gray-950">
        {part}
      </strong>
    ) : (
      part
    ),
  );
}

function renderChinese(zh: string, targetWords: string[]) {
  const words = targetWords
    .filter(Boolean)
    .sort((a, b) => b.length - a.length)
    .map(escapeRegExp);

  if (words.length === 0) return zh;

  const pattern = new RegExp(`([（(])(${words.join('|')})([）)])`, 'gi');
  const parts: Array<string | { word: string; bracketed: string }> = [];
  let lastIndex = 0;

  for (const match of zh.matchAll(pattern)) {
    if (match.index == null) continue;
    if (match.index > lastIndex) {
      parts.push(zh.slice(lastIndex, match.index));
    }
    parts.push({ word: match[2], bracketed: match[0] });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < zh.length) {
    parts.push(zh.slice(lastIndex));
  }

  return parts.map((part, index) => {
    if (typeof part === 'string') return part;

    return (
      <button
        key={`${part.word}-${index}`}
        type="button"
        onClick={() => speakEn(part.word)}
        className="mx-0.5 inline-flex min-h-[32px] items-center rounded-full bg-primary/10 px-2 py-1 text-sm font-semibold text-primary transition-colors hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-primary/30"
        aria-label={`播放 ${part.word} 的英文發音`}
      >
        {part.bracketed}
      </button>
    );
  });
}

export default function StoryPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { source, setSource, batches } = useApp();
  const [storyState, setStoryState] = useState<{
    key: string;
    story: GsatStory | null;
    failed: boolean;
  } | null>(null);

  const batch = useMemo(() => batches.find((item) => item.id === id), [batches, id]);
  const storyKey =
    batch?.source === 'gsat' && batch.sourcePage != null
      ? `${batch.id}:${batch.sourcePage}`
      : null;
  const story = storyKey === storyState?.key ? storyState.story : null;
  const loading = storyKey != null && storyState?.key !== storyKey;
  const loadFailed = storyKey === storyState?.key && storyState.failed;

  useEffect(() => {
    if (batch && batch.source !== source) {
      setSource(batch.source);
    }
  }, [batch, setSource, source]);

  useEffect(() => {
    let cancelled = false;

    if (!batch || storyKey == null) {
      return () => {
        cancelled = true;
      };
    }

    loadGsatStories()
      .then((storiesData) => {
        if (cancelled) return;
        setStoryState({
          key: storyKey,
          story:
            findMinecraftStory(storiesData, batch.source, batch.sourcePage) ??
            null,
          failed: false,
        });
      })
      .catch((err) => {
        console.error('Failed to load story:', err);
        if (cancelled) return;
        setStoryState({ key: storyKey, story: null, failed: true });
      });

    return () => {
      cancelled = true;
    };
  }, [batch, storyKey]);

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-light">
        <Header
          title="故事模式"
          onBack={() => navigate(id ? `/batch/${id}` : '/')}
          rightSlot={<UserBadge />}
        />
        <main className="flex flex-1 items-center justify-center px-4">
          <p className="text-gray-600">故事載入中…</p>
        </main>
      </div>
    );
  }

  if (!batch || !story) {
    return (
      <div className="flex min-h-screen flex-col bg-bg-light">
        <Header
          title="故事模式"
          onBack={() => navigate(id ? `/batch/${id}` : '/')}
          rightSlot={<UserBadge />}
        />
        <main className="flex flex-1 items-center justify-center px-4 text-center">
          <div>
            <span className="material-symbols-outlined mb-3 text-5xl text-gray-300">
              auto_stories
            </span>
            <h2 className="text-lg font-bold text-gray-900">找不到故事內容</h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              {loadFailed
                ? '故事資料暫時無法載入，請稍後再試。'
                : '這個批次沒有可用的故事模式。'}
            </p>
            <button
              type="button"
              onClick={() => navigate(id ? `/batch/${id}` : '/')}
              className="mt-5 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-primary/90"
            >
              返回批次
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title="故事模式"
        onBack={() => navigate(`/batch/${batch.id}`)}
        rightSlot={<UserBadge />}
      />

      <main className="flex-1 px-4 pb-10 pt-4">
        <section className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <p className="text-xs font-semibold text-amber-700">
            學測第 {story.page} 頁
          </p>
          <h2 className="mt-1 text-xl font-bold text-gray-950">
            Minecraft 故事
          </h2>
          <p className="mt-2 text-sm leading-6 text-gray-700">
            本頁 {story.wordList.length} 個單字，分成 {story.sentences.length}{' '}
            句閱讀。
          </p>
        </section>

        <ol className="space-y-3">
          {story.sentences.map((sentence) => (
            <li
              key={sentence.index}
              className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex items-start gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold text-gray-600">
                  {sentence.index + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-start gap-2">
                    <p className="flex-1 text-base leading-7 text-gray-900">
                      {renderEnglish(sentence.text, sentence.targetWords)}
                    </p>
                    <SpeakButton word={sentence.text} className="shrink-0" />
                  </div>
                  <p className="mt-3 text-sm leading-7 text-gray-700">
                    {renderChinese(sentence.zh, sentence.targetWords)}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </main>
    </div>
  );
}
