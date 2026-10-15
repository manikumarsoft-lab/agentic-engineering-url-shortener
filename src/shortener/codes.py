"""Random, non-sequential short codes (CSPRNG base62).

Satisfies: FR-SHR-005, FR-SHR-006, A-003.
"""
from __future__ import annotations

import re
import secrets
import string

ALPHABET = string.ascii_letters + string.digits
CODE_PATTERN = re.compile(r"^[A-Za-z0-9]{4,10}$")


def generate(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
