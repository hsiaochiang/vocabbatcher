import { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../store/AppContext';
import Header from '../components/Header';
import WordCard from '../components/WordCard';
import SelectionCounter from '../components/SelectionCounter';
import Toast from '../components/Toast';

const MAX_SELECTION = 25;

type FreqFilter = 'all' | 'high' | 'mid' | 'low';
type PosFilter = 'all' | 'n.' | 'v.' | 'adj.' | 'adv.' | 'other';

const FREQ_OPTIONS: { value: FreqFilter; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'high', label: '高頻 ≥8' },
  { value: 'mid', label: '中頻 4-7' },
  { value: 'low', label: '低頻 ≤3' },
];

const POS_OPTIONS: { value: PosFilter; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'n.', label: 'n.' },
  { value: 'v.', label: 'v.' },
  { value: 'adj.', label: 'adj.' },
  { value: 'adv.', label: 'adv.' },
  { value: 'other', label: '其他' },
];

export default function BatchBuilderPage() {
  const { allWords, createBatch, setActiveBatch } = useApp();
  const navigate = useNavigate();

  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [freqFilter, setFreqFilter] = useState<FreqFilter>('all');
  const [posFilter, setPosFilter] = useState<PosFilter>('all');
  const [search, setSearch] = useState('');
  const [toastVisible, setToastVisible] = useState(false);

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
          const mainPos = ['n.', 'v.', 'adj.', 'adv.'];
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
    const batch = createBatch(words);
    setActiveBatch(batch.id);
    navigate(`/batch/${batch.id}`);
  };

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header title="批次建立器" onBack={() => navigate('/')} />

      {/* Filter chips */}
      <div className="border-b border-gray-100 bg-white px-4 py-3">
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
        <SelectionCounter count={selected.size} max={MAX_SELECTION} />
        <p className="mt-0.5 text-xs text-gray-400">
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
            <p className="text-gray-400">沒有符合條件的單字</p>
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
