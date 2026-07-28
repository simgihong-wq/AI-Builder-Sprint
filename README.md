# 🌸 약속지킴이 (Promise Companion) — 팀 디티의꽃

> AI Builder Sprint 2026 · 중고거래 채팅에서 빠진 약속과 분쟁 리스크를 찾아주는 분쟁 예방 서비스
> **"문서가 아니라 신뢰를 만드는 생활형 CLM"**

## 무엇을 하나요?
거래 채팅 캡처를 올리면 → AI가 확정된 조건을 정리하고 → 빠진 약속·위험 신호를 찾아
→ 보내기 좋은 확인 질문을 만들어주고 → 양측 확인 후 **약속 카드**를 발급합니다.

## 아키텍처
```
캡처(다중) → 마스킹 → Document Parse → 화자 분리 → Information Extract
→ 코드 검증 → Solar Pro 3 (충돌·리스크 판단, 질문 생성) → 약속 카드
```
- Upstage 3종 API(Parse·Extract·Solar)가 전부 핵심 경로 — 하나라도 빼면 서비스가 동작하지 않습니다.
- 에이전트·RAG·프레임워크 미사용: 단순함의 원칙에 따른 의도적 설계 결정입니다.
- 모든 설계는 사전 실험으로 검증됨 → [실험① 화자 분리](docs/실험1_화자분리_검증리포트.md) · [실험② A/B 테스트](docs/실험2_AB테스트_최종리포트.md)

## 팀
| 이름 | 역할 |
|---|---|
| 심지홍 | 디자인 · 프론트엔드 · 통합 책임 |
| 이상엽 | 백엔드 · AI 파이프라인 |
| 재윤 | 발표 · 품질 · 테스트 데이터 |

## 실행 방법
```bash
# backend
cd backend && pip install -r requirements.txt
cp .env.example .env  # UPSTAGE_API_KEY 입력
python app.py

# frontend
cd frontend && (안내 추가 예정)
```

---

## 🤖 AI 활용 로그
> 평가 기준 "AI를 통한 생산성 개선"의 근거 기록. 매일 각자 한 줄씩. (시간 절감 추정 포함)

### #0 사전 검증 (대회 전, 지홍)
- Upstage Playground + Claude 좌표 분석으로 화자 분리 규칙을 코딩 없이 실측 확정 (3플랫폼×2테마).
  대회 중 발견 시 최소 반나절 소요 예상 → 사전 제거.
- Studio 에이전트 + 콘솔 Chat으로 Extract vs Solar A/B 실험 완료 → 아키텍처 확정.
  부수 수확: 마스킹 필수 근거(계좌·동호수 실추출), 데모 샘플 3종, Solar 프롬프트 지시문.

### 지홍
- 7/28: 레포 세팅(AGENTS.md·Hooks)을 Claude와 30분에 완료 (수동 예상 2시간+)

### 상엽
- 7/28:

### 재윤
- 7/28:
