import { Card } from "./ui/Card";
import { Button } from "./ui/Button";
import { NavHeader } from "./ui/NavHeader";
import { SectionLabel } from "./ui/SectionLabel";
import { ReceiptRow } from "./ui/ReceiptRow";
import { BottomBar } from "./ui/BottomBar";
import type { ChecklistItem, SolarJudgement } from "../types/promise";

interface ResultSummaryScreenProps {
  result: SolarJudgement;
  checklistItems: ChecklistItem[];
  onBack: () => void;
  onNext: () => void;
}

export function ResultSummaryScreen({
  result,
  checklistItems,
  onBack,
  onNext,
}: ResultSummaryScreenProps) {
  return (
    <div className="min-h-screen bg-bg">
      <div className="mx-auto flex min-h-screen w-full max-w-[420px] flex-col">
        <NavHeader title="거래 분석 결과" onBack={onBack} />

        <div className="flex-1 px-5 pb-[120px] pt-1">
          <h1 className="mb-2 text-2xl font-bold leading-[1.38] tracking-[-0.03em] text-ink">
            {checklistItems.length > 0 ? (
              <>
                확인이 필요한
                <br />
                {checklistItems.length}가지가 있어요
              </>
            ) : (
              <>
                확인할 내용이
                <br />
                따로 없어요
              </>
            )}
          </h1>
          <p className="mb-6 text-[15px] leading-[1.5] text-text-secondary">
            대화 12개를 읽고 정리했어요.
          </p>

          <Card className="flex items-center gap-3.5">
            <div className="grid h-[46px] w-[46px] flex-none place-items-center rounded-full bg-warning-bg text-[22px]">
              ⚠️
            </div>
            <div>
              <div className="mb-0.5 text-[17px] font-bold text-ink">
                주의가 필요한 거래예요
              </div>
              <div className="text-[13px] text-text-tertiary">
                위험 신호 {result.risk_signals.length}개 · 미확인{" "}
                {checklistItems.length}개
              </div>
            </div>
          </Card>

          <SectionLabel>정해진 약속</SectionLabel>
          <Card>
            <ReceiptRow label="물건" value={result.item} divider={false} />
            <ReceiptRow
              label="가격"
              value={`${result.final_price.toLocaleString()}원`}
            />
            <ReceiptRow label="장소" value={result.location ?? "-"} />
            <ReceiptRow label="시간" value={result.datetime ?? "-"} />
            <ReceiptRow
              label="거래 방식"
              value={result.delivery_method ?? "-"}
            />
          </Card>

          {result.risk_signals.length > 0 && (
            <>
              <SectionLabel>주의해서 볼 부분</SectionLabel>
              <div
                className="bg-danger-bg px-5 py-[18px]"
                style={{ borderRadius: 18 }}
              >
                <div className="mb-[7px] flex items-center gap-[7px] text-sm font-bold text-danger">
                  🚨 거래를 서두르고 있어요
                </div>
                <div className="mb-1.5 text-[15px] font-semibold leading-[1.5] text-ink">
                  "{result.risk_signals[0]}"
                </div>
                <div className="text-[13px] leading-[1.55] text-text-secondary">
                  {result.risk_notes[0]}
                </div>
              </div>
            </>
          )}
        </div>

        <BottomBar>
          <Button onClick={onNext}>
            {checklistItems.length > 0
              ? `확인할 ${checklistItems.length}가지 보기`
              : "약속 카드 보기"}
          </Button>
        </BottomBar>
      </div>
    </div>
  );
}
