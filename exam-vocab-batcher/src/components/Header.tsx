import type { ReactNode } from 'react';

interface HeaderProps {
  title: string;
  onBack?: () => void;
  rightSlot?: ReactNode;
}

export default function Header({ title, onBack, rightSlot }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-gray-200 bg-white/80 px-4 py-3 backdrop-blur-sm">
      {onBack && (
        <button
          onClick={onBack}
          className="flex items-center text-gray-600 hover:text-primary"
          aria-label="返回"
        >
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
      )}
      <h1 className="flex-1 truncate text-lg font-semibold text-gray-900">
        {title}
      </h1>
      {rightSlot}
    </header>
  );
}
