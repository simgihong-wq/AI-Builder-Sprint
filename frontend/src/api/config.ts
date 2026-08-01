// "localhost"가 아니라 "127.0.0.1"인 이유: 일부 Windows 환경에서 localhost가
// IPv6(::1)로 먼저 풀리는데 Flask는 IPv4(0.0.0.0)만 바인딩해서 fetch가
// 타임아웃남(TypeError: Failed to fetch) — 실측으로 확인됨.
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5000";

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
