"""텍스트 붙여넣기 백업 경로 (①Parse/②좌표기반 후처리를 건너뛴다).

프론트 UploadScreen.tsx의 텍스트 탭 placeholder에는 화자 접두어 안내가 없어,
사용자가 "나:"/"상대방:" 없이 카톡 내보내기 원문을 그대로 붙여넣을 수 있다.
그래서 3단 폴백으로 화자를 판별한다:
  1) explicit — 모든 접두어가 SPEAKER_ALIASES에 걸림
  2) guessed  — 서로 다른 이름이 정확히 2개만 등장 (첫 등장 -> other, 나머지 -> me)
  3) unknown  — 그 외. 화자 없이도 Extract~Solar는 동작한다.
"""

import re

from . import masking, postprocess

SPEAKER_ALIASES = {
    "나": "me", "저": "me", "본인": "me", "me": "me",
    "상대방": "other", "상대": "other", "판매자": "other", "구매자": "other", "other": "other",
    "시스템": "system", "안내": "system", "system": "system",
}

PREFIX_RE = re.compile(r"^([^\s:：]{1,12})\s*[:：]\s*(.*)$")


def _normalize(token):
    return SPEAKER_ALIASES.get(token) or SPEAKER_ALIASES.get(token.lower())


def _new_message(speaker, text, kind, capture):
    return {
        "speaker": speaker, "text": text, "kind": kind,
        "capture": capture, "y": None, "x_min": None, "x_max": None,
    }


def parse_raw_text(raw_text):
    """raw_text -> (messages, meta). meta = {"speaker_mode", "masked_counts"}."""
    raw_lines = raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    parsed = []  # (token_or_None, remainder_text, original_line)
    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            continue
        if line == "---":
            parsed.append(("__boundary__", None, None))
            continue
        m = PREFIX_RE.match(line)
        if m:
            parsed.append((m.group(1), m.group(2), line))
        else:
            parsed.append((None, line, line))

    speaker_tokens = [
        t for t, _, _ in parsed
        if t not in (None, "__boundary__") and _normalize(t) != "system"
    ]
    distinct = list(dict.fromkeys(speaker_tokens))

    explicit_ok = bool(speaker_tokens) and all(
        _normalize(t) in ("me", "other") for t in speaker_tokens
    )

    token_map = {}
    if explicit_ok:
        speaker_mode = "explicit"
        token_map = {t: _normalize(t) for t in distinct}
    elif len(distinct) == 2:
        speaker_mode = "guessed"
        used_roles = set()
        for t in distinct:
            role = _normalize(t)
            if role in ("me", "other"):
                token_map[t] = role
                used_roles.add(role)
        for t in distinct:
            if t in token_map:
                continue
            for role in ("other", "me"):
                if role not in used_roles:
                    token_map[t] = role
                    used_roles.add(role)
                    break
    else:
        speaker_mode = "unknown"

    messages = []
    capture_index = 0
    current = None

    for token, text, original_line in parsed:
        if token == "__boundary__":
            capture_index += 1
            current = None
            continue

        if token is not None and _normalize(token) == "system":
            messages.append(_new_message("system", text, "system", capture_index))
            current = None
            continue

        if speaker_mode == "unknown":
            messages.append(_new_message(None, original_line, "message", capture_index))
            current = None
            continue

        if token is not None:
            messages.append(_new_message(token_map[token], text, "message", capture_index))
            current = len(messages) - 1
            continue

        # 접두어 없는 줄 -> 직전 메시지에 이어붙임 (없으면 화자 미상으로 새로 시작)
        if current is not None:
            messages[current]["text"] += "\n" + text
        else:
            messages.append(_new_message(None, text, "message", capture_index))
            current = len(messages) - 1

    for msg in messages:
        msg["text"] = postprocess.TIMESTAMP_RE.sub("", msg["text"]).strip()

    messages, masked_counts = masking.mask_messages(messages)

    meta = {"speaker_mode": speaker_mode, "masked_counts": masked_counts}
    return messages, meta
