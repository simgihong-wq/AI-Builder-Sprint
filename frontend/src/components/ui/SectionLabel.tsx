import type { ReactNode } from "react";

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <div className="mb-2.5 mt-6 text-[13px] font-semibold text-text-tertiary">
      {children}
    </div>
  );
}
