import { NavHeader } from "./ui/NavHeader";
import { Button } from "./ui/Button";
import { ReceiptRow } from "./ui/ReceiptRow";
import { BottomBar } from "./ui/BottomBar";
import type { SolarJudgement } from "../types/promise";

interface PromiseCardScreenProps {
  result: SolarJudgement;
  onBack: () => void;
}

function formatIssuedAt(date: Date) {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())} ${pad(
    date.getHours(),
  )}:${pad(date.getMinutes())}`;
}

export function PromiseCardScreen({ result, onBack }: PromiseCardScreenProps) {
  const issuedAt = formatIssuedAt(new Date());
  const hasAccessories = result.accessories.length > 0;

  return (
    <div className="min-h-screen bg-bg">
      <div className="mx-auto flex min-h-screen w-full max-w-[420px] flex-col">
        <NavHeader title="약속 카드" onBack={onBack} />

        <div className="flex-1 px-5 pb-[120px] pt-1">
          <h1 className="mb-2 text-2xl font-bold leading-[1.38] tracking-[-0.03em] text-ink">
            약속이
            <br />
            정리됐어요
          </h1>
          <p className="mb-6 text-[15px] leading-[1.5] text-text-secondary">
            거래 전에 서로 한 번씩 확인해보세요.
          </p>

          <div
            className="overflow-hidden rounded-[22px] bg-surface"
            style={{ boxShadow: "0 6px 24px rgba(25,31,40,.07)" }}
          >
            <div
              className="px-[22px] pb-5 pt-6 text-white"
              style={{
                background: "linear-gradient(135deg, #3182F6, #1B64DA)",
              }}
            >
              <div className="mb-3 text-xs font-bold tracking-[0.02em] opacity-85">
                PROMISE CARD
              </div>
              <div className="mb-1 text-xl font-bold leading-[1.35]">
                {result.item}
              </div>
              <div className="text-[26px] font-extrabold tracking-[-0.04em]">
                {result.final_price.toLocaleString()}원
              </div>
            </div>

            <div className="px-[22px] pb-5 pt-1.5">
              <ReceiptRow
                label="장소"
                value={result.location ?? "-"}
                divider={false}
              />
              <ReceiptRow label="시간" value={result.datetime ?? "-"} />
              <ReceiptRow
                label="거래 방식"
                value={result.delivery_method ?? "-"}
              />
              <ReceiptRow
                label="결제"
                value={result.payment_method ?? "미정"}
              />
              <ReceiptRow
                label="제품 상태"
                value={result.condition_info ?? "-"}
              />
              <ReceiptRow label="하자 시" value={result.refund_policy ?? "-"} />
              <ReceiptRow
                label="구성품"
                value={
                  hasAccessories ? result.accessories.join(", ") : "언급 없음"
                }
                mutedValue={!hasAccessories}
              />
            </div>

            <div className="mx-[22px] flex items-center justify-between border-t border-dashed border-border pb-[22px] pt-4">
              <span className="flex items-center gap-[5px] text-[12.5px] font-bold text-confirmed">
                ✓ 양쪽 확인 완료
              </span>
              <span className="text-xs text-text-tertiary">{issuedAt}</span>
            </div>
          </div>

          {!hasAccessories && (
            <div className="mt-3 rounded-[14px] bg-warning-bg px-4 py-3.5 text-[13px] font-medium leading-[1.55] text-warning-text-2">
              구성품은 아직 정해지지 않았어요. 만나기 전에 한 번 더
              확인해보세요.
            </div>
          )}
        </div>

        <BottomBar>
          <div className="flex gap-2">
            <div className="flex-1">
              <Button
                variant="outline"
                onClick={() => console.log("이미지로 저장")}
              >
                이미지로 저장
              </Button>
            </div>
            <div className="flex-1">
              <Button onClick={() => console.log("상대에게 보내기")}>
                상대에게 보내기
              </Button>
            </div>
          </div>
        </BottomBar>
      </div>
    </div>
  );
}
