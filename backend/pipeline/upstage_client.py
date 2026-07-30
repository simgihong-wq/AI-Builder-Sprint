"""Upstage API 호출 공통 클라이언트. API 키는 여기서만 읽는다 (호출 시점에)."""

import json
import os
import time

import requests

BASE_URL = "https://api.upstage.ai/v1"

_PARSE_HINT = " 캡처가 잘 안 읽히면 텍스트 붙여넣기로 시도해주세요."


class UpstageError(Exception):
    def __init__(self, user_message, *, stage, detail="", status=None):
        super().__init__(user_message)
        self.user_message = user_message
        self.stage = stage
        self.detail = detail
        self.status = status


def _api_key():
    key = os.environ.get("UPSTAGE_API_KEY")
    if not key:
        raise UpstageError(
            "서버 설정이 완료되지 않았어요. 관리자에게 문의해주세요.",
            stage="config",
            detail="UPSTAGE_API_KEY not set",
        )
    return key


def _headers(extra=None):
    headers = {"Authorization": f"Bearer {_api_key()}"}
    if extra:
        headers.update(extra)
    return headers


def _hint(stage):
    return _PARSE_HINT if stage == "parse" else ""


def _map_error(stage, *, detail, status=None, is_timeout=False, is_connection=False):
    hint = _hint(stage)
    if is_timeout:
        return UpstageError(
            f"분석이 오래 걸리고 있어요. 캡처 수를 줄이거나 잠시 후 다시 시도해주세요.{hint}",
            stage=stage, detail=detail, status=status,
        )
    if status in (401, 403):
        return UpstageError(
            f"서버 설정에 문제가 있어요. 관리자에게 문의해주세요.{hint}",
            stage=stage, detail=detail, status=status,
        )
    if status == 429:
        return UpstageError(
            f"요청이 많아요. 30초 후 다시 시도해주세요.{hint}",
            stage=stage, detail=detail, status=status,
        )
    if is_connection or (status is not None and status >= 500):
        return UpstageError(
            f"분석 서버와 연결하지 못했어요. 잠시 후 다시 시도해주세요.{hint}",
            stage=stage, detail=detail, status=status,
        )
    return UpstageError(
        f"분석 중 문제가 생겼어요. 잠시 후 다시 시도해주세요.{hint}",
        stage=stage, detail=detail, status=status,
    )


def _request_with_retry(method, url, *, stage, timeout, **kwargs):
    attempts = 0
    while True:
        attempts += 1
        try:
            resp = requests.request(method, url, timeout=timeout, **kwargs)
        except requests.Timeout as exc:
            if attempts < 2:
                time.sleep(0.8)
                continue
            raise _map_error(stage, detail=str(exc), is_timeout=True)
        except requests.ConnectionError as exc:
            if attempts < 2:
                time.sleep(0.8)
                continue
            raise _map_error(stage, detail=str(exc), is_connection=True)

        if resp.status_code == 429 and attempts < 2:
            time.sleep(3)
            continue
        if resp.status_code >= 500 and attempts < 2:
            time.sleep(0.8)
            continue
        if resp.status_code >= 400:
            raise _map_error(stage, detail=resp.text[:500], status=resp.status_code)
        return resp


def post_json(path, payload, *, stage, timeout=60):
    resp = _request_with_retry(
        "POST", f"{BASE_URL}{path}", stage=stage, timeout=timeout,
        headers=_headers({"Content-Type": "application/json"}), json=payload,
    )
    try:
        return resp.json()
    except ValueError as exc:
        raise _map_error(stage, detail=str(exc), status=resp.status_code)


def post_multipart(path, files, data, *, stage, timeout=120):
    resp = _request_with_retry(
        "POST", f"{BASE_URL}{path}", stage=stage, timeout=timeout,
        headers=_headers(), files=files, data=data,
    )
    try:
        return resp.json()
    except ValueError as exc:
        raise _map_error(stage, detail=str(exc), status=resp.status_code)


def parse_json_content(response, *, stage):
    """OpenAI 스타일 응답(choices[0].message.content, JSON 문자열)을 dict로 파싱."""
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise UpstageError(
            "분석 결과를 읽지 못했어요. 다시 시도해주세요.",
            stage=stage, detail=f"{exc}: {str(response)[:500]}",
        )

    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise UpstageError(
            "분석 결과를 읽지 못했어요. 다시 시도해주세요.",
            stage=stage, detail=f"{exc}: {text[:500]}",
        )


def chat_json(model, messages, *, stage, schema=None, temperature=0.1,
              max_tokens=3000, timeout=90, path="/chat/completions"):
    """schema-guided JSON 응답을 반환하는 chat-completions 스타일 호출.

    Information Extraction(/information-extraction)과 Chat Completions
    (/chat/completions) 둘 다 choices[0].message.content 형태로 응답하므로
    같은 헬퍼를 공유한다.
    """
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if schema is not None:
        payload["response_format"] = {"type": "json_schema", "json_schema": schema}
    response = post_json(path, payload, stage=stage, timeout=timeout)
    return parse_json_content(response, stage=stage)
