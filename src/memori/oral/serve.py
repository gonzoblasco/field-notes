"""Guarded server entry point.

``make run`` starts uvicorn with the default loopback host, but nothing stops
someone from passing ``--host 0.0.0.0``. This runner makes the bind an explicit
decision the code can refuse.
"""

from __future__ import annotations

import os
import sys

from .net import LocalOnlyViolation, assert_loopback_host


def _parse(argv: list[str]) -> tuple[str, int]:
    host = os.environ.get("FIELD_NOTES_HOST", "127.0.0.1")
    port = int(os.environ.get("FIELD_NOTES_PORT", "8100"))
    it = iter(argv)
    for arg in it:
        if arg in ("--host", "-h"):
            host = next(it, host)
        elif arg in ("--port", "-p"):
            port = int(next(it, port))
        elif arg.startswith("--host="):
            host = arg.split("=", 1)[1]
        elif arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
    return host, port


def main(argv: list[str] | None = None) -> int:
    host, port = _parse(list(sys.argv[1:] if argv is None else argv))
    try:
        assert_loopback_host(host)
    except LocalOnlyViolation as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    import uvicorn

    uvicorn.run(os.environ.get("FIELD_NOTES_APP", "memori.oral.ui:app"), host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
