"""프론트 frontend/src/types/promise.ts 와의 하드 계약.

필드명 하나라도 다르면 프론트가 그대로 깨진다 (배열 필드에 .length를 무조건
호출하는 등). description은 사실상 프롬프트 역할을 하므로 AGENTS.md의 스키마
주석을 그대로 옮겨 적는다.
"""

EXTRACT_PROPERTIES = {
    "item": {
        "type": "string",
        "description": "거래 품목명. 예: '애플 아이패드 에어 5세대 64GB'.",
    },
    "final_price": {
        "type": "integer",
        "description": (
            "최종 합의가(원). 협상 중 거절된 제안 금액이 아니라 실제로 합의된 "
            "최종 금액. '5.5만원'처럼 만원 단위로 언급되면 원 단위로 환산 "
            "(예: 5.5만원 -> 55000, 5.5 -> 55000). 대화에서 합의된 금액을 "
            "찾을 수 없으면 0."
        ),
    },
    "location": {
        "type": ["string", "null"],
        "description": (
            "양측이 실제로 합의한 거래 장소만 기입. 한쪽이 자기 위치를 "
            "언급만 한 경우(예: '저는 가야동이에요')는 합의된 장소가 아니므로 "
            "null로 두고 missing_items에 반영할 것."
        ),
    },
    "datetime": {
        "type": ["string", "null"],
        "description": "양측이 합의한 거래 일시. 합의되지 않았으면 null.",
    },
    "delivery_method": {
        "type": ["string", "null"],
        "description": (
            "직거래/택배/반택 등 합의된 거래 방식만. 질문만 오가고 답이 "
            "없었다면 null."
        ),
    },
    "payment_method": {
        "type": ["string", "null"],
        "description": (
            "안심결제/현금/계좌이체 등 합의된 결제수단만. 문의만 오간 경우는 "
            "null."
        ),
    },
    "accessories": {
        "type": "array",
        "items": {"type": "string"},
        "description": "포함된 구성품 목록(충전기, 케이스 등). 없으면 빈 배열.",
    },
    "refund_policy": {
        "type": ["string", "null"],
        "description": "합의된 환불/교환 조건. 언급 없으면 null.",
    },
    "condition_info": {
        "type": ["string", "null"],
        "description": "제품 상태 정보(배터리 성능, 사용감 등). 언급 없으면 null.",
    },
    "risk_signals": {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "대화 중 위험하거나 의심스러운 발언의 원문 그대로. "
            "예: '제가 급전이 필요해서'. 없으면 빈 배열."
        ),
    },
}

EXTRACT_REQUIRED = list(EXTRACT_PROPERTIES.keys())

EXTRACT_SCHEMA = {
    "name": "promise_extract_fields",
    "schema": {
        "type": "object",
        "properties": EXTRACT_PROPERTIES,
        "required": EXTRACT_REQUIRED,
        "additionalProperties": False,
    },
}

CHAT_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "speaker": {
            "type": "string",
            "enum": ["me", "other"],
            "description": "발화자. 나=me, 상대방=other.",
        },
        "text": {
            "type": "string",
            "description": "대화록에 실제로 있는 문장을 글자 그대로 복사. 새로 지어내지 말 것.",
        },
        "highlight": {
            "type": "string",
            "description": (
                "text 문자열 안에 실제로 포함된 부분 문자열만. 강조할 부분이 "
                "없으면 빈 문자열로 둘 것."
            ),
        },
    },
    "required": ["speaker", "text", "highlight"],
    "additionalProperties": False,
}

CHECKLIST_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "description": "영문 소문자 kebab/snake 식별자. 예: payment, battery, defect.",
        },
        "label": {"type": "string", "description": "짧은 한국어 라벨. 예: '결제 방식'."},
        "question": {
            "type": "string",
            "description": "confirm_questions 중 이 항목에 대응되는 질문.",
        },
        "description": {
            "type": "string",
            "description": (
                "왜 중요한지 + 확인하지 않으면 어떤 문제가 생기는지, 2문장 "
                "이내 존댓말로 설명."
            ),
        },
        "relatedMessages": {
            "type": "array",
            "items": CHAT_MESSAGE_SCHEMA,
            "description": (
                "이 항목과 관련된 실제 대화 메시지. 근거가 되는 메시지가 "
                "없으면 빈 배열."
            ),
        },
    },
    "required": ["id", "label", "question", "description", "relatedMessages"],
    "additionalProperties": False,
}

JUDGE_PROPERTIES = {
    **EXTRACT_PROPERTIES,
    "conflicts": {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "서로 다른 값이 대화 중 여러 번 언급되어 충돌하는 경우 그 내용을 "
            "한국어 문장으로 설명. 예: '게시가는 31만원인데 실제 대화에서는 "
            "37만원으로 합의됨'. detected_price_candidates에 서로 다른 금액이 "
            "2개 이상 주어지면 반드시 여기 명시할 것. 충돌이 없으면 빈 배열."
        ),
    },
    "missing_items": {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "대화에서 확인되지 않았거나 합의가 불분명한 항목의 한국어 라벨. "
            "예: '배터리 성능', '결제 방식'."
        ),
    },
    "risk_notes": {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "risk_signals의 각 항목에 대해 왜 위험한지와 어떻게 확인하면 "
            "좋을지 설명하는 존댓말 문장. 가격 충돌이 있다면 리스크로 승격해 "
            "여기에도 반영할 것."
        ),
    },
    "confirm_questions": {
        "type": "array",
        "items": {"type": "string"},
        "description": (
            "missing_items와 risk_notes를 바탕으로 상대방에게 보낼 확인 "
            "질문. 사용자('나')의 채팅 말투를 그대로 유지해서 작성."
        ),
    },
    "checklistItems": {
        "type": "array",
        "items": CHECKLIST_ITEM_SCHEMA,
        "description": (
            "missing_items/risk_notes를 화면에 보여줄 체크리스트 형태로 "
            "구조화한 것. 3~5개. relatedMessages의 text는 반드시 대화록 "
            "원문 그대로 복사."
        ),
    },
}

JUDGE_REQUIRED = list(JUDGE_PROPERTIES.keys())

JUDGE_SCHEMA = {
    "name": "promise_judgement",
    "schema": {
        "type": "object",
        "properties": JUDGE_PROPERTIES,
        "required": JUDGE_REQUIRED,
        "additionalProperties": False,
    },
}

CARD_SCHEMA = {
    "name": "promise_card_text",
    "schema": {
        "type": "object",
        "properties": {
            "card_title": {"type": "string", "description": "약속 카드 상단 제목 문구."},
            "card_summary": {"type": "string", "description": "카드 본문 요약 1~2문장."},
            "one_line_warning": {
                "type": "string",
                "description": "리스크가 있으면 한 줄 경고 문구, 없으면 빈 문자열.",
            },
        },
        "required": ["card_title", "card_summary", "one_line_warning"],
        "additionalProperties": False,
    },
}
