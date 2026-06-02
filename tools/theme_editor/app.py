"""
MP3 Player — Theme Editor
Flask web app that generates theme.json files for the Switch homebrew.

Run:
    pip install flask
    python app.py
Then open http://localhost:5000
"""

import json
import os
import shutil
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

ASSET_ALLOWED_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ttf', '.otf'}

app = Flask(__name__)

# Paths relative to this file
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
THEMES_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../romfs/themes"))

os.makedirs(THEMES_DIR, exist_ok=True)

# ─── Default theme values ───────────────────────────────────────────────────
DEFAULT_THEME = {
    "meta": {
        "name":    "My Theme",
        "author":  "YourName",
        "version": "1.0.0"
    },
    "colors": {
        # Main surfaces
        "background":    "#12121c",   # Full 1280×720 background tint (if no image)
        "panel_player":  "#202032",   # Left player panel  460×580
        "panel_playlist":"#202032",   # Right playlist panel 700×580
        "header":        "#1a1a2e",   # Header bar 1280×60
        "footer":        "#1a1a2e",   # Footer bar 1280×60

        # Accent / highlight
        "accent":        "#5aaaff",   # Borders, active elements
        "selected_row":  "#37477a",   # Currently selected playlist row bg
        "now_playing":   "#2870c8",   # Outline of currently playing row

        # Text
        "text_primary":  "#ffffff",   # Track name, headers
        "text_secondary":"#aaaacc",   # Artist, time stamps
        "text_hint":     "#666688",   # Footer button hints

        # Progress bar
        "progress_bg":   "#2d2d41",   # Track (full width)
        "progress_fill": "#5096ff",   # Filled portion

        # Buttons
        "btn_normal":    "#37375a",   # Prev / Next buttons bg
        "btn_primary":   "#5aaaff",   # Play/Pause button bg (active state)
        "btn_icon":      "#ffffff",   # Icon colour drawn on buttons

        # Misc
        "album_art_bg":  "#37375a",   # Default album-art placeholder bg
        "scrollbar_bg":  "#2d2d41",   # Scrollbar track
        "scrollbar_thumb":"#5aaaff"   # Scrollbar thumb
    },
    "assets": {
        # Set to "" to use the colour fallback.
        # Paths are relative to romfs/themes/<theme_name>/
        #
        # ── Backgrounds ────────────────────────────────────────────────────
        "background":          "",   # 1280×720 px  — full screen backdrop
        "header":              "",   # 1280×60  px  — top bar
        "footer":              "",   # 1280×60  px  — bottom bar with hints
        "panel_player":        "",   # 460×580  px  — left player card
        "panel_playlist":      "",   # 700×580  px  — right playlist card

        # ── Album art ──────────────────────────────────────────────────────
        "album_art_default":   "",   # 420×320  px  — shown when no embedded art

        # ── Progress bar ───────────────────────────────────────────────────
        "progress_bg":         "",   # 420×10   px  — bar track
        "progress_fill":       "",   # 1×10     px  — tiled/stretched fill

        # ── Control buttons ────────────────────────────────────────────────
        "btn_play":            "",   # 90×90    px  — play icon
        "btn_pause":           "",   # 90×90    px  — pause icon
        "btn_prev":            "",   # 70×70    px  — previous track
        "btn_next":            "",   # 70×70    px  — next track

        # ── Font ───────────────────────────────────────────────────────────
        "font_regular":        "",   # TTF file — track names (22 pt)
        "font_small":          ""    # TTF file — timestamps, hints (16 pt)
    }
}


def load_theme(name: str) -> dict:
    path = os.path.join(THEMES_DIR, name, "theme.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        # Fill missing keys from defaults (non-destructive)
        for section, values in DEFAULT_THEME.items():
            data.setdefault(section, {})
            for k, v in values.items():
                data[section].setdefault(k, v)
        return data
    return json.loads(json.dumps(DEFAULT_THEME))  # deep copy


def save_theme(name: str, data: dict) -> None:
    folder = os.path.join(THEMES_DIR, name)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "theme.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def list_themes() -> list[str]:
    themes = []
    if os.path.isdir(THEMES_DIR):
        for entry in sorted(os.listdir(THEMES_DIR)):
            if os.path.isfile(os.path.join(THEMES_DIR, entry, "theme.json")):
                themes.append(entry)
    return themes


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    themes = list_themes()
    current = request.args.get("theme", themes[0] if themes else "__new__")
    theme_data = load_theme(current) if current != "__new__" else json.loads(json.dumps(DEFAULT_THEME))
    return render_template(
        "editor.html",
        themes=themes,
        current=current,
        theme=theme_data,
        default=DEFAULT_THEME
    )


@app.route("/api/themes")
def api_themes():
    return jsonify(list_themes())


@app.route("/api/theme/<name>")
def api_get_theme(name):
    return jsonify(load_theme(name))


@app.route("/api/theme/<name>", methods=["POST"])
def api_save_theme(name):
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    save_theme(name, data)
    return jsonify({"ok": True, "saved": name})


@app.route("/api/theme/<name>/export")
def api_export_theme(name):
    path = os.path.join(THEMES_DIR, name, "theme.json")
    if not os.path.exists(path):
        return jsonify({"error": "Theme not found"}), 404
    return send_file(path, as_attachment=True, download_name=f"{name}_theme.json")


@app.route("/api/theme/<name>", methods=["DELETE"])
def api_delete_theme(name):
    folder = os.path.join(THEMES_DIR, name)
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    return jsonify({"ok": True})


@app.route("/api/theme/<name>/asset", methods=["POST"])
def api_upload_asset(name):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    f = request.files['file']
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    filename = secure_filename(f.filename)
    if not filename:
        return jsonify({"error": "Invalid filename"}), 400
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ASSET_ALLOWED_EXTS:
        return jsonify({"error": f"File type {ext} not allowed"}), 400
    real_themes = os.path.realpath(THEMES_DIR)
    real_folder = os.path.realpath(os.path.join(THEMES_DIR, name))
    if not real_folder.startswith(real_themes + os.sep):
        return jsonify({"error": "Invalid theme name"}), 400
    os.makedirs(real_folder, exist_ok=True)
    f.save(os.path.join(real_folder, filename))
    return jsonify({"ok": True, "filename": filename})


@app.route("/api/theme/<name>/asset/<path:filename>")
def api_get_asset(name, filename):
    real_themes = os.path.realpath(THEMES_DIR)
    real_folder = os.path.realpath(os.path.join(THEMES_DIR, name))
    if not real_folder.startswith(real_themes + os.sep):
        return jsonify({"error": "Invalid theme name"}), 400
    real_filepath = os.path.realpath(os.path.join(real_folder, filename))
    if not real_filepath.startswith(real_folder + os.sep):
        return jsonify({"error": "Invalid filename"}), 400
    if not os.path.isfile(real_filepath):
        return jsonify({"error": "Not found"}), 404
    return send_file(real_filepath)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
