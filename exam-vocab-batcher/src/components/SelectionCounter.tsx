interface SelectionCounterProps {
  count: number;
  max: number;
}

export default function SelectionCounter({ count, max }: SelectionCounterProps) {
  const isFull = count >= max;

  return (
    <div
      className={`flex items-center gap-2 text-sm font-medium ${
        isFull ? 'text-primary' : 'text-gray-600'
      }`}
    >
      {isFull && (
        <span className="material-symbols-outlined text-[18px] text-primary">
          info
        </span>
      )}
      <span>
        已選 {count} / {max}
      </span>
    </div>
  );
}
