import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from pipeline import orchestrator
from pipeline.upstage_client import UpstageError

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB

ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".heic"}
MAX_IMAGES = 5
MAX_TEXT_LENGTH = 20000


def ok(data):
    return jsonify({"ok": True, "data": data, "error": None})


def err(message, status=400):
    return jsonify({"ok": False, "data": None, "error": message}), status


@app.get("/health")
def health():
    return ok({"status": "up", "upstage_key_set": bool(os.environ.get("UPSTAGE_API_KEY"))})


@app.post("/api/analyze")
def analyze():
    files = [f for f in request.files.getlist("images") if f and f.filename]

    try:
        if files:
            if len(files) > MAX_IMAGES:
                return err(f"캡처는 최대 {MAX_IMAGES}장까지 올릴 수 있어요.")
            for f in files:
                ext = os.path.splitext(f.filename)[1].lower()
                if ext not in ALLOWED_IMAGE_EXT:
                    return err("이미지 파일만 올릴 수 있어요.")
            data = orchestrator.analyze_images(files)
        else:
            body = request.get_json(silent=True) or {}
            raw_text = (body.get("raw_text") or body.get("text") or "").strip()
            if len(raw_text) < 10:
                return err("캡처를 올리거나 대화 내용을 붙여넣어주세요.")
            if len(raw_text) > MAX_TEXT_LENGTH:
                return err("대화가 너무 길어요. 핵심 부분만 붙여넣어주세요.")
            data = orchestrator.analyze_text(raw_text)
    except UpstageError as exc:
        app.logger.error("upstage error [%s]: %s", exc.stage, exc.detail)
        return err(exc.user_message, 502)
    except Exception:
        app.logger.exception("analyze 처리 중 예상치 못한 오류")
        return err("분석 중 문제가 생겼어요. 잠시 후 다시 시도해주세요.", 500)

    return ok(data)


@app.errorhandler(413)
def too_large(_e):
    return err("업로드 용량이 너무 커요. 캡처 수를 줄이거나 용량을 낮춰주세요.", 413)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
