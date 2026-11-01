import argparse
import subprocess
import sys
import time

def run_backend():
    print("Starting MultiAI FastAPI backend on http://127.0.0.1:8000...")
    return subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])

def run_frontend():
    print("Starting MultiAI Streamlit frontend on http://localhost:8501...")
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])

def main():
    parser = argparse.ArgumentParser(description="MultiAI Service Runner")
    parser.add_argument("service", nargs="?", default="all", choices=["backend", "frontend", "all"], help="Service to run (backend, frontend, or all)")
    args = parser.parse_args()

    processes = []
    try:
        if args.service in ("backend", "all"):
            p_backend = run_backend()
            processes.append(p_backend)
            time.sleep(1)

        if args.service in ("frontend", "all"):
            p_frontend = run_frontend()
            processes.append(p_frontend)

        print("\nMultiAI is running! Press Ctrl+C to terminate.")
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\nShutting down MultiAI services...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()
