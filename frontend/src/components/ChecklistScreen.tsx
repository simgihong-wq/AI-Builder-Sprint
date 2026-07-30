import { useState } from "react";
import { Button } from "./ui/Button";
import { CopyButton } from "./ui/CopyButton";
import { ProgressBar } from "./ui/ProgressBar";
import { NavHeader } from "./ui/NavHeader";
import { BottomBar } from "./ui/BottomBar";
import { ChatTranscript } from "./ChatTranscript";
import type { ChecklistItem } from "../types/promise";

interface ChecklistScreenProps {
  items: ChecklistItem[];
  onBack: () => void;
  onNext: () => void;
}

export function ChecklistScreen({
  items,
  onBack,
  onNext,
}: ChecklistScreenProps) {
  const [checked, setChecked] = useState<Set<string>>(new Set());
  const [toast, setToast] = useState(false);

  const toggleChecked = (id: string) => {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const showToast = () => {
    setToast(true);
    setTimeout(() => setToast(false), 1400);
  };

  return (
    <div className="min-h-screen bg-bg">
      <div className="mx-auto flex min-h-screen w-full max-w-[420px] flex-col">
        <NavHeader title="확인 체크리스트" onBack={onBack} />

        <div className="flex-1 px-5 pb-[120px] pt-1">
          <h1 className="mb-2 text-2xl font-bold leading-[1.38] tracking-[-0.03em] text-ink">
            이 {items.length}가지만
            <br />
            물어보면 돼요
          </h1>
          <p className="mb-6 text-[15px] leading-[1.5] text-text-secondary">
            복사해서 그대로 보내세요.
          </p>

          <div className="mb-[22px] mt-1">
            <ProgressBar value={checked.size} max={items.length} />
            <div className="mt-[9px] text-[13px] font-medium text-text-tertiary">
              {checked.size}/{items.length} 확인했어요
            </div>
          </div>

          {items.map((item, index) => {
            const isChecked = checked.has(item.id);
            return (
              <div
                key={item.id}
                className={`rounded-[18px] bg-surface px-5 py-[22px] transition-opacity ${
                  index > 0 ? "mt-3" : ""
                } ${isChecked ? "opacity-50" : "opacity-100"}`}
              >
                <div className="mb-[9px] text-xs font-bold text-primary">
                  {item.label}
                </div>
                <div className="mb-[9px] text-[19px] font-bold leading-[1.45] tracking-[-0.03em] text-ink">
                  "{item.question}"
                </div>
                <div className="mb-4 text-[13.5px] leading-[1.55] text-text-tertiary">
                  {item.description}
                </div>

                <div className="flex items-center gap-2">
                  <CopyButton text={item.question} onCopy={showToast} />
                  <button
                    type="button"
                    onClick={() => toggleChecked(item.id)}
                    className={`flex h-11 items-center gap-[7px] rounded-xl border pl-[11px] pr-3.5 text-sm font-semibold tracking-[-0.02em] transition-colors ${
                      isChecked
                        ? "border-confirmed bg-confirmed-bg text-confirmed-text"
                        : "border-[#D1D6DB] bg-surface text-text-secondary"
                    }`}
                  >
                    <span
                      className={`grid h-[19px] w-[19px] flex-none place-items-center rounded-full border-[1.5px] text-[11px] font-extrabold text-white ${
                        isChecked
                          ? "border-confirmed bg-confirmed"
                          : "border-[#C6CDD4] bg-surface"
                      }`}
                    >
                      {isChecked ? "✓" : ""}
                    </span>
                    {isChecked ? "확인했어요" : "확인하기"}
                  </button>
                </div>

                {item.relatedMessages.length > 0 && (
                  <details className="mt-3.5 border-t border-border-soft pt-3.5">
                    <summary className="flex list-none items-center gap-1 text-[13px] font-semibold text-text-tertiary [&::-webkit-details-marker]:hidden">
                      왜 이걸 물어봐야 하나요? ›
                    </summary>
                    <div className="mt-3">
                      <ChatTranscript messages={item.relatedMessages} />
                    </div>
                  </details>
                )}
              </div>
            );
          })}
        </div>

        <BottomBar>
          <Button onClick={onNext}>약속 카드 만들기</Button>
        </BottomBar>

        {toast && (
          <div className="pointer-events-none fixed bottom-[96px] left-1/2 flex w-full max-w-[420px] -translate-x-1/2 justify-center">
            <div className="rounded-xl bg-[rgba(25,31,40,.92)] px-[18px] py-3 text-sm font-semibold text-white">
              복사했어요
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
