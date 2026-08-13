import { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';
import WordCard from '../components/WordCard';
import SelectionCounter from '../components/SelectionCounter';
import Toast from '../components/Toast';
import UserBadge from '../components/UserBadge';
import { VOCAB_SOURCE_LABEL, type VocabEntry } from '../types/vocab';

const MAX_SELECTION = 25;

type FreqFilter = 'all' | 'high' | 'mid' | 'low';
type PosFilter = 'all' | 'n.' | 'v.' | 'adj.' | 'adv.' | 'pron.' | 'prep.' | 'conj.' | 'other';

const FREQ_OPTIONS: { value: FreqFilter; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'high', label: '高頻 ≥8' },
  { value: 'mid', label: '中頻 4-7' },
  { value: 'low', label: '低頻 ≤3' },
];

const POS_OPTIONS: { value: PosFilter; label: string }[] = [
  { value: 'all', label: '全部詞性' },
  { value: 'n.', label: '名詞' },
  { value: 'v.', label: '動詞' },
  { value: 'adj.', label: '形容詞' },
  { value: 'adv.', label: '副詞' },
  { value: 'pron.', label: '代名詞' },
  { value: 'prep.', label: '介系詞' },
  { value: 'conj.', label: '連接詞' },
  { value: 'other', label: '其他' },
];

function sameWordSet(a: VocabEntry[], b: VocabEntry[]) {
  if (a.length !== b.length) return false;

  const aWords = new Set(a.map((word) => word.word));
  return b.every((word) => aWords.has(word.word));
}

export default function BatchBuilderPage() {
  const { source, allWords, batches, createBatch, updateBatch, setActiveBatch } =
    useApp();
  const navigate = useNavigate();

  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [freqFilter, setFreqFilter] = useState<FreqFilter>('all');
  const [posFilter, setPosFilter] = useState<PosFilter>('all');
  const [search, setSearch] = useState('');
  const [toastVisible, setToastVisible] = useState(false);

  const sourceBatches = useMemo(
    () => batches.filter((batch) => batch.source === source),
    [batches, source],
  );

  const pageOptions = useMemo(() => {
    const pages = new Map<number, Map<string, VocabEntry>>();
    for (const word of allWords) {
      for (const page of word.source_page) {
        if (!pages.has(page)) {
          pages.set(page, new Map());
        }
        pages.get(page)?.set(word.word, word);
      }
    }

    return Array.from(pages.entries())
      .sort(([a], [b]) => a - b)
      .map(([page, words]) => ({
        page,
        words: Array.from(words.values()).sort((a, b) =>
          a.word.localeCompare(b.word),
        ),
      }));
  }, [allWords]);

  const filtered = useMemo(() => {
    return allWords.filter((w) => {
      // Frequency filter
      if (freqFilter !== 'all' && w.frequency != null) {
        if (freqFilter === 'high' && w.frequency < 8) return false;
        if (freqFilter === 'mid' && (w.frequency < 4 || w.frequency > 7))
          return false;
        if (freqFilter === 'low' && w.frequency > 3) return false;
      }
      // POS filter
      if (posFilter !== 'all') {
        if (posFilter === 'other') {
          const mainPos = ['n.', 'v.', 'adj.', 'adv.', 'pron.', 'prep.', 'conj.'];
          if (w.pos && mainPos.includes(w.pos)) return false;
        } else {
          if (w.pos !== posFilter) return false;
        }
      }
      // Search
      if (search.trim()) {
        if (!w.word.toLowerCase().includes(search.trim().toLowerCase()))
          return false;
      }
      return true;
    });
  }, [allWords, freqFilter, posFilter, search]);

  const isFull = selected.size >= MAX_SELECTION;

  const toggleWord = useCallback(
    (word: string) => {
      setSelected((prev) => {
        const next = new Set(prev);
        if (next.has(word)) {
          next.delete(word);
        } else if (next.size < MAX_SELECTION) {
          next.add(word);
        } else {
          setToastVisible(true);
          return prev;
        }
        return next;
      });
    },
    [],
  );

  const handleCreate = () => {
    const words = allWords.filter((w) => selected.has(w.word));
    const duplicate = sourceBatches.find((batch) => sameWordSet(batch.words, words));
    if (
      duplicate &&
      !window.confirm(
        `已經有一個內容相同的批次「${duplicate.name}」，仍要建立新的嗎？`,
      )
    ) {
      return;
    }

    const batch = createBatch(
      words,
      `批次 #${sourceBatches.length + 1}（${VOCAB_SOURCE_LABEL[source]}）`,
    );
    setActiveBatch(batch.id);
    navigate(`/batch/${batch.id}`);
  };

  const handleCreatePageBatch = (page: number, words: VocabEntry[]) => {
    const duplicate = sourceBatches.find((batch) => sameWordSet(batch.words, words));
    if (
      duplicate &&
      !window.confirm(
        `已經有一個內容相同的批次「${duplicate.name}」，仍要建立新的嗎？`,
      )
    ) {
      return;
    }

    const batch = createBatch(
      words,
      `批次 #${sourceBatches.length + 1}（${VOCAB_SOURCE_LABEL[source]}第 ${page} 頁）`,
    );
    updateBatch(batch.id, { sourcePage: page });
    setActiveBatch(batch.id);
    navigate(`/batch/${batch.id}`);
  };

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title={`${VOCAB_SOURCE_LABEL[source]}批次建立器`}
        onBack={() => navigate('/')}
        rightSlot={<UserBadge />}
      />

      {/* Filters */}
      <div className="border-b border-gray-100 bg-white px-4 py-3">
        <section className="mb-3 rounded-xl border border-primary/20 bg-primary/5 p-3">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-900">
              快速建立：選課本頁碼
            </h2>
            <span className="text-xs text-gray-500">{pageOptions.length} 頁</span>
          </div>
          <div className="grid grid-cols-4 gap-2 sm:grid-cols-6">
            {pageOptions.map(({ page, words }) => (
              <button
                key={page}
                type="button"
                onClick={() => handleCreatePageBatch(page, words)}
                aria-label={`建立第 ${page} 頁批次`}
                className="flex min-h-14 flex-col items-center justify-center rounded-lg border border-primary/20 bg-white px-2 py-2 text-primary shadow-sm transition-colors hover:border-primary hover:bg-primary/10"
              >
                <span className="text-base font-semibold leading-5">{page}</span>
                <span className="text-xs leading-4 text-gray-500">
                  {words.length} 字
                </span>
              </button>
            ))}
          </div>
        </section>

        <p className="mb-2 text-xs font-medium text-gray-500">
          進階篩選：手動選字
        </p>
        <div className="mb-2 flex gap-2 overflow-x-auto">
          {FREQ_OPTIONS.map((opt) => (
            <Chip
              key={opt.value}
              label={opt.label}
              active={freqFilter === opt.value}
              onClick={() => setFreqFilter(opt.value)}
            />
          ))}
        </div>
        <div className="mb-2 flex gap-2 overflow-x-auto">
          {POS_OPTIONS.map((opt) => (
            <Chip
              key={opt.value}
              label={opt.label}
              active={posFilter === opt.value}
              onClick={() => setPosFilter(opt.value)}
            />
          ))}
        </div>
        {/* Search */}
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[20px] text-gray-400">
            search
          </span>
          <input
            type="text"
            placeholder="搜尋英文單字…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-gray-200 bg-gray-50 py-2 pl-10 pr-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      {/* Selection counter (sticky) */}
      <div className="sticky top-[57px] z-20 border-b border-gray-100 bg-white/90 px-4 py-2 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <SelectionCounter count={selected.size} max={MAX_SELECTION} />
          <div className="flex gap-2">
            {selected.size > 0 && (
              <button
                onClick={() => setSelected(new Set())}
                className="rounded-full px-3 py-1 text-xs font-medium text-red-500 hover:bg-red-50"
              >
                清除
              </button>
            )}
            <button
              onClick={() => {
                setSelected((prev) => {
                  const next = new Set(prev);
                  for (const w of filtered) {
                    if (next.size >= MAX_SELECTION) break;
                    next.add(w.word);
                  }
                  return next;
                });
              }}
              disabled={isFull}
              className="rounded-full px-3 py-1 text-xs font-medium text-primary hover:bg-primary/10 disabled:opacity-40"
            >
              全選篩選結果
            </button>
          </div>
        </div>
        <p className="mt-0.5 text-xs text-gray-500">
          顯示 {filtered.length} 筆
        </p>
      </div>

      {/* Word list */}
      <main className="flex-1 pb-24">
        {filtered.map((entry) => (
          <WordCard
            key={entry.word}
            entry={entry}
            selected={selected.has(entry.word)}
            disabled={isFull}
            onToggle={() => toggleWord(entry.word)}
          />
        ))}
        {filtered.length === 0 && (
          <div className="flex flex-col items-center py-16 text-center">
            <span className="material-symbols-outlined mb-3 text-4xl text-gray-300">
              search_off
            </span>
            <p className="text-gray-600">沒有符合條件的單字</p>
          </div>
        )}
      </main>

      {/* Bottom create button */}
      <div className="fixed inset-x-0 bottom-0 border-t border-gray-200 bg-white p-4">
        <button
          onClick={handleCreate}
          disabled={selected.size === 0}
          className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          建立批次（{selected.size} 字）
        </button>
      </div>

      <Toast
        message="最多只能選 25 個單字"
        visible={toastVisible}
        onHide={() => setToastVisible(false)}
      />
    </div>
  );
}

function Chip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-colors ${
        active
          ? 'bg-primary text-white'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
    >
      {label}
    </button>
  );
}
