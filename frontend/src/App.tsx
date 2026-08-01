import { useState } from "react";
import { UploadScreen } from "./components/UploadScreen";
import { ResultSummaryScreen } from "./components/ResultSummaryScreen";
import { ChecklistScreen } from "./components/ChecklistScreen";
import { PromiseCardScreen } from "./components/PromiseCardScreen";
import type { AnalyzedData } from "./api/types";

type Step = "upload" | "summary" | "checklist" | "card";

const STEP_ORDER: Step[] = ["upload", "summary", "checklist", "card"];

function App() {
  const [step, setStep] = useState<Step>("upload");
  const [analyzedData, setAnalyzedData] = useState<AnalyzedData | null>(null);

  const hasChecklist = (analyzedData?.checklistItems.length ?? 0) > 0;

  const goBack = () => {
    if (step === "card" && !hasChecklist) {
      // 체크리스트가 비어 있어 요약에서 카드로 바로 건너뛴 경우, 뒤로가기도 요약으로
      setStep("summary");
      return;
    }
    const index = STEP_ORDER.indexOf(step);
    if (index > 0) setStep(STEP_ORDER[index - 1]);
  };

  const handleAnalyzed = (data: AnalyzedData) => {
    setAnalyzedData(data);
    setStep("summary");
  };

  if (step !== "upload" && !analyzedData) {
    // 분석 데이터 없이 이 단계에 올 수 없음(방어적 처리) — 업로드로 되돌림
    return <UploadScreen onAnalyzed={handleAnalyzed} />;
  }

  switch (step) {
    case "summary":
      return (
        <ResultSummaryScreen
          result={analyzedData!.result}
          checklistItems={analyzedData!.checklistItems}
          onBack={goBack}
          onNext={() => setStep(hasChecklist ? "checklist" : "card")}
        />
      );
    case "checklist":
      return (
        <ChecklistScreen
          items={analyzedData!.checklistItems}
          onBack={goBack}
          onNext={() => setStep("card")}
        />
      );
    case "card":
      return (
        <PromiseCardScreen result={analyzedData!.result} onBack={goBack} />
      );
    default:
      return <UploadScreen onAnalyzed={handleAnalyzed} />;
  }
}

export default App;
