"""⑥ 약속 카드 문구 다듬기 (스트레치). 실패해도 전체 응답을 막지 않는다 —
호출부(orchestrator._try_polish_card)가 모든 예외를 삼킨다."""

import json

from . import schemas, upstage_client

CARD_SYSTEM_PROMPT = (
    "너는 중고거래 약속 카드에 들어갈 문구를 다듬는 역할이다. "
    "판단 단계에서 나온 결과를 바탕으로 짧고 친근한 존댓말로 요약하라. "
    "새로운 사실을 지어내지 말고 주어진 정보만 사용하라."
)


def polish_card(judgement):
    messages = [
        {"role": "system", "content": CARD_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(judgement, ensure_ascii=False)},
    ]
    return upstage_client.chat_json(
        "solar-mini", messages,
        stage="card", schema=schemas.CARD_SCHEMA,
        temperature=0.3, max_tokens=400, timeout=30,
    )
