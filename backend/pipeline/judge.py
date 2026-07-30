"""⑤ Solar Pro 3 판단 — "판사" 역할. 실험②에서 확정된 5개 필수 지시 +
checklistItems 확장 지시를 시스템 프롬프트에 그대로 반영한다.
"""

import json
import re

from . import schemas, upstage_client

JUDGE_SYSTEM_PROMPT = "\n".join([
    "너는 중고거래 채팅 대화록을 검토해 빠진 약속과 분쟁 리스크를 찾는 판사 역할이다.",
    "아래 지시를 반드시 따르라:",
    "1. 값들이 서로 충돌하면 반드시 conflicts에 지적하라.",
    "2. 한쪽이 언급만 한 것과 양측이 실제로 합의한 것을 구분하라. 합의가 "
    "불분명하면 해당 필드는 null로 두고 missing_items에 넣어라.",
    "3. risk_signals의 각 항목에 대해 왜 위험한지와 어떻게 확인하면 좋을지를 "
    "risk_notes에 설명하라.",
    "4. confirm_questions는 사용자('나')의 채팅 말투를 그대로 유지해 작성하라.",
    "5. 가격 충돌은 리스크 신호로 승격해 risk_signals와 risk_notes 양쪽에 "
    "반영하라.",
    "6. [코드 검증 결과]의 detected_price_candidates에 서로 다른 금액이 2개 "
    "이상 있으면 반드시 conflicts에 그 내용을 명시하라.",
    "7. checklistItems[].relatedMessages[].text는 [대화록]에 있는 문장을 "
    "글자 그대로 복사하라. 새로 지어내지 마라. highlight는 그 text 안에 "
    "실제로 포함된 부분 문자열이어야 하며, 강조할 부분이 없으면 빈 문자열로 "
    "둔다. 근거가 되는 메시지가 없으면 relatedMessages는 빈 배열로 둔다.",
    "8. checklistItems는 3~5개로, question은 confirm_questions 중 대응되는 "
    "것과 맞추고, description은 '왜 중요한지 + 확인 안 하면 어떤 문제가 "
    "생기는지'를 2문장 이내 존댓말로 설명하라.",
    "9. item/final_price 등 [수집된 정보]의 10개 필드는 절대 다시 출력하지 "
    "마라 — 이미 확정된 값이며 그대로 최종 결과에 병합된다. 네가 낼 값은 "
    "conflicts/missing_items/risk_notes/confirm_questions/checklistItems "
    "다섯 개뿐이다. 값이 의심스러우면 다시 쓰지 말고 conflicts에 지적하라.",
    "10. 대화록에 [전화번호], [계좌번호], [상세주소] 같은 마스킹 토큰이 "
    "보이면 그 정보는 이미 대화에서 교환된 것으로 간주하라. 실제 값을 알 수 "
    "없다는 이유로 missing_items나 confirm_questions에 다시 물어보라고 넣지 "
    "마라. 단, 그 정보 자체가 risk_signals와 관련된 경우는 예외로 다뤄도 된다.",
])


def build_user_message(transcript, extract, validation, speaker_mode):
    parts = [
        "[대화록]", transcript, "",
        "[수집된 정보 (Extract)]", json.dumps(extract, ensure_ascii=False, indent=2), "",
        "[코드 검증 결과]", json.dumps(validation, ensure_ascii=False, indent=2),
    ]
    if speaker_mode == "unknown":
        parts += [
            "",
            "참고: 이 대화록은 화자 구분 정보가 없다. "
            "checklistItems의 relatedMessages는 항상 빈 배열로 둘 것.",
        ]
    return "\n".join(parts)


def _normalize_for_match(text):
    return re.sub(r"\s+", "", text or "")


def sanitize_checklist(items, messages):
    """ChatTranscript.tsx가 text.includes(highlight)+text.split(highlight)로
    정확 부분문자열 매칭을 하므로, 대화록에 없는 인용이나 부분문자열이 아닌
    highlight는 프론트에서 하이라이트가 조용히 사라지거나(첫 케이스) 뒷부분이
    잘린다(두 번째 케이스). 여기서 결정론적으로 걸러낸다."""
    normalized_real = [
        _normalize_for_match(m.get("text", "")) for m in messages
    ]
    normalized_real = [t for t in normalized_real if t]

    seen_ids = set()
    cleaned = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue

        related = []
        for rm in item.get("relatedMessages", []) or []:
            if not isinstance(rm, dict):
                continue
            speaker = rm.get("speaker")
            text = rm.get("text", "")
            if speaker not in ("me", "other") or not isinstance(text, str) or not text.strip():
                continue

            norm_text = _normalize_for_match(text)
            found = any(
                norm_text in real or real in norm_text for real in normalized_real
            )
            if not found:
                continue

            highlight = rm.get("highlight") or ""
            if highlight:
                if highlight not in text or text.count(highlight) != 1:
                    highlight = ""

            entry = {"speaker": speaker, "text": text}
            if highlight:
                entry["highlight"] = highlight
            related.append(entry)

        item_id = str(item.get("id") or "item").strip() or "item"
        base_id = item_id
        suffix = 2
        while item_id in seen_ids:
            item_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_ids.add(item_id)

        cleaned.append({
            "id": item_id,
            "label": item.get("label", ""),
            "question": item.get("question", ""),
            "description": item.get("description", ""),
            "relatedMessages": related,
        })

    return cleaned


_MISSING_FIELD_LABELS = {
    "location": "거래 장소", "datetime": "거래 시간", "delivery_method": "거래 방식",
    "payment_method": "결제 방식", "refund_policy": "환불 조건", "condition_info": "제품 상태",
}

_FALLBACK_CONFIRM_QUESTIONS = [
    "최종 가격과 거래 장소·시간을 다시 한번 확인해 주실 수 있을까요?",
    "결제 방식은 어떻게 진행하기로 하셨나요?",
    "받은 후 문제가 있으면 어떻게 하기로 하셨는지 확인해 주실 수 있을까요?",
]


def build_fallback_judgement(extract, validation):
    """Solar 호출이 실패했을 때 쓰는 보험. LLM 없이 extract/validate 결과만으로
    최소한의 판단을 만든다 — 데모 당일 Solar가 흔들려도 화면은 뜨게 한다."""
    conflicts = []
    if validation.get("price_conflict"):
        candidates = validation.get("detected_price_candidates", [])
        conflicts.append(f"가격 후보가 여러 개 발견됐어요: {candidates}. 최종 합의 금액을 다시 확인해주세요.")

    missing_items = [
        label for field, label in _MISSING_FIELD_LABELS.items() if not extract.get(field)
    ]
    missing_items += validation.get("missing_required", [])

    risk_notes = [
        f"'{signal}' 발언이 있었어요. 거래 전 다시 한번 확인해보는 게 좋아요."
        for signal in extract.get("risk_signals", [])
    ]

    return {
        **extract,
        "conflicts": conflicts,
        "missing_items": missing_items,
        "risk_notes": risk_notes,
        "confirm_questions": list(_FALLBACK_CONFIRM_QUESTIONS),
    }


def judge(transcript, extract, validation, messages, speaker_mode):
    chat_messages = [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": build_user_message(transcript, extract, validation, speaker_mode)},
    ]
    raw = upstage_client.chat_json(
        "solar-pro3", chat_messages,
        stage="judge", schema=schemas.JUDGE_SCHEMA,
        temperature=0.2, max_tokens=3000, timeout=120,
    )
    # extract의 10개 필드는 파이썬에서 그대로 병합한다 — Solar가 다시 쓰게
    # 하면 스키마상 item이 non-null 문자열이라 모를 때 엉뚱한 값을 지어내는
    # 것이 실측으로 확인됨(§JUDGE_SCHEMA 주석 참조).
    judgement = {**extract, **raw}
    judgement["checklistItems"] = sanitize_checklist(raw.get("checklistItems"), messages)
    return judgement
