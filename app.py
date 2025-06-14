from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    filename = f"video_{os.urandom(6).hex()}.mp4"
    output_path = f"/tmp/{filename}"

    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"success": True, "path": output_path})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "yt-dlp Twitter API running"
