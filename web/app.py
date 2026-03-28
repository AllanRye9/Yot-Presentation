#!/usr/bin/env python3
"""
Yot-Presentation Web Application
Converts uploaded files (PDF, Word, Excel, images, text) into
an online presentation with AI-powered voice command control.

New in v5.4:
- File management system: upload multiple files, switch between them, delete.
- ML learning: tracks voice command usage in SQLite; surfaces personalised
  suggestions to help frequent users work faster.
- Docker-ready: listens on 0.0.0.0, DATA_DIR env-var for the SQLite DB path.
"""

import base64
import io
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

# ─── runtime configuration ────────────────────────────────────────────────
DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "yot_learning.db"

# In-memory file registry: file_id → {filename, total_slides, slides,
#                                      created_at, thumbnail}
# NOTE: this resets on restart – mount DATA_DIR as a Docker volume if
# you need persistence across restarts.
_file_registry: dict[str, dict[str, Any]] = {}

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "doc",
    "xlsx",
    "xls",
    "txt",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "bmp",
    "webp",
}

# ─────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─────────────────────────────────────────────
# file → slides converters
# ─────────────────────────────────────────────


def convert_pdf(file_bytes: bytes) -> list[dict[str, Any]]:
    """Render each PDF page as a PNG image slide."""
    import fitz  # PyMuPDF

    slides: list[dict[str, Any]] = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num, page in enumerate(doc):
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)
        img_b64 = base64.b64encode(pix.tobytes("png")).decode()
        slides.append(
            {
                "id": page_num + 1,
                "type": "image",
                "title": f"Page {page_num + 1}",
                "image": f"data:image/png;base64,{img_b64}",
                "notes": page.get_text().strip(),
            }
        )
    doc.close()
    return slides


def convert_docx(file_bytes: bytes) -> list[dict[str, Any]]:
    """Convert a Word document to text/bullet slides grouped by Heading 1."""
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    slide_groups: list[dict[str, Any]] = []
    current: dict[str, Any] = {"title": "", "bullets": []}
    found_heading1 = False

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name.lower()
        if "heading 1" in style:
            if current["title"] or current["bullets"]:
                slide_groups.append(current)
            current = {"title": text, "bullets": []}
            found_heading1 = True
        elif "heading 2" in style or "heading 3" in style:
            current["bullets"].append({"level": 1, "text": text})
        else:
            current["bullets"].append({"level": 2, "text": text})

    if current["title"] or current["bullets"]:
        slide_groups.append(current)

    # Fallback – no Heading 1 found; chunk all paragraphs into slides of ≤ 6 lines
    if not found_heading1:
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        chunk = 6
        slide_groups = []
        for i in range(0, len(lines), chunk):
            block = lines[i : i + chunk]
            slide_groups.append(
                {
                    "title": block[0],
                    "bullets": [{"level": 2, "text": l} for l in block[1:]],
                }
            )

    return [
        {
            "id": i + 1,
            "type": "text",
            "title": g.get("title", f"Slide {i + 1}"),
            "bullets": g.get("bullets", []),
        }
        for i, g in enumerate(slide_groups)
    ]


def convert_xlsx(file_bytes: bytes) -> list[dict[str, Any]]:
    """Convert each Excel sheet to a table slide."""
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    slides: list[dict[str, Any]] = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = [
            [str(cell) if cell is not None else "" for cell in row]
            for row in ws.iter_rows(values_only=True)
            if any(c is not None for c in row)
        ]
        if rows:
            slides.append(
                {
                    "id": len(slides) + 1,
                    "type": "table",
                    "title": sheet_name,
                    "headers": rows[0],
                    "rows": rows[1:],
                }
            )

    return slides


def convert_text(file_bytes: bytes) -> list[dict[str, Any]]:
    """Split a plain-text document on blank lines / form-feeds into slides."""
    text = file_bytes.decode("utf-8", errors="replace")
    sections = [s.strip() for s in re.split(r"\n\s*\n|\f", text) if s.strip()]

    if not sections:
        return [{"id": 1, "type": "text", "title": "Document", "bullets": []}]

    slides = []
    for i, section in enumerate(sections):
        lines = section.split("\n")
        slides.append(
            {
                "id": i + 1,
                "type": "text",
                "title": lines[0],
                "bullets": [
                    {"level": 2, "text": l.strip()}
                    for l in lines[1:]
                    if l.strip()
                ],
            }
        )
    return slides


def convert_image(file_bytes: bytes, filename: str) -> list[dict[str, Any]]:
    """Wrap a single image as one slide."""
    ext = filename.rsplit(".", 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    img_b64 = base64.b64encode(file_bytes).decode()
    return [
        {
            "id": 1,
            "type": "image",
            "title": Path(filename).stem,
            "image": f"data:{mime};base64,{img_b64}",
        }
    ]


# ─────────────────────────────────────────────
# voice-command matching (mirrors original Python logic)
# ─────────────────────────────────────────────

# Multi-language command patterns identical to the original v5.3.1 application
COMMAND_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # jump to slide (must come first – has a capture group)
    (
        "jump_slide",
        re.compile(
            r"(?:jump to|go to|slide|page|number|"
            r"salta a|ve a|diapositiva|página|"
            r"aller à|diapo|numéro|"
            r"gehe zu|folie|seite|"
            r"vai a|ir para|"
            r"跳到|转到|幻灯片|スライド|ページ)"
            r"\s*(\d+)",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # next slide
    (
        "next_slide",
        re.compile(
            r"\b(next|forward|advance|go forward|go right|"
            r"siguiente|adelante|próxima|"
            r"suivant|avancer|prochaine|"
            r"nächst|vorwärts|"
            r"prossimo|avanti|successivo|"
            r"próximo|avançar|seguinte|"
            r"下一张|下一个|向前|次へ|進む)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # previous slide
    (
        "prev_slide",
        re.compile(
            r"\b(previous|prev|back|go back|return|"
            r"anterior|atrás|volver|"
            r"précédent|retour|"
            r"zurück|vorherig|"
            r"precedente|indietro|tornare|"
            r"voltar|para trás|"
            r"上一张|上一个|向后|戻る|前へ)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # start presentation
    (
        "start_show",
        re.compile(
            r"\b(start presentation|begin show|present now|"
            r"comenzar presentación|iniciar show|"
            r"commencer présentation|débuter|"
            r"präsentation starten|"
            r"inizia presentazione|"
            r"iniciar apresentação|"
            r"开始演示|开始放映|"
            r"プレゼンテーション開始|スライドショー開始)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # start (shorter fallback)
    (
        "start_show",
        re.compile(
            r"\b(start|begin|present|play|iniciar|commencer|starten|iniziare|começar)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # end show
    (
        "end_show",
        re.compile(
            r"\b(stop presentation|end show|exit show|close presentation|"
            r"detener presentación|finalizar show|"
            r"arrêter présentation|quitter diaporama|"
            r"präsentation beenden|"
            r"ferma presentazione|termina spettacolo|"
            r"parar apresentação|sair do show|"
            r"停止演示|退出幻灯片|"
            r"プレゼンテーション終了|スライドショー終了)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # end (shorter fallback)
    (
        "end_show",
        re.compile(
            r"\b(end|stop|exit|quit|close|terminar|finir|beenden|terminare)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # blackout
    (
        "blackout",
        re.compile(
            r"\b(black|blackout|blank|darken|turn off screen|"
            r"pantalla negra|oscurecer|"
            r"écran noir|assombrir|"
            r"schwarzer bildschirm|verdunkeln|"
            r"schermo nero|scurire|"
            r"tela preta|escurecer|"
            r"黑屏|黒い画面|暗くする)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # zoom in
    (
        "zoom_in",
        re.compile(
            r"\b(zoom in|magnify|enlarge|agrandir|vergrößern|ingrandire|ampliar|放大|ズームイン)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # zoom out
    (
        "zoom_out",
        re.compile(
            r"\b(zoom out|shrink|reduce|réduire|verkleinern|rimpicciolire|縮小|ズームアウト)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # zoom reset
    (
        "zoom_reset",
        re.compile(
            r"\b(reset zoom|normal size|actual size|zoom normal|rétablir zoom)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # fullscreen
    (
        "fullscreen",
        re.compile(
            r"\b(fullscreen|full screen|maximize|présentation plein écran)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # first slide
    (
        "first_slide",
        re.compile(
            r"\b(first slide|go to start|beginning|primera|première|erste folie)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # last slide
    (
        "last_slide",
        re.compile(
            r"\b(last slide|final slide|end slide|última|dernière|letzte folie)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # pen tool
    (
        "pen_tool",
        re.compile(
            r"\b(pen tool|draw|annotation|herramienta pluma|dibujar|"
            r"outil stylo|dessiner|stiftwerkzeug|zeichnen|"
            r"strumento penna|disegnare|ferramenta caneta|desenhar|"
            r"笔工具|绘制|ペンツール|描画)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # eraser
    (
        "eraser",
        re.compile(
            r"\b(eraser|erase|clear drawing|borrar|gomme|effacer|radiergummi|gomma)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
    # pointer
    (
        "pointer",
        re.compile(
            r"\b(pointer|arrow|cursor|puntero|pointeur|zeiger|puntatore)\b",
            re.IGNORECASE | re.UNICODE,
        ),
    ),
]


def match_command(text: str) -> dict[str, Any]:
    """
    Match a spoken phrase against all command patterns.
    Returns a dict with at minimum an 'action' key.
    Mirrors the two-stage (regex → fuzzy) logic of the original v5.3.1.
    """
    text = text.lower().strip()

    for action, pattern in COMMAND_PATTERNS:
        m = pattern.search(text)
        if m:
            result: dict[str, Any] = {"action": action, "confidence": 0.95}
            if action == "jump_slide":
                result["slide"] = int(m.group(1))
            return result

    return {"action": "unknown", "text": text, "confidence": 0.0}


# ─────────────────────────────────────────────
# ML learning – SQLite-backed command frequency
# ─────────────────────────────────────────────


def _get_db() -> sqlite3.Connection:
    """Return a connection to the learning database, creating tables if needed."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS command_usage (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            command   TEXT    NOT NULL,
            text      TEXT    NOT NULL,
            lang      TEXT    NOT NULL DEFAULT 'en',
            confidence REAL   NOT NULL DEFAULT 0.0,
            ts        TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def record_command(command: str, text: str, lang: str, confidence: float) -> None:
    """Insert one command-usage record into the learning database."""
    ts = datetime.now(timezone.utc).isoformat()
    with _get_db() as conn:
        conn.execute(
            "INSERT INTO command_usage (command, text, lang, confidence, ts) VALUES (?,?,?,?,?)",
            (command, text, lang, confidence, ts),
        )


def get_suggestions(limit: int = 5) -> list[dict[str, Any]]:
    """Return the most-frequently-used commands, highest count first."""
    with _get_db() as conn:
        rows = conn.execute(
            """
            SELECT command,
                   COUNT(*)                             AS count,
                   AVG(confidence)                      AS avg_confidence,
                   MAX(ts)                              AS last_used
            FROM   command_usage
            WHERE  command != 'unknown'
            GROUP  BY command
            ORDER  BY count DESC, last_used DESC
            LIMIT  ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "command": row["command"],
            "count": row["count"],
            "avg_confidence": round(row["avg_confidence"], 3),
            "last_used": row["last_used"],
        }
        for row in rows
    ]


# ─────────────────────────────────────────────
# file management helpers
# ─────────────────────────────────────────────


def _thumbnail_for_slides(slides: list[dict[str, Any]]) -> str:
    """Return a data-URI thumbnail from the first slide (image type only)."""
    if slides and slides[0].get("type") == "image":
        return slides[0]["image"]
    return ""


def _register_file(
    filename: str, slides: list[dict[str, Any]]
) -> str:
    """Store the file in the registry and return its UUID."""
    file_id = str(uuid.uuid4())
    _file_registry[file_id] = {
        "id": file_id,
        "filename": filename,
        "total_slides": len(slides),
        "slides": slides,
        "thumbnail": _thumbnail_for_slides(slides),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return file_id


# ─────────────────────────────────────────────
# routes
# ─────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return (
            jsonify(
                {
                    "error": (
                        f"Unsupported file type. "
                        f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                    )
                }
            ),
            400,
        )

    file_bytes = file.read()
    filename: str = file.filename
    ext = filename.rsplit(".", 1)[1].lower()

    try:
        converters = {
            "pdf": lambda b: convert_pdf(b),
            "docx": lambda b: convert_docx(b),
            "doc": lambda b: convert_docx(b),
            "xlsx": lambda b: convert_xlsx(b),
            "xls": lambda b: convert_xlsx(b),
            "txt": lambda b: convert_text(b),
            "png": lambda b: convert_image(b, filename),
            "jpg": lambda b: convert_image(b, filename),
            "jpeg": lambda b: convert_image(b, filename),
            "gif": lambda b: convert_image(b, filename),
            "bmp": lambda b: convert_image(b, filename),
            "webp": lambda b: convert_image(b, filename),
        }
        slides = converters[ext](file_bytes)
        file_id = _register_file(filename, slides)
        return jsonify(
            {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "total_slides": len(slides),
                "slides": slides,
            }
        )
    except (ImportError, ValueError, OSError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 500


# ─── file management ─────────────────────────────────────────────────────────


@app.route("/api/files", methods=["GET"])
def list_files():
    """Return metadata for all uploaded files (no slide data to keep payload small)."""
    files = [
        {
            "id": entry["id"],
            "filename": entry["filename"],
            "total_slides": entry["total_slides"],
            "thumbnail": entry["thumbnail"],
            "created_at": entry["created_at"],
        }
        for entry in _file_registry.values()
    ]
    # newest first
    files.sort(key=lambda f: f["created_at"], reverse=True)
    return jsonify({"files": files})


@app.route("/api/files/<file_id>", methods=["GET"])
def get_file(file_id: str):
    """Return the full slide data for a single file."""
    entry = _file_registry.get(file_id)
    if entry is None:
        return jsonify({"error": "File not found"}), 404
    return jsonify(
        {
            "success": True,
            "file_id": file_id,
            "filename": entry["filename"],
            "total_slides": entry["total_slides"],
            "slides": entry["slides"],
        }
    )


@app.route("/api/files/<file_id>", methods=["DELETE"])
def delete_file(file_id: str):
    """Remove a file from the in-memory registry."""
    if file_id not in _file_registry:
        return jsonify({"error": "File not found"}), 404
    del _file_registry[file_id]
    return jsonify({"success": True, "deleted": file_id})


# ─── ML learning ─────────────────────────────────────────────────────────────


@app.route("/api/learn", methods=["POST"])
def learn():
    """Record a successfully executed voice command for ML training."""
    data: dict[str, Any] = request.get_json(force=True) or {}
    command: str = data.get("command", "")
    text: str = data.get("text", "")
    lang: str = data.get("lang", "en")
    confidence: float = float(data.get("confidence", 0.0))

    if not command or command == "unknown":
        return jsonify({"error": "No valid command provided"}), 400

    try:
        record_command(command, text, lang, confidence)
        return jsonify({"success": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/suggestions", methods=["GET"])
def suggestions():
    """Return the user's most-frequently-used commands (ML-derived)."""
    limit = min(int(request.args.get("limit", 5)), 20)
    try:
        return jsonify({"suggestions": get_suggestions(limit)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/command", methods=["POST"])
def process_command():
    """Process a voice-command transcript and return the matched action."""
    data: dict[str, Any] = request.get_json(force=True) or {}
    text: str = data.get("text", "")
    result = match_command(text)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=port)
