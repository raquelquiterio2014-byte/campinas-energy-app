"""End-to-end HTTP test including stopping and restarting the FastAPI process.

Run with 'python verify_restart.py' inside ERA-Energy-App in conda era-gis.
Uses temporary synthetic files; does not read operational GeoPackages.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from make_demo_data import create

HERE = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:18765"

def request(path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    method = "POST" if body else "GET"
    req = urllib.request.Request(BASE + path, data=body, method=method)
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = response.read()
            return response.status, json.loads(data) if "json" in response.headers.get("Content-Type", "") else data
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())

def start(env):
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app_server:app", "--host", "127.0.0.1", "--port", "18765"],
        cwd=HERE, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    for _ in range(70):
        if proc.poll() is not None:
            raise RuntimeError("Uvicorn exited during startup")
        try:
            if request("/health")[0] == 200:
                return proc
        except (OSError, TimeoutError):
            time.sleep(.2)
    proc.terminate()
    raise RuntimeError("Uvicorn did not become healthy")

def stop(proc):
    if proc is None: return
    proc.terminate()
    try: proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=8)

def main():
    with tempfile.TemporaryDirectory(prefix="era-app-synthetic-") as tmp:
        gpkg = Path(tmp) / "synthetic.gpkg"
        db = Path(tmp) / "studies.db"
        create(gpkg)
        env = dict(os.environ, ERA_GPKG_PATH=str(gpkg), ERA_STUDIES_DB_PATH=str(db))
        proc = None
        try:
            proc = start(env)
            assert request("/app/")[0] == 200
            assert request("/alimentadores/SYN-A/ssdmt")[0] == 200
            point = {"longitude": -47.052, "latitude": -22.913}
            code = "/alimentadores/SYN-A/studies/RESTART-001"
            assert request("/alimentadores/SYN-A/connection", point)[0] == 200
            status, saved = request(code, point)
            assert status == 201, (status, saved)
            assert request(code, point)[0] == 409
            stop(proc)
            proc = None
            proc = start(env)
            status, restored = request(code)
            assert status == 200, (status, restored)
            assert restored["selected_point"] == saved["selected_point"]
            assert restored["connection_line"] == saved["connection_line"]
            assert request("/alimentadores/SYN-A/studies")[0] == 200
            print("PASS: synthetic map API, connection, SQLite save, duplicate rejection, server restart and geometry restore")
        finally:
            stop(proc)

if __name__ == "__main__":
    main()
