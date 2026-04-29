import os

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from services.search_service import (
    MAX_FILE_SIZE_BYTES,
    MAX_TEXT_LENGTH,
    get_algorithm_metadata,
    run_all,
    run_search,
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_BYTES

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/algorithms", methods=["GET"])
def list_algorithms():
    return jsonify(get_algorithm_metadata())


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "files" not in request.files:
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist("files")
    uploaded = []

    for file in files:
        if not file.filename:
            continue
        if file.filename.endswith(".txt"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            uploaded.append({"filename": filename, "content": content, "size": len(content)})

    if not uploaded:
        return jsonify({"error": "No valid .txt files uploaded"}), 400

    return jsonify({"files": uploaded})


@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    text = data.get("text", "")
    pattern = data.get("pattern", "")
    algorithm_id = data.get("algorithm", "naive")
    all_algorithms = data.get("all_algorithms", False)

    if not text or not pattern:
        return jsonify({"error": "Text and pattern are required"}), 400

    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"Text too large (max {MAX_TEXT_LENGTH:,} characters)"}), 400

    if all_algorithms:
        results = run_all(text, pattern)
        return jsonify({"results": results, "mode": "compare"})

    result = run_search(text, pattern, algorithm_id)
    if result is None:
        return jsonify({"error": f"Unknown algorithm: {algorithm_id}"}), 400

    return jsonify({"result": result, "mode": "single"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
