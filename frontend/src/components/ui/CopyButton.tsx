interface CopyButtonProps {
  text: string;
  onCopy?: () => void;
}

export function CopyButton({ text, onCopy }: CopyButtonProps) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // clipboard unavailable — silently ignore
    }
    onCopy?.();
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      className="inline-flex h-11 flex-1 items-center justify-center gap-1.5 rounded-xl bg-primary-soft text-[14.5px] font-bold tracking-[-0.02em] text-primary active:bg-primary-soft-active"
    >
      📋 복사하기
    </button>
  );
}
