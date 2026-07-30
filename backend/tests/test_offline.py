"""네트워크 없이 즉시 실행하는 단위 검증. pytest 불필요.

    python backend/tests/test_offline.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline import judge, masking, postprocess, text_input, validate  # noqa: E402

FAILURES = []
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "ipad_chat.txt")


def _el(category, text, x_min, x_max, y_min, y_max, page=1):
    return {
        "category": category, "page": page, "text": text,
        "coords": [{"x": x_min, "y": y_min}, {"x": x_max, "y": y_max}],
    }


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" - {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


def test_masking_targets():
    text = (
        "계좌는 농협 3511094710813 이고 연락처는 010-1234-5678 이에요. "
        "집주소는 101동 502호 인데 참고만 하세요."
    )
    masked, counts = masking.mask_text(text)
    check("phone masked", "[전화번호]" in masked and "010-1234-5678" not in masked)
    check("account masked (bank-prefixed)", "[계좌번호]" in masked and "3511094710813" not in masked)
    check("address masked", "[상세주소]" in masked and "101동 502호" not in masked)
    check("counts reflect all three", counts == {"phone": 1, "account": 1, "address": 1}, str(counts))


def test_masking_avoids_false_positives():
    date_text = "2026-01-28 에 뵈어요"
    masked, counts = masking.mask_text(date_text)
    check("date not masked", masked == date_text, masked)
    check("date masking counts zero", counts["account"] == 0, str(counts))

    price_text = "370,000원 준비해서 나올게요"
    masked, counts = masking.mask_text(price_text)
    check("comma price not masked", masked == price_text, masked)

    price_text2 = "370000원에 드릴게요"
    masked, counts = masking.mask_text(price_text2)
    check("6-digit price not masked", masked == price_text2, masked)

    location_text = "저는 가야동 근처라 거기서 가까운 곳으로 정해봤어요"
    masked, counts = masking.mask_text(location_text)
    check("location '가야동' not masked", masked == location_text, masked)
    check("location masking counts zero", counts["address"] == 0, str(counts))


def test_mask_messages_aggregates_counts():
    messages = [
        {"speaker": "me", "text": "010-1234-5678로 연락주세요"},
        {"speaker": "other", "text": "네 101동 502호로 갈게요"},
    ]
    masked, total = masking.mask_messages(messages)
    check("mask_messages phone count", total["phone"] == 1, str(total))
    check("mask_messages address count", total["address"] == 1, str(total))
    check(
        "mask_messages preserves non-text keys",
        masked[0]["speaker"] == "me" and masked[1]["speaker"] == "other",
    )


def test_parse_raw_text_explicit_fixture():
    raw_text = open(FIXTURE_PATH, encoding="utf-8").read()
    messages, meta = text_input.parse_raw_text(raw_text)
    check("fixture speaker_mode explicit", meta["speaker_mode"] == "explicit", meta["speaker_mode"])
    check("fixture has messages", len(messages) > 5, str(len(messages)))
    check("fixture first speaker is me", messages[0]["speaker"] == "me", messages[0]["speaker"])
    check(
        "fixture system message captured",
        any(m["kind"] == "system" for m in messages),
    )
    check(
        "fixture masking applied (no raw phone)",
        all("010-1234-5678" not in m["text"] for m in messages),
    )
    check(
        "fixture masking applied (no raw account)",
        all("3511094710813" not in m["text"] for m in messages),
    )
    check(
        "fixture preserves date",
        any("2026-01-28" in m["text"] for m in messages),
    )
    check(
        "fixture preserves location 가야동",
        any("가야동" in m["text"] for m in messages),
    )


def test_parse_raw_text_guessed_mode():
    raw_text = (
        "지훈: 안녕하세요 아직 판매하시나요\n"
        "민수: 네 아직 있어요\n"
        "지훈: 5만원에 가능할까요\n"
        "민수: 네 좋아요\n"
    )
    messages, meta = text_input.parse_raw_text(raw_text)
    check("guessed mode detected", meta["speaker_mode"] == "guessed", meta["speaker_mode"])
    # 먼저 등장한 이름(지훈) -> other, 나머지(민수) -> me
    check("guessed: first speaker -> other", messages[0]["speaker"] == "other", messages[0]["speaker"])
    check("guessed: second speaker -> me", messages[1]["speaker"] == "me", messages[1]["speaker"])


def test_parse_raw_text_unknown_mode():
    raw_text = "아이패드 팝니다\n상태 좋아요\n연락주세요\n"
    messages, meta = text_input.parse_raw_text(raw_text)
    check("unknown mode detected", meta["speaker_mode"] == "unknown", meta["speaker_mode"])
    check("unknown mode: one message per line", len(messages) == 3, str(len(messages)))
    check("unknown mode: speaker is None", all(m["speaker"] is None for m in messages))


def test_parse_raw_text_continuation_and_boundary():
    raw_text = (
        "나: 첫 줄입니다\n"
        "이어지는 두번째 줄\n"
        "---\n"
        "상대방: 다음 캡처 메시지\n"
    )
    messages, meta = text_input.parse_raw_text(raw_text)
    check("continuation merged into one message", len(messages) == 2, str(len(messages)))
    check(
        "continuation text joined with newline",
        "첫 줄입니다\n이어지는 두번째 줄" == messages[0]["text"],
        messages[0]["text"],
    )
    check("boundary increments capture", messages[1]["capture"] == 1, str(messages[1]["capture"]))


def test_parse_raw_text_timestamp_stripped():
    raw_text = "나: 안녕하세요 오후 3:12 에 봬요\n"
    messages, meta = text_input.parse_raw_text(raw_text)
    check("timestamp removed", "3:12" not in messages[0]["text"], messages[0]["text"])


def test_validate_price_conflict_detection():
    transcript = open(FIXTURE_PATH, encoding="utf-8").read()
    candidates = validate.find_price_candidates(transcript)
    check("price candidates include 310000", 310000 in candidates, str(candidates))
    check("price candidates include 370000", 370000 in candidates, str(candidates))
    result = validate.validate({"item": "아이패드", "final_price": 370000}, transcript)
    check("price_conflict true for 31만 vs 37만", result["price_conflict"] is True, str(result))


def test_validate_no_false_conflict_for_negotiation():
    transcript = "6만원에 파는데 5.5만원 어때요? 그럼 5.8만원에 주세요"
    result = validate.validate({"item": "SSD", "final_price": 58000}, transcript)
    check(
        "no price_conflict within negotiation range",
        result["price_conflict"] is False,
        str(result),
    )


def test_validate_required_fields():
    missing_both = validate.check_required({"item": "", "final_price": 0})
    check("missing item detected", "품목" in missing_both, str(missing_both))
    check("missing price detected", "가격" in missing_both, str(missing_both))
    missing_none = validate.check_required({"item": "아이패드", "final_price": 370000})
    check("no missing fields when complete", missing_none == [], str(missing_none))


def test_sanitize_checklist_removes_hallucinated_message():
    messages = [
        {"speaker": "other", "text": "제가 오늘 그쪽으로 갈테니까 직거래 가능하시려나요.. 제가 급전이 필요해서"},
    ]
    items = [{
        "id": "payment", "label": "결제 방식", "question": "안심결제로 진행해도 괜찮을까요?",
        "description": "설명", "relatedMessages": [
            {"speaker": "other", "text": "제가 급전이 필요해서", "highlight": "급전이 필요해서"},
            {"speaker": "other", "text": "대화록에 없는 문장입니다", "highlight": ""},
        ],
    }]
    cleaned = judge.sanitize_checklist(items, messages)
    check("kept 1 valid relatedMessage", len(cleaned[0]["relatedMessages"]) == 1, str(cleaned))


def test_sanitize_checklist_drops_bad_highlight():
    messages = [{"speaker": "other", "text": "네 있습니다 있습니다"}]
    items = [{
        "id": "x", "label": "l", "question": "q", "description": "d",
        "relatedMessages": [
            {"speaker": "other", "text": "네 있습니다 있습니다", "highlight": "없는말"},
        ],
    }]
    cleaned = judge.sanitize_checklist(items, messages)
    check(
        "invalid highlight dropped but message kept",
        len(cleaned[0]["relatedMessages"]) == 1 and "highlight" not in cleaned[0]["relatedMessages"][0],
        str(cleaned),
    )

    items2 = [{
        "id": "y", "label": "l", "question": "q", "description": "d",
        "relatedMessages": [
            {"speaker": "other", "text": "네 있습니다 있습니다", "highlight": "있습니다"},
        ],
    }]
    cleaned2 = judge.sanitize_checklist(items2, messages)
    check(
        "highlight appearing twice is dropped",
        "highlight" not in cleaned2[0]["relatedMessages"][0],
        str(cleaned2),
    )


def test_sanitize_checklist_dedupes_ids():
    items = [
        {"id": "battery", "label": "l1", "question": "q1", "description": "d1", "relatedMessages": []},
        {"id": "battery", "label": "l2", "question": "q2", "description": "d2", "relatedMessages": []},
    ]
    cleaned = judge.sanitize_checklist(items, [])
    ids = [c["id"] for c in cleaned]
    check("duplicate ids get suffixed", ids == ["battery", "battery-2"], str(ids))


def test_elements_to_messages_y_reorder():
    # 실제 화면 순서: 첫번째 메시지(y=0.2)가 먼저인데 JSON에는 두번째(y=0.5)가 먼저 옴
    elements = [
        _el("paragraph", "두번째 메시지", 0.5, 0.93, 0.5, 0.55),
        _el("paragraph", "첫번째 메시지", 0.16, 0.5, 0.2, 0.25),
    ]
    messages = postprocess.elements_to_messages(elements, 0)
    check("y reorder: first message first", messages[0]["text"] == "첫번째 메시지", str(messages))
    check("y reorder: second message second", messages[1]["text"] == "두번째 메시지", str(messages))


def test_elements_to_messages_header_footer_removed():
    elements = [
        _el("paragraph", "헤더 로고", 0.3, 0.7, 0.02, 0.05),  # y_center=0.035 < 0.12
        _el("paragraph", "정상 메시지", 0.16, 0.5, 0.3, 0.35),
        _el("paragraph", "입력창 텍스트", 0.1, 0.9, 0.9, 0.95),  # y_center=0.925 > 0.88
    ]
    messages = postprocess.elements_to_messages(elements, 0)
    check(
        "header/footer stripped, only real message kept",
        len(messages) == 1 and messages[0]["text"] == "정상 메시지",
        str(messages),
    )


def test_elements_to_messages_speaker_assignment():
    # 실험① §3-1 실측 좌표: 당근 왼쪽 x_min≈0.16/오른쪽 x_max≈0.933,
    # 번개 왼쪽 x_min≈0.08/오른쪽 x_max≈0.91, iMessage 왼쪽 x_min≈0.07/오른쪽 x_max≈0.93
    elements = [
        _el("paragraph", "당근 왼쪽(상대방)", 0.16, 0.55, 0.3, 0.35),
        _el("paragraph", "당근 오른쪽(나)", 0.5, 0.933, 0.4, 0.45),
        _el("paragraph", "번개 왼쪽(상대방)", 0.08, 0.5, 0.5, 0.55),
        _el("paragraph", "번개 오른쪽(나)", 0.5, 0.91, 0.6, 0.65),
        _el("paragraph", "iMessage 왼쪽(상대방)", 0.07, 0.5, 0.7, 0.75),
        _el("paragraph", "iMessage 오른쪽(나)", 0.5, 0.93, 0.8, 0.85),
    ]
    messages = postprocess.elements_to_messages(elements, 0)
    by_text = {m["text"]: m["speaker"] for m in messages}
    check("당근 왼쪽 -> other", by_text["당근 왼쪽(상대방)"] == "other", str(by_text))
    check("당근 오른쪽 -> me", by_text["당근 오른쪽(나)"] == "me", str(by_text))
    check("번개 왼쪽 -> other", by_text["번개 왼쪽(상대방)"] == "other", str(by_text))
    check("번개 오른쪽 -> me", by_text["번개 오른쪽(나)"] == "me", str(by_text))
    check("iMessage 왼쪽 -> other", by_text["iMessage 왼쪽(상대방)"] == "other", str(by_text))
    check("iMessage 오른쪽 -> me", by_text["iMessage 오른쪽(나)"] == "me", str(by_text))


def test_elements_to_messages_system_and_figure():
    elements = [
        _el("paragraph", "안심결제로 안전하게 거래하세요", 0.1, 0.9, 0.3, 0.34),  # x스팬 0.8 -> system
        _el("figure", "", 0.2, 0.8, 0.4, 0.5),
    ]
    messages = postprocess.elements_to_messages(elements, 0)
    check("wide system phrase -> kind system", messages[0]["kind"] == "system", str(messages))
    check(
        "figure -> photo event",
        messages[1]["kind"] == "photo" and messages[1]["text"] == "사진 공유됨",
        str(messages),
    )


def test_elements_to_messages_noise_and_timestamp():
    elements = [
        _el("paragraph", "₩", 0.2, 0.3, 0.3, 0.32),  # 노이즈: 한글/숫자 없는 2글자 이하
        _el("paragraph", "안녕하세요 오후 3:12 입니다", 0.16, 0.5, 0.4, 0.45),
    ]
    messages = postprocess.elements_to_messages(elements, 0)
    check("noise icon block dropped", len(messages) == 1, str(messages))
    check("timestamp stripped from remaining message", "3:12" not in messages[0]["text"], str(messages))


def test_build_fallback_judgement():
    extract_result = {
        "item": "아이패드", "final_price": 370000, "location": None, "datetime": None,
        "delivery_method": "직거래", "payment_method": None, "accessories": [],
        "refund_policy": None, "condition_info": None, "risk_signals": ["제가 급전이 필요해서"],
    }
    validation = {"missing_required": [], "detected_price_candidates": [310000, 370000], "price_conflict": True}
    fallback = judge.build_fallback_judgement(extract_result, validation)
    check("fallback keeps extract fields", fallback["item"] == "아이패드", str(fallback))
    check("fallback flags price conflict", len(fallback["conflicts"]) == 1, str(fallback))
    check("fallback flags missing location", "거래 장소" in fallback["missing_items"], str(fallback))
    check("fallback has risk note for risk signal", len(fallback["risk_notes"]) == 1, str(fallback))
    check("fallback has confirm questions", len(fallback["confirm_questions"]) >= 1, str(fallback))


def test_elements_to_messages_capture_index_preserved():
    elements = [_el("paragraph", "메시지", 0.16, 0.5, 0.3, 0.35)]
    messages = postprocess.elements_to_messages(elements, 2)
    check("capture index preserved", messages[0]["capture"] == 2, str(messages))


if __name__ == "__main__":
    test_masking_targets()
    test_masking_avoids_false_positives()
    test_mask_messages_aggregates_counts()
    test_parse_raw_text_explicit_fixture()
    test_parse_raw_text_guessed_mode()
    test_parse_raw_text_unknown_mode()
    test_parse_raw_text_continuation_and_boundary()
    test_parse_raw_text_timestamp_stripped()
    test_validate_price_conflict_detection()
    test_validate_no_false_conflict_for_negotiation()
    test_validate_required_fields()
    test_sanitize_checklist_removes_hallucinated_message()
    test_sanitize_checklist_drops_bad_highlight()
    test_sanitize_checklist_dedupes_ids()
    test_elements_to_messages_y_reorder()
    test_elements_to_messages_header_footer_removed()
    test_elements_to_messages_speaker_assignment()
    test_elements_to_messages_system_and_figure()
    test_elements_to_messages_noise_and_timestamp()
    test_elements_to_messages_capture_index_preserved()
    test_build_fallback_judgement()

    print()
    if FAILURES:
        print(f"{len(FAILURES)}건 실패: {FAILURES}")
        sys.exit(1)
    print("전부 통과")
