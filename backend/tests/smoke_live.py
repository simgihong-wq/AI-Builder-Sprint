"""실제 Upstage API로 raw_text -> transcript -> extract -> validate(-> judge)를
순서대로 돌려 단계별 결과와 소요시간을 출력한다.

    python backend/tests/smoke_live.py backend/tests/fixtures/ipad_chat.txt
    python backend/tests/smoke_live.py backend/tests/fixtures/ipad_chat.txt --judge

judge.py가 아직 없으면 --judge 없이 extract/validate까지만 돈다.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from pipeline import extract, postprocess, text_input, validate  # noqa: E402
from pipeline.upstage_client import UpstageError  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("사용법: python smoke_live.py <fixture.txt> [--judge]")
        sys.exit(1)
    fixture_path = sys.argv[1]
    run_judge = "--judge" in sys.argv[2:]

    raw_text = open(fixture_path, encoding="utf-8").read()

    timings = {}

    t0 = time.time()
    messages, meta = text_input.parse_raw_text(raw_text)
    timings["parse_raw_text_ms"] = int((time.time() - t0) * 1000)
    print(f"== 화자 모드: {meta['speaker_mode']} / 마스킹: {meta['masked_counts']} ==")
    print(f"메시지 {len(messages)}건\n")

    transcript = postprocess.build_transcript(messages)
    print("== 대화록 ==")
    print(transcript)
    print()

    try:
        t0 = time.time()
        extract_result = extract.extract_fields(transcript)
        timings["extract_ms"] = int((time.time() - t0) * 1000)
    except UpstageError as exc:
        print(f"[FAIL] extract 단계: {exc.user_message}\n  detail: {exc.detail}")
        sys.exit(1)

    print("== Extract 결과 ==")
    print(json.dumps(extract_result, ensure_ascii=False, indent=2))
    print()

    t0 = time.time()
    validation = validate.validate(extract_result, transcript)
    timings["validate_ms"] = int((time.time() - t0) * 1000)
    print("== 코드 검증 결과 ==")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print()

    assertions = []
    assertions.append(("final_price == 370000", extract_result.get("final_price") == 370000))
    assertions.append(("price_conflict detected", validation.get("price_conflict") is True))

    judgement = None
    if run_judge:
        from pipeline import judge  # 지연 import: judge.py가 없어도 --judge 없이는 동작

        t0 = time.time()
        judgement = judge.judge(transcript, extract_result, validation, messages, meta["speaker_mode"])
        timings["judge_ms"] = int((time.time() - t0) * 1000)
        print("== Solar 판단 결과 ==")
        print(json.dumps(judgement, ensure_ascii=False, indent=2))
        print()
        assertions.append(("conflicts >= 1", len(judgement.get("conflicts", [])) >= 1))
        assertions.append(("confirm_questions >= 2", len(judgement.get("confirm_questions", [])) >= 2))

    print("== 소요시간(ms) ==")
    print(json.dumps(timings, ensure_ascii=False, indent=2))
    print()

    print("== 검증 ==")
    all_ok = True
    for name, ok in assertions:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        all_ok = all_ok and ok

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
