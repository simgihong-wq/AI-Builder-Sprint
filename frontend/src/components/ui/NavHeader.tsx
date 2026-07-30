interface NavHeaderProps {
  title: string;
  onBack?: () => void;
}

export function NavHeader({ title, onBack }: NavHeaderProps) {
  return (
    <div className="flex h-[52px] flex-none items-center gap-2 px-3">
      {onBack && (
        <button
          type="button"
          onClick={onBack}
          aria-label="뒤로가기"
          className="grid h-9 w-9 flex-none place-items-center rounded-[10px] text-[15px] hover:bg-border"
        >
          ←
        </button>
      )}
      <span className="text-[15px] font-semibold">{title}</span>
    </div>
  );
}
