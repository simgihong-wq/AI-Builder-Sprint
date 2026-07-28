# AGENTS.md — 디티의꽃 팀 공통 규칙 (단일 진실 소스)

## 프로젝트: 약속지킴이 (Promise Companion)
중고거래 채팅 캡처를 분석해 확정된 약속을 정리하고, 빠진 조건·분쟁 리스크를 찾아
확인 질문을 생성한 뒤 약속 카드(Promise Card)를 만드는 분쟁 예방 서비스.
핵심 메시지: "문서가 아니라 신뢰를 만드는 생활형 CLM"

## Git 규칙 (중요)
- PR, 이슈, 커밋은 반드시 포크한 레포(simgihong-wq/AI-Builder-Sprint)에만 생성한다.
- 원본 레포(ApptiveDev/AI-Builder-Sprint)로 PR을 보내지 않는다. upstream으로 push 금지.
- push 전 git remote -v로 origin이 포크 레포인지 확인한다.
- 커밋은 기능 단위로 작게, 메시지는 `feat|fix|docs|chore(scope): 제목` 형식, 100자 이내.
- 작업 시작 시 git pull 먼저.

## 폴더 소유권 (충돌 방지)
- `frontend/` — 지홍 전담. 다른 사람(및 다른 사람의 AI)은 수정 금지, 읽기만.
- `backend/` — 상엽 전담. 동일.
- `docs/`, `test-data/` — 재윤 전담. 동일.
- 공용 파일(README.md, AGENTS.md)은 수정 전 팀 채팅에 알린다.
- README의 AI 활용 로그는 각자 자기 이름 섹션에만 추가한다.

## 아키텍처 (변경 금지 — 사전 실험으로 확정됨, docs/실험 리포트 참조)
```
캡처(다중) → ⓪ 마스킹(전화·계좌·주소 정규식)
           → ① Document Parse (텍스트+좌표)
           → ② 후처리·화자 분리 (아래 규칙)
           → ③ Information Extract (10필드 수집)
           → ④ 코드 검증 (필수 필드 누락·값 충돌 감지)
           → ⑤ Solar Pro 3 (충돌·합의 판단, 리스크 해석, 확인 질문 생성)
           → ⑥ 약속 카드 (문구 다듬기: solar-mini)
```
- 에이전트/멀티에이전트/RAG/LangChain 등 프레임워크 사용 금지 (단순함의 원칙).
- 바닐라 Python + API 호출로 구현한다.

## 화자 분리 규칙 (실험①로 실측 확정 — 임의 변경 금지)
- Document Parse 엔드포인트: https://api.upstage.ai/v1/document-digitization (model: document-parse)
- 후처리 순서: y좌표 재정렬 → 타임스탬프 제거(정규식 `(오전|오후)\s?\d{1,2}:\d{2}`)
  → 한글·숫자 없는 2글자 이하 블록 제거 → y<0.12(헤더)·y>0.88(입력창) 제거
  → 광폭 블록(x스팬>0.8) 또는 시스템 문구는 "시스템 정보"로 분류(버리지 않음, 최고 신뢰 확정 정보)
  → figure는 화자 없이 "사진 공유됨" 이벤트로 기록
- 화자 배정: x_max ≥ 0.88 → "나" / x_min ≤ 0.20 → "상대방" / 그 외 → Solar 맥락 판별 폴백
- 지원 플랫폼: 당근·번개장터·문자(iMessage). 파싱 실패 시 텍스트 붙여넣기 백업 경로.

## 데이터 스키마 (합의 없이 변경 금지)
Extract 10필드:
```json
{
  "item": "string",
  "final_price": "number — 최종 합의가. 거절된 제안 아님. 5.5→55000 환산",
  "location": "string|null — 양측 합의된 경우만",
  "datetime": "string|null",
  "delivery_method": "string|null — 직거래/택배/반택",
  "payment_method": "string|null — 합의된 경우만, 문의만은 null",
  "accessories": ["string"],
  "refund_policy": "string|null",
  "condition_info": "string|null",
  "risk_signals": ["string — 위험 발언 원문"]
}
```
Solar 판단 출력(⑤단계): 위 필드 + `conflicts`(값 충돌 목록), `missing_items`, `risk_notes`(위험 이유 설명), `confirm_questions`(사용자 말투 반영).

## Solar 프롬프트 필수 지시 (실험②로 확정)
- "값들이 서로 충돌하면 반드시 지적하라" (예: 게시가 31만 vs 카드 15만)
- "한쪽이 언급만 한 것과 양측이 합의한 것을 구분하라"
- "리스크 발언(Extract가 수집)에 대해 왜 위험한지와 확인 방법을 설명하라"
- "확인 질문은 사용자의 채팅 말투를 유지해 작성하라"
- 가격 충돌은 리스크 신호로 승격해 표시한다.

## API·보안 규칙
- API 키는 .env에만. 코드에 하드코딩 금지, 커밋 절대 금지.
- .env, *.key, 실개인정보 포함 캡처는 .gitignore 대상.
- test-data/의 캡처는 가짜 정보(이름·계좌·동호수)로 재제작된 것만 커밋한다.
- Upstage 크레딧: Usage 탭 잔액을 매일 확인 (담당: 재윤).

## 코드 컨벤션
- Python: 함수·변수 snake_case, 파이프라인 각 단계는 별도 모듈(backend/pipeline/*.py).
- API 응답 형식 통일: `{ "ok": bool, "data": ..., "error": str|null }`
- 에러 시 사용자 안내 메시지 포함 (예: 파싱 실패 → "텍스트 붙여넣기로 시도해주세요")

## 작업 방식
- 새 기능은 plan 모드로 설계 검토 후 구현 (막코딩 금지).
- 구현 시 테스트 먼저 작성하고 통과까지 확인.
- 데모 경로(캡처→약속 카드)를 깨뜨릴 수 있는 변경은 test-data/ 샘플 3종으로 검증 후 커밋.
- 8/2(일)부터 기능 동결 — 신규 기능 금지, 수정·안정화만.
