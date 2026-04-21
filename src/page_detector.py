"""Detect a book-page-number string at the bottom of a PDF page."""

from __future__ import annotations

import re
from dataclasses import dataclass

import fitz  # PyMuPDF

# Only spans whose y0 >= height * BOTTOM_BAND_THRESHOLD are considered.
# Real page numbers almost always sit in the very bottom strip; keeping the
# band narrow suppresses TOC entries, footer notes and text inside boxes.
BOTTOM_BAND_THRESHOLD = 0.93

MAX_LEN = 15

# Tokens that, if present on the same line as a number candidate, strongly
# suggest the number is a price, barcode, phone, etc. — not a page number.
LINE_REJECT_TOKENS: tuple[str, ...] = (
    "$", "NT", "US", "USD", "售價", "定價", "建議", "ISBN", "Tel", "電話", "傳真",
    "專線", "©",
)

# Patterns ordered by preference. When multiple candidates exist on the
# same page, ones matching an earlier (higher-priority) pattern win.
PATTERNS: tuple[re.Pattern[str], ...] = (
    # Chapter-style book pages: "1-4", "12-3" (very common in Taiwanese tech books)
    re.compile(r"^\d+-\d+$"),
    # Alphabetic / Chinese chapter codes: "A-3", "D-11", "附錄-5"
    re.compile(r"^[A-Za-z]+-\d+$"),
    re.compile(r"^[一-鿿]+-\d+$"),
    # Plain arabic numerals: "1" .. "9999"
    re.compile(r"^\d{1,4}$"),
    # Lowercase roman numerals for front matter: "i", "iii", "xii"
    re.compile(r"^[ivxlcdm]{1,8}$"),
    # Three-level hierarchical "1.2.3" only — two-level "1.2" is too ambiguous
    # (e.g. ISBN classification "312.83" would match and cause false positives).
    re.compile(r"^\d+\.\d+\.\d+$"),
)

_TRIM_CHARS = " \t\r\n·•‧．。,，;；:：()[]{}<>\"'"


@dataclass
class _Candidate:
    text: str
    y1: float
    priority: int  # lower = higher priority (index into PATTERNS)


def _clean(text: str) -> str:
    return text.strip().strip(_TRIM_CHARS).strip()


def _match_priority(text: str) -> int | None:
    """Return pattern index if matched, else None."""
    for i, p in enumerate(PATTERNS):
        if p.match(text):
            return i
    return None


def _line_is_rejected(line: dict) -> bool:
    """True if the line contains a token that disqualifies it (price, phone, etc.)."""
    joined = "".join(span.get("text", "") for span in line.get("spans", []))
    return any(tok in joined for tok in LINE_REJECT_TOKENS)


def detect_page_number(page: fitz.Page) -> str | None:
    """Return the detected book page string (e.g. '20', '1-4', 'D-11') or None."""
    height = page.rect.height
    y_threshold = height * BOTTOM_BAND_THRESHOLD

    data = page.get_text("dict")
    candidates: list[_Candidate] = []

    for block in data.get("blocks", []):
        for line in block.get("lines", []):
            if _line_is_rejected(line):
                continue
            for span in line.get("spans", []):
                bbox = span.get("bbox")
                if not bbox:
                    continue
                y0, y1 = bbox[1], bbox[3]
                if y0 < y_threshold:
                    continue
                text = _clean(span.get("text", ""))
                if not text or len(text) > MAX_LEN:
                    continue
                priority = _match_priority(text)
                if priority is not None:
                    candidates.append(_Candidate(text=text, y1=y1, priority=priority))

    if not candidates:
        return None

    # Prefer the bottom-most candidate (where real page numbers live);
    # break ties by pattern priority.
    candidates.sort(key=lambda c: (-c.y1, c.priority))
    return candidates[0].text
