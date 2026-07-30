"""④ 코드 검증 — LLM 없이 결정론적으로 필수 필드 누락·값 충돌 후보를 찾는다.

실험②에서 Extract는 값 충돌에 침묵하고 한쪽 값을 조용히 선택하는 경향이
확인됐다. 여기서 가격 후보를 전부 긁어 클러스터링해두면, ⑤ Solar 프롬프트가
"이 후보들이 서로 충돌하는지 판단하라"는 근거로 사용할 수 있다.
"""

import re

PRICE_WON_RE = re.compile(r"(\d{1,3}(?:,\d{3})+|\d{4,})\s*원")
PRICE_MAN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*만\s*원?")

# 인접한 두 후보가 이 이상 차이 나면 "같은 협상 흐름"이 아니라 "서로 다른
# 금액"으로 본다. SSD 협상 샘플(6만->5.5->5.8, 최대 diff 3000)은 한 클러스터로
# 묶이고, 31만 vs 37만(diff 60000)은 분리되도록 튜닝된 값 — 함부로 낮추지 말 것.
_CLUSTER_MIN_DIFF = 5000
_CLUSTER_MIN_RATIO = 1.05


def find_price_candidates(transcript):
    candidates = set()
    for m in PRICE_WON_RE.finditer(transcript):
        value = int(m.group(1).replace(",", ""))
        if value >= 1000:
            candidates.add(value)
    for m in PRICE_MAN_RE.finditer(transcript):
        value = int(float(m.group(1)) * 10000)
        if value >= 1000:
            candidates.add(value)
    return sorted(candidates)


def _cluster(sorted_values):
    if not sorted_values:
        return []
    clusters = [[sorted_values[0]]]
    for value in sorted_values[1:]:
        prev = clusters[-1][-1]
        diff = value - prev
        ratio = (value / prev) if prev else 1
        if diff >= _CLUSTER_MIN_DIFF and ratio >= _CLUSTER_MIN_RATIO:
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return clusters


def check_required(extract):
    missing = []
    if not extract.get("item"):
        missing.append("품목")
    if not extract.get("final_price"):
        missing.append("가격")
    return missing


def validate(extract, transcript):
    candidates = find_price_candidates(transcript)
    clusters = _cluster(candidates)
    return {
        "missing_required": check_required(extract),
        "detected_price_candidates": candidates,
        "price_conflict": len(clusters) >= 2,
    }
