#!/usr/bin/env python3
"""Private, dependency-free Music Foundry render API.

Health is public for Railway. Every project/audio endpoint requires a bearer token.
Rendered files and job state live under MUSIC_FOUNDRY_DATA (mount a persistent volume).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import uuid
import wave
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("MUSIC_FOUNDRY_DATA", "/data/music-foundry")).resolve()
PROJECTS = DATA / "projects"
JOBS = DATA / "jobs"
TOKEN = os.environ.get("MUSIC_FOUNDRY_API_TOKEN", "")
PORT = int(os.environ.get("PORT", "8080"))
MAX_BODY = 16_384
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
FILENAME = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,100}\\.(wav|json)$")
LOCK = threading.Lock()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_job(job_id):
    path = JOBS / (job_id + ".json")
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def write_job(job):
    JOBS.mkdir(parents=True, exist_ok=True)
    path = JOBS / (job["id"] + ".json")
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(job, indent=2))
    tmp.replace(path)


def valid_audio(path):
    with wave.open(str(path), "rb") as audio:
        return {
            "bytes": path.stat().st_size,
            "channels": audio.getnchannels(),
            "sample_rate": audio.getframerate(),
            "sample_width_bytes": audio.getsampwidth(),
            "frames": audio.getnframes(),
            "duration_seconds": round(audio.getnframes() / audio.getframerate(), 3),
        }


def render_job(job):
    try:
        project_dir = PROJECTS / job["project"]
        output = project_dir / job["id"]
        output.mkdir(parents=True, exist_ok=True)
        if job["arrangement"] == "warehouse-rave-v3":
            script = ROOT / "render_warehouse_rave_v3.py"
        else:
            script = ROOT / "render_instrumental.py"
        command = [
            os.environ.get("PYTHON", "python3"), str(script),
            "--output", str(output), "--bpm", str(job["bpm"]),
        ]
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=900)
        if completed.returncode:
            raise RuntimeError((completed.stderr or completed.stdout)[-5000:])
        manifest_path = output / "audio_manifest.json"
        if not manifest_path.is_file():
            raise RuntimeError("Renderer completed without audio_manifest.json")
        manifest = json.loads(manifest_path.read_text())
        mix_name = manifest.get("mix", "instrumental_mix.wav")
        mix_path = output / mix_name
        if not mix_path.is_file() or mix_path.stat().st_size < 4096:
            raise RuntimeError("Rendered mix is missing or too small to be valid audio")
        audio = valid_audio(mix_path)
        if audio["duration_seconds"] < 10 or audio["frames"] <= 0:
            raise RuntimeError("Rendered mix failed duration validation")
        files = {}
        for item in output.iterdir():
            if item.is_file() and item.suffix in (".wav", ".json"):
                files[item.name] = {"bytes": item.stat().st_size}
                if item.suffix == ".wav":
                    files[item.name].update(valid_audio(item))
        job.update({
            "status": "succeeded", "completed_at": utc_now(),
            "output_dir": str(output.relative_to(DATA)),
            "manifest": manifest, "audio_validation": audio, "files": files,
            "message": "Instrumental render complete. Vocals are not included in this render.",
        })
    except Exception as exc:
        job.update({"status": "failed", "completed_at": utc_now(), "error": str(exc)[:5000]})
    write_job(job)


def json_response(handler, status, payload):
    raw = json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(raw)


class Handler(BaseHTTPRequestHandler):
    server_version = "MusicFoundry/1.0"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", os.environ.get("MUSIC_FOUNDRY_ALLOWED_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def end_headers(self):
        self._cors()
        super().end_headers()

    def authorized(self):
        if not TOKEN:
            json_response(self, 503, {"error": "MUSIC_FOUNDRY_API_TOKEN is not configured"})
            return False
        supplied = self.headers.get("Authorization", "")
        if supplied != "Bearer " + TOKEN:
            json_response(self, 401, {"error": "Unauthorized"})
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/app"):
            page = ROOT / "service" / "index.html"
            if not page.is_file():
                json_response(self, 404, {"error": "App not found"})
                return
            raw = page.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)
            return
        if path == "/health":
            json_response(self, 200, {"ok": True, "service": "music-foundry", "renderer": "offline-procedural-v1"})
            return
        if not self.authorized():
            return
        if path == "/api/v1/projects":
            json_response(self, 200, {"projects": [{"id": "somebodys-gotta-do-it", "title": "Somebody's Gotta Do It", "arrangements": ["warehouse-rave-v3", "original"]}]})
            return
        match = re.fullmatch(r"/api/v1/jobs/([0-9a-f-]{36})", path)
        if match:
            job = read_job(match.group(1))
            json_response(self, 200 if job else 404, job or {"error": "Job not found"})
            return
        match = re.fullmatch(r"/api/v1/jobs/([0-9a-f-]{36})/files/([a-zA-Z0-9_.-]+)", path)
        if match:
            job = read_job(match.group(1))
            name = match.group(2)
            if not job or job.get("status") != "succeeded" or not FILENAME.fullmatch(name):
                json_response(self, 404, {"error": "File not found"})
                return
            file_path = (DATA / job["output_dir"] / name).resolve()
            if not file_path.is_relative_to(DATA) or not file_path.is_file():
                json_response(self, 404, {"error": "File not found"})
                return
            content_type = "audio/wav" if file_path.suffix == ".wav" else "application/json"
            size = file_path.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", 'attachment; filename="' + name + '"')
            self.send_header("Cache-Control", "private, no-store")
            self.end_headers()
            with file_path.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    self.wfile.write(chunk)
            return
        json_response(self, 404, {"error": "Not found"})

    def do_POST(self):
        if not self.authorized():
            return
        if urlparse(self.path).path != "/api/v1/render":
            json_response(self, 404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("Request body must be between 1 and 16384 bytes")
            payload = json.loads(self.rfile.read(length))
            project = payload.get("project", "somebodys-gotta-do-it")
            arrangement = payload.get("arrangement", "warehouse-rave-v3")
            bpm = int(payload.get("bpm", 127))
            if project != "somebodys-gotta-do-it" or not SLUG.fullmatch(project):
                raise ValueError("Unknown project")
            if arrangement not in ("warehouse-rave-v3", "original"):
                raise ValueError("Unknown arrangement")
            if not 40 <= bpm <= 240:
                raise ValueError("BPM must be between 40 and 240")
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            json_response(self, 400, {"error": str(exc)})
            return
        job = {
            "id": str(uuid.uuid4()), "project": project, "arrangement": arrangement,
            "bpm": bpm, "status": "queued", "created_at": utc_now(),
        }
        write_job(job)
        thread = threading.Thread(target=render_job, args=(job,), daemon=True)
        thread.start()
        json_response(self, 202, {"job_id": job["id"], "status": "queued", "status_url": "/api/v1/jobs/" + job["id"]})


if __name__ == "__main__":
    DATA.mkdir(parents=True, exist_ok=True)
    PROJECTS.mkdir(parents=True, exist_ok=True)
    JOBS.mkdir(parents=True, exist_ok=True)
    print("Music Foundry API listening on port %d; persistent data at %s" % (PORT, DATA), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
