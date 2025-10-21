#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import time


def _should_wait_for_database(argv: list[str]) -> bool:
    if os.getenv("SKIP_DB_WAIT", "").lower() in {"1", "true", "yes"}:
        return False

    if len(argv) <= 1:
        return False

    command = argv[1]
    commands_requiring_db = {
        "migrate",
        "makemigrations",
        "shell",
        "dbshell",
        "runserver",
        "test",
    }

    return command in commands_requiring_db


def _wait_for_database(argv: list[str]) -> None:
    if not _should_wait_for_database(argv):
        return

    import django
    from django.db import OperationalError, connections

    django.setup()

    max_attempts = int(os.getenv("DATABASE_WAIT_ATTEMPTS", "6"))
    sleep_seconds = float(os.getenv("DATABASE_WAIT_INTERVAL", "5"))

    last_error: OperationalError | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            with connections["default"].cursor():
                return
        except OperationalError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            time.sleep(sleep_seconds)

    if last_error is not None:
        raise last_error


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    _wait_for_database(sys.argv)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
