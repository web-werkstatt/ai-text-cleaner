"""Stdin-Loader."""

from __future__ import annotations

import sys


def read_stdin() -> str:
    return sys.stdin.read()
