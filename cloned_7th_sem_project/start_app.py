"""
start_app.py
Unified runner for the Smart Flood Risk Prediction & Disaster Command Center.
Launches the FastAPI backend and Vite React frontend concurrently.
"""

import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(root_dir, "7thsem_group_project")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 60)
    print("🌊 Starting FloodSense AI (React Framework + FastAPI Backend)")
    print("=" * 60)

    # 1. Start FastAPI Backend
    print("[1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=project_dir
    )

    # Give backend a moment to spin up
    time.sleep(2)

    # 2. Start Vite React Frontend
    print("[2/2] Launching React Vite Frontend on http://localhost:5173 ...")
    shell_cmd = "npm run dev"
    frontend_proc = subprocess.Popen(
        shell_cmd,
        cwd=frontend_dir,
        shell=True
    )

    print("\n✅ System active!")
    print("👉 Open your browser at: http://localhost:5173")
    print("👉 FastAPI Interactive Docs at: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to shut down both servers.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
