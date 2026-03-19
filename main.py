"""Project entrypoint for running backend or frontend servers."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import uvicorn


def parse_args() -> argparse.Namespace:
    """Parse command-line options for app mode and networking."""
    parser = argparse.ArgumentParser(description="Run burn unit backend or frontend.")
    parser.add_argument(
        "--mode",
        choices=["backend", "frontend"],
        default="backend",
        help="Select which app to run.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind server to.")
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for selected mode (backend default 8000, frontend default 8501).",
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000",
        help="Backend API base URL used by frontend mode.",
    )
    return parser.parse_args()


def run_backend(host: str, port: int) -> None:
    """Start the FastAPI backend server."""
    uvicorn.run("backend.app:app", host=host, port=port, reload=False)


def run_frontend(host: str, port: int, api_url: str) -> None:
    """Start the Streamlit frontend server."""
    app_path = Path(__file__).resolve().parent / "frontend" / "app.py"
    env = os.environ.copy()
    env["BURN_API_URL"] = api_url

    command = [
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        host,
        "--server.port",
        str(port),
    ]
    subprocess.run(command, check=True, env=env)


def main() -> None:
    """Start the selected server mode."""
    args = parse_args()
    if args.mode == "backend":
        run_backend(host=args.host, port=args.port or 8000)
        return

    try:
        run_frontend(host=args.host, port=args.port or 8501, api_url=args.api_url)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
    except FileNotFoundError as exc:
        raise SystemExit(
            "Streamlit command not found. Install dependencies with `uv sync` or `uv add streamlit`."
        ) from exc


if __name__ == "__main__":
    sys.exit(main())
