import { useState } from "react";
import { UploadScreen } from "./components/UploadScreen";
import { ResultSummaryScreen } from "./components/ResultSummaryScreen";
import { ChecklistScreen } from "./components/ChecklistScreen";
import { PromiseCardScreen } from "./components/PromiseCardScreen";
import { mockChecklistItems, mockResult } from "./data/mockResult";

type Step = "upload" | "summary" | "checklist" | "card";

const STEP_ORDER: Step[] = ["upload", "summary", "checklist", "card"];

function App() {
  const [step, setStep] = useState<Step>("upload");

  const goBack = () => {
    const index = STEP_ORDER.indexOf(step);
    if (index > 0) setStep(STEP_ORDER[index - 1]);
  };

  switch (step) {
    case "summary":
      return (
        <ResultSummaryScreen
          result={mockResult}
          checklistItems={mockChecklistItems}
          onBack={goBack}
          onNext={() => setStep("checklist")}
        />
      );
    case "checklist":
      return (
        <ChecklistScreen
          items={mockChecklistItems}
          onBack={goBack}
          onNext={() => setStep("card")}
        />
      );
    case "card":
      return <PromiseCardScreen result={mockResult} onBack={goBack} />;
    default:
      return <UploadScreen onNext={() => setStep("summary")} />;
  }
}

export default App;
