import os
import re
import time
import hashlib
import logging
from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    send_from_directory,
    render_template,
    abort,
    Response,
    request,
)
from werkzeug.utils import secure_filename

DATA_FOLDER = os.environ.get("DATA_FOLDER", "/data")

main_bp = Blueprint("main", __name__)


# ================================
# Utilities
# ================================
def compute_sha256(filepath: str) -> str:
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def get_files_info() -> list[dict]:
    files = []
    try:
        for filename in os.listdir(DATA_FOLDER):
            filepath = os.path.join(DATA_FOLDER, filename)
            if os.path.isfile(filepath):
                try:
                    stat = os.stat(filepath)
                    files.append(
                        {
                            "name": filename,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                            "sha256": compute_sha256(filepath),
                        }
                    )
                except FileNotFoundError:
                    pass
    except FileNotFoundError:
        pass
    # Par défaut, fichiers triés par date descendante
    return sorted(files, key=lambda x: x["modified"], reverse=True)


# ================================
# Routes HTTP
# ================================
@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/api/files")
def api_files():
    return jsonify(get_files_info())


@main_bp.route("/download/<path:filename>")
def download_file(filename):
    if not re.fullmatch(r"[\w.\- ]+", filename):
        abort(400, description="Invalid file name")

    safe_filename = secure_filename(filename)
    file_path = os.path.join(DATA_FOLDER, safe_filename)

    if not os.path.isfile(file_path):
        abort(404, description="File not found or deleted")

    try:
        client_ip = request.remote_addr
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{now} - INFO - [X] Download {client_ip} : {safe_filename}"
        )  # seul affichage autorisé
        return send_from_directory(DATA_FOLDER, safe_filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error when downloading {safe_filename} from {client_ip}: {e}")
        abort(500, description="Server error while downloading")


# ================================
# Server-Sent Events (SSE)
# ================================
def event_stream():
    last_snapshot = {}

    while True:
        try:
            current_snapshot = {}
            for filename in os.listdir(DATA_FOLDER):
                filepath = os.path.join(DATA_FOLDER, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    current_snapshot[filename] = (stat.st_size, stat.st_mtime)

            if current_snapshot != last_snapshot:
                last_snapshot = current_snapshot
                yield "data: update\n\n"

        except Exception as e:
            logging.error(f"Error in SSE event_stream : {e}", exc_info=True)

        time.sleep(2)


@main_bp.route("/events")
def sse_stream():
    return Response(event_stream(), mimetype="text/event-stream")
