import type { ReactNode } from "react";

export function BottomBar({ children }: { children: ReactNode }) {
  return (
    <div
      className="fixed bottom-0 left-1/2 w-full max-w-[420px] -translate-x-1/2 px-5 pb-[26px] pt-3"
      style={{
        background:
          "linear-gradient(180deg, rgba(242,244,246,0), var(--color-bg) 28%)",
      }}
    >
      {children}
    </div>
  );
}
