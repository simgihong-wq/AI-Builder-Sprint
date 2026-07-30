"""② 후처리·화자 분리. 실험①(화자분리 검증 리포트) §4의 7단계를 그대로
구현한다. TIMESTAMP_RE와 build_transcript는 text_input.py(백업 경로)도
함께 쓴다.
"""

import re

TIMESTAMP_RE = re.compile(r"(오전|오후)\s?\d{1,2}:\d{2}")

# 광폭 블록(x스팬>0.8)이 아니어도 이 문구가 보이면 시스템 메시지로 분류.
# 실험①에서 실측된 플랫폼 고정 문구.
SYSTEM_PHRASES = (
    "안심결제로 안전하게", "거래 예약을 했어요", "안전결제", "정산 예정 금액", "거래방법",
)


def _coords_bounds(coords):
    xs = [p["x"] for p in coords]
    ys = [p["y"] for p in coords]
    return min(xs), max(xs), min(ys), max(ys)


def _is_noise(text):
    """한글·숫자 없는 2글자 이하 블록(아이콘 등)."""
    if len(text) > 2:
        return False
    return re.search(r"[가-힣0-9]", text) is None


def elements_to_messages(elements, capture_index):
    """실험①의 x_max>=0.88/x_min<=0.20 화자 배정 규칙을 그대로 적용한다.
    elements는 parse.py가 반환한 {category, page, text(마스킹 완료), coords}
    형태의 얇은 dict 리스트."""
    enriched = []
    for el in elements:
        coords = el.get("coords") or []
        if not coords:
            continue
        x_min, x_max, y_min, y_max = _coords_bounds(coords)
        enriched.append({
            "category": el.get("category"),
            "text": el.get("text", ""),
            "page": el.get("page", 0),
            "y_center": (y_min + y_max) / 2,
            "x_min": x_min,
            "x_max": x_max,
        })

    # ① y좌표 기준 재정렬 — JSON 순서 ≠ 화면 순서인 사례가 실측으로 확인됨
    enriched.sort(key=lambda e: (e["page"], e["y_center"]))

    messages = []
    for e in enriched:
        if e["category"] == "figure":
            # ⑦ figure는 화자 없이 이벤트로만 기록
            messages.append({
                "speaker": None, "text": "사진 공유됨", "kind": "photo",
                "capture": capture_index, "y": e["y_center"],
                "x_min": e["x_min"], "x_max": e["x_max"],
            })
            continue

        # ② 타임스탬프 제거
        text = TIMESTAMP_RE.sub("", e["text"]).strip()
        if not text:
            continue
        # ③ 노이즈 블록 제거
        if _is_noise(text):
            continue
        # ④ 상/하단 UI 제거
        if e["y_center"] < 0.12 or e["y_center"] > 0.88:
            continue

        x_span = e["x_max"] - e["x_min"]
        if x_span > 0.8 or any(phrase in text for phrase in SYSTEM_PHRASES):
            # ⑤ 시스템 메시지 분류 (버리지 않음 — 최고 신뢰도 확정 정보)
            messages.append({
                "speaker": "system", "text": text, "kind": "system",
                "capture": capture_index, "y": e["y_center"],
                "x_min": e["x_min"], "x_max": e["x_max"],
            })
            continue

        # ⑥ 화자 배정
        if e["x_max"] >= 0.88:
            speaker = "me"
        elif e["x_min"] <= 0.20:
            speaker = "other"
        else:
            speaker = "other"  # TODO: Solar 맥락 판별 폴백 (실험①에서 해당 케이스 0건)

        messages.append({
            "speaker": speaker, "text": text, "kind": "message",
            "capture": capture_index, "y": e["y_center"],
            "x_min": e["x_min"], "x_max": e["x_max"],
        })

    return messages


def build_transcript(messages):
    """Extract/Solar에 넣을 하나의 대화록 문자열로 조립.

    [캡처 1]
    나: ...
    상대방: ...
    [시스템 정보] ...
    [이벤트] 사진 공유됨

    [캡처 2]
    ...
    """
    if not messages:
        return ""

    lines = []
    current_capture = None
    for msg in messages:
        capture = msg.get("capture", 0)
        if capture != current_capture:
            if current_capture is not None:
                lines.append("")
            lines.append(f"[캡처 {capture + 1}]")
            current_capture = capture

        kind = msg.get("kind", "message")
        speaker = msg.get("speaker")
        text = msg.get("text", "")

        if kind == "system":
            lines.append(f"[시스템 정보] {text}")
        elif kind == "photo":
            lines.append("[이벤트] 사진 공유됨")
        elif speaker == "me":
            lines.append(f"나: {text}")
        elif speaker == "other":
            lines.append(f"상대방: {text}")
        else:
            lines.append(text)

    return "\n".join(lines)
