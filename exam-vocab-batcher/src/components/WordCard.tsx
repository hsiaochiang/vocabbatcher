import { memo, type KeyboardEvent } from 'react';
import type { VocabEntry } from '../types/vocab';
import SpeakButton from './SpeakButton';

interface WordCardProps {
  entry: VocabEntry;
  selected: boolean;
  disabled: boolean;
  onToggle: () => void;
}

export default memo(function WordCard({
  entry,
  selected,
  disabled,
  onToggle,
}: WordCardProps) {
  const canToggle = !disabled || selected;

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (!canToggle) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onToggle();
    }
  };

  return (
    <div
      role="button"
      tabIndex={canToggle ? 0 : -1}
      aria-pressed={selected}
      aria-disabled={!canToggle}
      onClick={() => {
        if (canToggle) onToggle();
      }}
      onKeyDown={handleKeyDown}
      className={`flex w-full items-start gap-3 border-b border-gray-100 px-4 py-3 text-left transition-colors ${
        canToggle
          ? 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/30'
          : ''
      } ${
        selected
          ? 'bg-primary/5'
          : disabled
            ? 'cursor-not-allowed opacity-40'
            : 'hover:bg-gray-50'
      }`}
    >
      {/* Checkbox */}
      <span
        className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border ${
          selected
            ? 'border-primary bg-primary text-white'
            : 'border-gray-300'
        }`}
      >
        {selected && (
          <span className="material-symbols-outlined text-[16px]">check</span>
        )}
      </span>

      {/* Word info */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-baseline gap-2">
              <span className="break-words text-base font-semibold text-gray-900">
                {entry.word}
              </span>
              {entry.pos && (
                <span className="shrink-0 text-xs text-gray-500">
                  [{entry.pos}]
                </span>
              )}
            </div>
          </div>
          <SpeakButton word={entry.word} className="shrink-0" />
        </div>
        {entry.zh_definition && (
          <p className="mt-0.5 text-sm text-gray-500">{entry.zh_definition}</p>
        )}
        {entry.frequency != null && (
          <p className="mt-0.5 text-xs text-gray-500">頻率 {entry.frequency} 次</p>
        )}
      </div>
    </div>
  );
});
