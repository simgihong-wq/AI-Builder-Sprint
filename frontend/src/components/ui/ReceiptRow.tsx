import type { ReactNode } from "react";

interface ReceiptRowProps {
  label: string;
  value: ReactNode;
  divider?: boolean;
  mutedValue?: boolean;
}

export function ReceiptRow({
  label,
  value,
  divider = true,
  mutedValue = false,
}: ReceiptRowProps) {
  return (
    <div
      className={`flex items-start justify-between gap-4 py-[11px] ${
        divider ? "border-t border-border-soft" : ""
      }`}
    >
      <span className="flex-none text-sm text-text-tertiary">{label}</span>
      <span
        className={`text-right text-[15px] leading-[1.4] ${
          mutedValue
            ? "font-medium text-text-tertiary"
            : "font-semibold text-ink"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
