import type { ChecklistItem, SolarJudgement } from "../types/promise";
import type { AnalyzedData } from "../api/types";

export const mockResult: SolarJudgement = {
  item: "애플 아이패드 에어 5세대 64GB",
  final_price: 370000,
  location: "개금역 1번 출구",
  datetime: "오늘 밤 10시 30분",
  delivery_method: "직거래",
  payment_method: "안심결제",
  accessories: [],
  refund_policy: "당일 확인 후 환불",
  condition_info: "배터리 92%",
  risk_signals: ["제가 급전이 필요해서"],
  conflicts: [],
  missing_items: ["결제 방식", "배터리 성능", "하자가 있을 때", "침수/수리 이력"],
  risk_notes: [
    "안심결제 질문에는 답하지 않고 직거래를 제안했어요. 서두르는 상대와의 거래는 확인할 시간을 갖는 게 좋아요.",
  ],
  confirm_questions: [
    "안심결제로 진행해도 괜찮을까요?",
    "배터리 성능 몇 %인지 알 수 있을까요?",
    "받고 나서 문제가 있으면 어떻게 할까요?",
  ],
};

export const mockChecklistItems: ChecklistItem[] = [
  {
    id: "payment",
    label: "결제 방식",
    question: "안심결제로 진행해도 괜찮을까요?",
    description:
      "안심결제 여부를 물었지만 답을 받지 못했어요. 직거래 현금은 문제가 생겨도 되돌리기 어려워요.",
    relatedMessages: [
      { speaker: "me", text: "안심결제도 가능하신거죠?" },
      {
        speaker: "other",
        text: "제가 오늘 그쪽으로 갈테니까 직거래 가능하시려나요.. 제가 급전이 필요해서",
        highlight: "제가 급전이 필요해서",
      },
      { speaker: "me", text: "아 네 가능합니다" },
    ],
  },
  {
    id: "battery",
    label: "배터리 성능",
    question: "배터리 성능 몇 %인지 알 수 있을까요?",
    description:
      "대화에 배터리 얘기가 없었어요. 80% 아래면 교체에 10만원대가 들어요.",
    relatedMessages: [],
  },
  {
    id: "defect",
    label: "하자가 있을 때",
    question: "받고 나서 문제가 있으면 어떻게 할까요?",
    description:
      "중고거래 분쟁에서 가장 많이 부딪히는 부분이에요. 미리 정해두면 서로 편해요.",
    relatedMessages: [],
  },
  {
    id: "water-damage",
    label: "침수/수리 이력",
    question: "혹시 침수되거나 메인보드 수리한 적 있나요?",
    description:
      "침수나 수리 이력은 육안으로 구분이 어려워요. 확인 안 하면 나중에 AS센터에서 유상수리 통보를 받을 수 있어요.",
    relatedMessages: [],
  },
];

export const mockAnalyzedData: AnalyzedData = {
  result: mockResult,
  checklistItems: mockChecklistItems,
};
