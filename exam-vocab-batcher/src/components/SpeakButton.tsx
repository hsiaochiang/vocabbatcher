import type { MouseEvent } from 'react';
import { speakEn } from '../services/tts';

interface SpeakButtonProps {
  word: string;
  className?: string;
  label?: string;
}

export default function SpeakButton({
  word,
  className = '',
  label,
}: SpeakButtonProps) {
  if (typeof window === 'undefined' || !window.speechSynthesis) {
    return null;
  }

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    speakEn(word);
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`inline-flex min-h-[44px] min-w-[44px] items-center justify-center gap-2 rounded-full bg-primary/10 px-3 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary/20 focus:outline-none focus:ring-2 focus:ring-primary/40 ${className}`}
      aria-label={`播放 ${word} 的英文發音`}
      title={`播放 ${word} 的英文發音`}
    >
      <span className="material-symbols-outlined text-[22px]">volume_up</span>
      {label && <span>{label}</span>}
    </button>
  );
}
