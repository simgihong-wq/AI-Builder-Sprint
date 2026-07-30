"""⓪ 개인정보 마스킹. 텍스트가 시스템에 들어오는 두 지점(parse.py, text_input.py)
에서만 호출해 "업로드 즉시 마스킹"을 구조적으로 보장한다.
"""

import re

PHONE_MOBILE_RE = re.compile(r"01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}")
PHONE_LANDLINE_RE = re.compile(r"0(?:2|[3-6][1-5]|70)[-.\s]?\d{3,4}[-.\s]?\d{4}")

BANK_NAMES = (
    "국민|신한|우리|하나|농협|기업|카카오뱅크|케이뱅크|토스뱅크|새마을|"
    "우체국|수협|신협|산업|씨티|SC제일|SC|부산|대구|경남|광주|전북|제주"
)
BANK_ACCOUNT_RE = re.compile(
    rf"(?P<bank>{BANK_NAMES})(?P<suffix>은행)?\s*[:\s]*(?P<digits>[\d-]{{9,}})"
)

# 계좌번호로 볼 만큼 자릿수가 많은(10자리 이상) 숫자열만 마스킹한다.
# 날짜 표기(2026-01-28, 2026/01/28 15:10 등)는 다 합쳐도 8자리라 이 임계값에
# 걸리지 않고, "370,000원" 같은 가격도 콤마 때문에 연속 숫자로 안 잡힌다.
LONG_DIGIT_RUN_RE = re.compile(r"\b\d{10,}\b")
DASH_NUMBER_RE = re.compile(r"\b\d{2,6}-\d{2,6}-\d{2,8}\b")

# 반드시 "숫자+동 숫자+호" 쌍이어야 매치 — "가야동"처럼 지명으로 쓰인 "동"
# 단독은 절대 건드리지 않는다 (거래 장소 판단에 쓰이는 핵심 정보).
ADDRESS_RE = re.compile(r"\d{1,4}\s*동\s*\d{1,4}\s*호")


def _digit_count(s):
    return sum(ch.isdigit() for ch in s)


def mask_text(text):
    """(마스킹된 텍스트, {"phone":n,"account":n,"address":n}) 반환."""
    counts = {"phone": 0, "account": 0, "address": 0}

    text, n = PHONE_MOBILE_RE.subn("[전화번호]", text)
    counts["phone"] += n
    text, n = PHONE_LANDLINE_RE.subn("[전화번호]", text)
    counts["phone"] += n

    text, n = BANK_ACCOUNT_RE.subn(
        lambda m: f"{m.group('bank')}{m.group('suffix') or ''} [계좌번호]", text
    )
    counts["account"] += n

    text, n = LONG_DIGIT_RUN_RE.subn("[계좌번호]", text)
    counts["account"] += n

    dash_hits = [0]

    def _dash_sub(m):
        if _digit_count(m.group(0)) >= 10:
            dash_hits[0] += 1
            return "[계좌번호]"
        return m.group(0)

    text = DASH_NUMBER_RE.sub(_dash_sub, text)
    counts["account"] += dash_hits[0]

    text, n = ADDRESS_RE.subn("[상세주소]", text)
    counts["address"] += n

    return text, counts


def mask_messages(messages):
    """messages(list[dict], 각 dict에 "text" 키)에 마스킹을 적용하고
    (새 리스트, 누적 카운트)를 반환한다."""
    total = {"phone": 0, "account": 0, "address": 0}
    masked = []
    for msg in messages:
        text, counts = mask_text(msg.get("text", ""))
        for key in total:
            total[key] += counts[key]
        masked.append({**msg, "text": text})
    return masked, total
