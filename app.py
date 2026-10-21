#!/usr/bin/env python3
"""Entry point for running the InfiniAI Django application on port 3000."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_dependencies():
    try:
        import django  # noqa: F401
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            import urllib.request

            get_pip_path = "/tmp/get-pip.py"
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip_path)
            subprocess.check_call([sys.executable, get_pip_path, "-q"])

        req_file = Path(__file__).resolve().parent / "requirements.txt"
        if req_file.exists():
            cmd = [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)]
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                subprocess.check_call([*cmd, "--break-system-packages"])


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("DEFAULT_APP_PORT", "3000")),
    )
    args, _ = parser.parse_known_args()

    ensure_dependencies()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    import django
    from django.core.management import call_command

    django.setup()

    # Ensure database schema, production seed data, and static assets are ready before serving
    call_command("migrate", interactive=False, verbosity=1)
    call_command("seed_orbit_production")
    call_command("collectstatic", interactive=False, verbosity=0)

    bind_address = f"{args.host}:{args.port}"
    gunicorn_bin = shutil.which("gunicorn")
    if gunicorn_bin:
        workers = os.getenv("GUNICORN_WORKERS", "2")
        timeout = os.getenv("GUNICORN_TIMEOUT", "300")
        log_level = os.getenv("GUNICORN_LOG_LEVEL", "info")
        os.execv(
            gunicorn_bin,
            [
                gunicorn_bin,
                "core.wsgi:application",
                "--bind",
                bind_address,
                "--workers",
                workers,
                "--timeout",
                timeout,
                "--log-level",
                log_level,
                "--access-logfile",
                "-",
                "--error-logfile",
                "-",
            ],
        )
    else:
        from django.core.management import execute_from_command_line

        execute_from_command_line(
            [sys.argv[0], "runserver", bind_address, "--noreload", "--insecure"]
        )


if __name__ == "__main__":
    main()
