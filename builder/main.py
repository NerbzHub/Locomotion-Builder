"""Locomotion Builder command-line entrypoint."""

from __future__ import annotations

from collections.abc import Sequence

from builder.application.app import Application


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the command-line application and return an exit status."""
    return Application().run(arguments)



if __name__ == "__main__":
    raise SystemExit(main())
