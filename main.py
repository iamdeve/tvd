from flask import Flask, request, jsonify
from flask import send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)


@app.route("/")
def index():
    return "yt-dlp Twitter API is running!"


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    filename = f"/tmp/video_{os.urandom(4).hex()}.mp4"

    ydl_opts = {
        "format": "best",  # <--- simplified
        "outtmpl": filename,
        "quiet": True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(filename,
                         mimetype="video/mp4",
                         as_attachment=True,
                         download_name="twitter_video.mp4")
    except Exception as e:
        return jsonify({"error": str(e), "success": False})


@app.route("/get-download-url", methods=["POST"])
def get_video_url():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL", "success": False}), 400

    try:
        with YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        if isinstance(info, dict):
            # Option 1: info has direct URL
            if "url" in info:
                return jsonify({
                    "video_url": info["url"],
                    "success": True
                })

            # Option 2: Search for best format
            if "formats" in info and isinstance(info["formats"], list):
                best = max(
                    info["formats"],
                    key=lambda f: f.get("filesize", 0) if isinstance(f, dict) else 0
                )
                return jsonify({
                    "video_url": best["url"],
                    "format_note": best.get("format_note", ""),
                    "success": True
                })

        return jsonify({"error": "No valid video info found", "success": False}), 500

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
