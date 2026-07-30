"""③ 정보 수집 — "수집" 담당. 값의 정합성 판단은 하지 않는다
(④ 코드검증, ⑤ Solar가 담당 — 실험②).

원래 설계는 Upstage Information Extraction API(/v1/information-extraction)를
쓰는 것이었으나, 실제로 호출해보니 이 엔드포인트는 image_url 입력만 받고
텍스트 content를 지원하지 않는다(세 가지 content 형태 모두 400 에러로 확인).
마스킹은 텍스트 단계에서만 가능하므로 마스킹 안 된 원본 이미지를 Extract에
따로 보내는 대신, 이미 검증된 실험②의 B안(Solar Pro 3 프롬프팅으로 스키마
추출)을 그대로 사용해 마스킹된 텍스트 위에서 수집한다. 수집(③)과 판단(⑤)은
여전히 프롬프트·호출이 분리된 별도 단계로 유지한다.
"""

import re

from . import schemas, upstage_client

_MAN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*만")
_DIGITS_RE = re.compile(r"\d+")

# Solar가 스키마상 non-null 문자열이 필요할 때(예: item) 값을 모르면 JSON null
# 대신 문자열 "null"을 그대로 넣는 경우가 실측으로 확인됨 — 화면에 "null"이
# 그대로 노출되는 걸 막기 위해 빈 값으로 취급한다.
_NULL_LIKE = {"null", "none", "n/a", "na", "unknown", "미상", "없음"}


def _clean_str(value):
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text or text.lower() in _NULL_LIKE:
        return None
    return text

EXTRACT_SYSTEM_PROMPT = (
    "너는 중고거래 채팅 대화록에서 값을 있는 그대로 수집하는 역할이다. "
    "충돌 여부나 합의 여부에 대한 판단은 하지 마라 — 그건 다른 단계에서 한다. "
    "대화에 명시적으로 없는 값은 지어내지 말고 null 또는 빈 배열로 남겨라."
)


def extract_fields(transcript):
    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
        {"role": "user", "content": transcript},
    ]
    raw = upstage_client.chat_json(
        "solar-pro3", messages,
        stage="extract", schema=schemas.EXTRACT_SCHEMA,
        temperature=0.1, max_tokens=1200, timeout=60,
    )
    return _normalize(raw)


def _normalize_price(value):
    """LLM 출력이 흔들려도(문자열, "5.5만" 등) 정수 원 단위로 강제."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        s = value.replace(",", "").strip()
        m = _MAN_RE.search(s)
        if m:
            return int(float(m.group(1)) * 10000)
        m = _DIGITS_RE.search(s)
        if m:
            return int(m.group(0))
    return 0


def _normalize(raw):
    raw = raw if isinstance(raw, dict) else {}
    result = {"item": _clean_str(raw.get("item")) or ""}
    result["final_price"] = _normalize_price(raw.get("final_price"))

    for key in ("location", "datetime", "delivery_method", "payment_method",
                "refund_policy", "condition_info"):
        result[key] = _clean_str(raw.get(key))

    for key in ("accessories", "risk_signals"):
        value = raw.get(key)
        if isinstance(value, list):
            result[key] = [str(v) for v in value if str(v).strip()]
        elif isinstance(value, str) and value.strip():
            result[key] = [value.strip()]
        else:
            result[key] = []

    return result
