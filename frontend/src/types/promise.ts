export interface ExtractResult {
  item: string;
  final_price: number;
  location: string | null;
  datetime: string | null;
  delivery_method: string | null;
  payment_method: string | null;
  accessories: string[];
  refund_policy: string | null;
  condition_info: string | null;
  risk_signals: string[];
}

export interface SolarJudgement extends ExtractResult {
  conflicts: string[];
  missing_items: string[];
  risk_notes: string[];
  confirm_questions: string[];
}

export interface ChatMessage {
  speaker: "me" | "other";
  text: string;
  /** 부분 문자열만 강조(원문 <mark> 재현). text 안에 포함된 부분 문자열이어야 함 */
  highlight?: string;
}

export type SafetyLevel = "safe" | "caution" | "danger";

export interface ChecklistItem {
  id: string;
  label: string;
  question: string;
  description: string;
  relatedMessages: ChatMessage[];
}
