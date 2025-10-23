#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line, call_command
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Run wait_for_db before executing any management command to avoid
    # transient DB connectivity issues (e.g., Supabase SSL close during deploy).
    try:
        # Only attempt wait_for_db when a DB-backed command is likely.
        # We still call it safely for all commands; the command will return quickly
        # if DB is already available.
        call_command('wait_for_db')
    except Exception:
        # If wait_for_db fails, log to stderr but continue so that commands like
        # 'makemigrations' or 'collectstatic' can still run in offline scenarios.
        import traceback as _tb
        sys.stderr.write('Warning: wait_for_db failed or timed out:\n')
        sys.stderr.write(_tb.format_exc())

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
