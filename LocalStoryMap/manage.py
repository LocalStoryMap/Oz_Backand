#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # 환경변수가 설정돼 있으면 그 값을, 없으면 dev를 기본값으로 사용
    os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
        "DJANGO_SETTINGS_MODULE",
        "config.settings.dev",
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
