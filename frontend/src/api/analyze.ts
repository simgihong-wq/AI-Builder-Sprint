import { API_BASE_URL } from "./config";
import { ApiError, type AnalyzeApiData, type AnalyzedData } from "./types";

// 실측: Parse+Extract+Judge+Card 전체 파이프라인이 재시도 포함 시 90~200초대까지 걸릴 수 있음
const TIMEOUT_MS = 180_000;

interface Envelope {
  ok: boolean;
  data: AnalyzeApiData | null;
  error: string | null;
}

function toAnalyzedData(data: AnalyzeApiData): AnalyzedData {
  return { result: data.result, checklistItems: data.checklistItems };
}

async function postAnalyze(init: RequestInit): Promise<AnalyzedData> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/analyze`, {
      ...init,
      signal: controller.signal,
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new ApiError(
        "분석이 너무 오래 걸려요. 잠시 후 다시 시도해주세요.",
        "timeout",
      );
    }
    throw new ApiError(
      "서버에 연결하지 못했어요. 네트워크 상태를 확인해주세요.",
      "network",
    );
  } finally {
    clearTimeout(timeoutId);
  }

  let envelope: Envelope;
  try {
    envelope = await response.json();
  } catch {
    throw new ApiError(
      "서버 응답을 읽지 못했어요. 잠시 후 다시 시도해주세요.",
      "server",
    );
  }

  if (!envelope.ok || !envelope.data) {
    const kind = response.status >= 500 ? "server" : "validation";
    throw new ApiError(
      envelope.error ?? "분석 중 문제가 생겼어요. 잠시 후 다시 시도해주세요.",
      kind,
    );
  }

  return toAnalyzedData(envelope.data);
}

export function analyzeImages(files: File[]): Promise<AnalyzedData> {
  const formData = new FormData();
  files.forEach((file) => formData.append("images", file));
  return postAnalyze({ method: "POST", body: formData });
}

export function analyzeText(text: string): Promise<AnalyzedData> {
  return postAnalyze({
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: text }),
  });
}
