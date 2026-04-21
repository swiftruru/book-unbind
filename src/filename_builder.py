"""Build output filenames for split PDF pages."""

from __future__ import annotations

import re

_UNSAFE_CHARS = re.compile(r'[/\\:*?"<>|]')


def sanitize(detected: str) -> str:
    return _UNSAFE_CHARS.sub("_", detected).strip()


def build_filename(original_page_num: int, detected: str | None) -> str:
    """Compose the output filename for a single page.

    original_page_num is 1-based. `detected` is the book page string
    returned by page_detector, or None when nothing was found.
    """
    if original_page_num < 1:
        raise ValueError("original_page_num must be >= 1")

    prefix = f"{original_page_num:03d}"
    if detected:
        cleaned = sanitize(detected)
        if cleaned:
            return f"{prefix}_Page_{cleaned}.pdf"
    return f"{prefix}.pdf"
