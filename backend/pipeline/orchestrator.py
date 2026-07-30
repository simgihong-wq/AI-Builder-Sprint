"""파이프라인 전체 조립. app.py를 import하지 않는다(순환참조 방지) —
순수 dict를 반환하거나 upstage_client.UpstageError를 던질 뿐이다.
"""

import time

from . import extract, judge, postprocess, text_input, validate
from .upstage_client import UpstageError


def _public_messages(messages):
    """ChatTranscript.tsx용 — speaker가 me/other인 것만, 필요한 키만 남긴다."""
    return [
        {"speaker": m["speaker"], "text": m["text"]}
        for m in messages
        if m.get("speaker") in ("me", "other")
    ]


def _try_polish_card(judgement):
    """⑥ 카드 문구 다듬기(스트레치). card.py가 없거나 실패해도 응답을 막지 않는다."""
    try:
        from . import card
    except ImportError:
        return None
    try:
        return card.polish_card(judgement)
    except Exception:
        return None


def _run(messages, meta, *, source):
    timings = {}

    t0 = time.time()
    transcript = postprocess.build_transcript(messages)
    timings["transcript_ms"] = int((time.time() - t0) * 1000)

    t0 = time.time()
    extract_result = extract.extract_fields(transcript)
    timings["extract_ms"] = int((time.time() - t0) * 1000)

    t0 = time.time()
    validation = validate.validate(extract_result, transcript)
    timings["validate_ms"] = int((time.time() - t0) * 1000)

    t0 = time.time()
    speaker_mode = meta.get("speaker_mode", "unknown")
    degraded = False
    try:
        judgement = judge.judge(transcript, extract_result, validation, messages, speaker_mode)
    except UpstageError:
        judgement = judge.build_fallback_judgement(extract_result, validation)
        degraded = True
    timings["judge_ms"] = int((time.time() - t0) * 1000)

    checklist_items = judgement.pop("checklistItems", [])

    t0 = time.time()
    card_result = _try_polish_card(judgement)
    timings["card_ms"] = int((time.time() - t0) * 1000)

    captures = (max(m.get("capture", 0) for m in messages) + 1) if messages else 0
    timings["total_ms"] = sum(timings.values())

    return {
        "result": judgement,
        "checklistItems": checklist_items,
        "messages": _public_messages(messages),
        "card": card_result,
        "meta": {
            "source": source,
            "captures": captures,
            "speaker_mode": speaker_mode,
            "masked_counts": meta.get("masked_counts", {}),
            "detected_price_candidates": validation.get("detected_price_candidates", []),
            "missing_required": validation.get("missing_required", []),
            "degraded": degraded,
            "timings_ms": timings,
        },
    }


def analyze_text(raw_text):
    messages, meta = text_input.parse_raw_text(raw_text)
    return _run(messages, meta, source="text")


def analyze_images(files):
    from . import parse  # parse.py: task 7에서 채워짐

    captures_elements, masked_counts = parse.parse_images(files)
    all_messages = []
    for index, elements in enumerate(captures_elements):
        all_messages.extend(postprocess.elements_to_messages(elements, index))

    meta = {"speaker_mode": "coordinates", "masked_counts": masked_counts}
    return _run(all_messages, meta, source="images")
