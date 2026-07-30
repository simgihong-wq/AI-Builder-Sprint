"""① Document Parse. 응답 elements를 얇은 dict로 변환하고, 반환 직전에
마스킹을 적용한다(텍스트가 시스템에 들어오는 두 지점 중 하나 — 나머지 하나는
text_input.py). ocr=force는 실험①이 Playground "OCR Force"로 좌표 품질을
검증했으므로 반드시 유지한다.
"""

from . import masking, upstage_client


def parse_image(file_obj, filename):
    """단일 캡처 -> (elements, masked_counts).

    elements: [{category, page, text(마스킹 완료), coords: [{x,y}, ...]}]
    """
    stream = getattr(file_obj, "stream", file_obj)
    content_type = getattr(file_obj, "mimetype", None) or "application/octet-stream"

    files = {"document": (filename, stream, content_type)}
    data = {
        "model": "document-parse",
        "coordinates": "true",
        "output_formats": '["text"]',
        "ocr": "force",
    }
    response = upstage_client.post_multipart(
        "/document-digitization", files, data, stage="parse", timeout=120,
    )

    elements = []
    counts = {"phone": 0, "account": 0, "address": 0}
    for el in response.get("elements", []):
        content = el.get("content") or {}
        text = content.get("text") or ""
        text, element_counts = masking.mask_text(text)
        for key in counts:
            counts[key] += element_counts[key]
        elements.append({
            "category": el.get("category"),
            "page": el.get("page", 0),
            "text": text,
            "coords": el.get("coordinates") or [],
        })
    return elements, counts


def parse_images(files):
    """여러 캡처 -> (캡처별 elements 리스트, 전체 마스킹 카운트). 업로드
    순서를 그대로 캡처 인덱스로 사용한다(멀티 캡처 통합 — 실험②)."""
    all_elements = []
    total_counts = {"phone": 0, "account": 0, "address": 0}
    for index, file_obj in enumerate(files):
        filename = getattr(file_obj, "filename", f"capture-{index}")
        elements, counts = parse_image(file_obj, filename)
        all_elements.append(elements)
        for key in total_counts:
            total_counts[key] += counts[key]
    return all_elements, total_counts
