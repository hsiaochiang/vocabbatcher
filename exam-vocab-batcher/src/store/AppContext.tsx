import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import type { VocabEntry } from '../types/vocab';
import type { Batch } from '../types/batch';

interface AppState {
  allWords: VocabEntry[];
  isLoading: boolean;
  batches: Batch[];
  activeBatchId: string | null;
}

interface AppContextValue extends AppState {
  createBatch: (words: VocabEntry[]) => Batch;
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

export function AppProvider({ children }: { children: ReactNode }) {
  const [allWords, setAllWords] = useState<VocabEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [batches, setBatches] = useState<Batch[]>(() =>
    loadFromLS<Batch[]>('batches', []),
  );
  const [activeBatchId, setActiveBatchIdState] = useState<string | null>(() =>
    loadFromLS<string | null>('activeBatchId', null),
  );

  // Load vocab data on mount
  useEffect(() => {
    fetch(import.meta.env.BASE_URL + 'data/vocab.cleaned.json')
      .then((r) => r.json())
      .then((data: VocabEntry[]) => {
        setAllWords(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load vocab data:', err);
        setIsLoading(false);
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
    (words: VocabEntry[]): Batch => {
      const batch: Batch = {
        id: Date.now().toString(),
        name: `批次 #${batches.length + 1}`,
        createdAt: new Date().toISOString(),
        lastAccessedAt: new Date().toISOString(),
        words,
        flashcardIndex: 0,
      };
      setBatches((prev) => [batch, ...prev]);
      setActiveBatchIdState(batch.id);
      return batch;
    },
    [batches.length],
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
        allWords,
        isLoading,
        batches,
        activeBatchId,
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
