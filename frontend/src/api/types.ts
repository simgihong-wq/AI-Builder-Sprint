import type {
  ChatMessage,
  ChecklistItem,
  SolarJudgement,
} from "../types/promise";

export interface PromiseCard {
  card_title: string;
  card_summary: string;
  one_line_warning: string;
}

export interface AnalyzeMeta {
  source: "text" | "images";
  captures: number;
  speaker_mode: string;
  masked_counts: Record<string, number>;
  detected_price_candidates: number[];
  missing_required: string[];
  degraded: boolean;
  timings_ms: Record<string, number>;
}

export interface AnalyzeApiData {
  result: SolarJudgement;
  checklistItems: ChecklistItem[];
  messages: ChatMessage[];
  card: PromiseCard | null;
  meta: AnalyzeMeta;
}

/** 화면 레이어에서 실제로 쓰는 축약 타입 (mock/real 공통) */
export interface AnalyzedData {
  result: SolarJudgement;
  checklistItems: ChecklistItem[];
}

export type ApiErrorKind = "validation" | "server" | "network" | "timeout";

export class ApiError extends Error {
  kind: ApiErrorKind;

  constructor(message: string, kind: ApiErrorKind) {
    super(message);
    this.kind = kind;
  }
}
