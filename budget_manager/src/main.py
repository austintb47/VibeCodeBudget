from __future__ import annotations

import sys

from .cli import run_cli


def main() -> None:
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
