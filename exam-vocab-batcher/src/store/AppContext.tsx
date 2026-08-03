import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import {
  VOCAB_SOURCE_FILE,
  type VocabEntry,
  type VocabSource,
} from '../types/vocab';
import type { Batch } from '../types/batch';

interface AppState {
  source: VocabSource;
  allWords: VocabEntry[];
  isLoading: boolean;
  loadError: boolean;
  batches: Batch[];
  activeBatchId: string | null;
}

interface AppContextValue extends AppState {
  setSource: (source: VocabSource) => void;
  createBatch: (words: VocabEntry[], name?: string) => Batch;
  deleteBatch: (id: string) => void;
  updateBatch: (id: string, patch: Partial<Batch>) => void;
  setActiveBatch: (id: string) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

function loadFromLS<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function loadSourceFromLS(): VocabSource {
  const source = loadFromLS<VocabSource>('vocabSource', 'cap');
  return source === 'gsat' ? 'gsat' : 'cap';
}

function normalizeBatch(batch: Batch): Batch {
  return {
    ...batch,
    source: batch.source ?? 'cap',
  };
}

function normalizeVocabEntry(entry: VocabEntry): VocabEntry {
  return {
    ...entry,
    source_page: entry.source_page.filter((page) => Number.isInteger(page) && page > 0),
  };
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [source, setSourceState] = useState<VocabSource>(loadSourceFromLS);
  const [allWords, setAllWords] = useState<VocabEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [batches, setBatches] = useState<Batch[]>(() =>
    loadFromLS<Batch[]>('batches', []).map(normalizeBatch),
  );
  const [activeBatchId, setActiveBatchIdState] = useState<string | null>(() =>
    loadFromLS<string | null>('activeBatchId', null),
  );

  // Load vocab data when source changes
  useEffect(() => {
    let cancelled = false;

    fetch(import.meta.env.BASE_URL + VOCAB_SOURCE_FILE[source])
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: VocabEntry[]) => {
        if (cancelled) return;
        setAllWords(data.map(normalizeVocabEntry));
        setIsLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load vocab data:', err);
        if (cancelled) return;
        setLoadError(true);
        setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [source]);

  const setSource = useCallback((nextSource: VocabSource) => {
    setIsLoading(true);
    setLoadError(false);
    setAllWords([]);
    setSourceState(nextSource);
    localStorage.setItem('vocabSource', JSON.stringify(nextSource));
    setActiveBatchIdState((currentId) => {
      if (!currentId) return currentId;
      const currentBatch = loadFromLS<Batch[]>('batches', [])
        .map(normalizeBatch)
        .find((batch) => batch.id === currentId);
      return currentBatch && currentBatch.source === nextSource ? currentId : null;
    });
  }, []);

  // Persist batches
  useEffect(() => {
    localStorage.setItem('batches', JSON.stringify(batches));
  }, [batches]);

  // Persist activeBatchId
  useEffect(() => {
    if (activeBatchId) {
      localStorage.setItem('activeBatchId', JSON.stringify(activeBatchId));
    } else {
      localStorage.removeItem('activeBatchId');
    }
  }, [activeBatchId]);

  const createBatch = useCallback(
    (words: VocabEntry[], name?: string): Batch => {
      const batch: Batch = {
        id: Date.now().toString(),
        name: name ?? `批次 #${batches.length + 1}`,
        source,
        createdAt: new Date().toISOString(),
        lastAccessedAt: new Date().toISOString(),
        words,
        flashcardIndex: 0,
      };
      setBatches((prev) => [batch, ...prev]);
      setActiveBatchIdState(batch.id);
      return batch;
    },
    [batches.length, source],
  );

  const deleteBatch = useCallback((id: string) => {
    setBatches((prev) => prev.filter((b) => b.id !== id));
    setActiveBatchIdState((prev) => (prev === id ? null : prev));
  }, []);

  const updateBatch = useCallback((id: string, patch: Partial<Batch>) => {
    setBatches((prev) =>
      prev.map((b) => (b.id === id ? { ...b, ...patch } : b)),
    );
  }, []);

  const setActiveBatch = useCallback((id: string) => {
    setActiveBatchIdState(id);
  }, []);

  return (
    <AppContext.Provider
      value={{
        source,
        allWords,
        isLoading,
        loadError,
        batches,
        activeBatchId,
        setSource,
        createBatch,
        deleteBatch,
        updateBatch,
        setActiveBatch,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
