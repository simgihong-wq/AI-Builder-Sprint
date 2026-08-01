import { useEffect, useState } from "react";

const STAGES = ["대화 읽는 중", "약속 정리 중", "확인할 점 찾는 중"];
const STAGE_INTERVAL_MS = 1600;

export function LoadingScreen() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setStageIndex((prev) => Math.min(prev + 1, STAGES.length - 1));
    }, STAGE_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-5 bg-bg px-5">
      <div
        className="h-10 w-10 animate-spin rounded-full border-[3px] border-border"
        style={{ borderTopColor: "var(--color-primary)" }}
      />
      <p className="text-[15px] font-medium text-text-secondary">
        {STAGES[stageIndex]}
      </p>
    </div>
  );
}
