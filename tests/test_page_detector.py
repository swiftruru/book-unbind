"""Page detector tests.

We build small PDFs in-memory via PyMuPDF so no binary fixtures are needed.
Text is placed explicitly at the bottom of the page to exercise the
bottom-band heuristic.
"""

from __future__ import annotations

import fitz
import pytest

from src.page_detector import detect_page_number

PAGE_W, PAGE_H = 400, 600
BOTTOM_Y = PAGE_H - 30  # well within the bottom 15%
TOP_Y = 50  # well within the top band; should be ignored


def _make_page(texts_with_pos: list[tuple[str, float, float]]) -> fitz.Page:
    doc = fitz.open()
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    for text, x, y in texts_with_pos:
        # china-t is a PyMuPDF built-in CJK font; safe for ASCII too.
        page.insert_text((x, y), text, fontsize=12, fontname="china-t")
    return page


@pytest.mark.parametrize(
    "footer,expected",
    [
        ("20", "20"),
        ("410", "410"),
        ("iii", "iii"),
        ("D-11", "D-11"),
        ("A-3", "A-3"),
        ("1-4", "1-4"),
        ("12-3", "12-3"),
        ("1.2.3", "1.2.3"),
        ("附錄-5", "附錄-5"),
    ],
)
def test_detects_valid_footer(footer, expected):
    page = _make_page([(footer, PAGE_W / 2, BOTTOM_Y)])
    assert detect_page_number(page) == expected


def test_rejects_two_level_hierarchical_number():
    # ISBN classification numbers like 312.83 should NOT be treated as page numbers.
    page = _make_page([("312.83", PAGE_W / 2, BOTTOM_Y)])
    assert detect_page_number(page) is None


def test_rejects_uppercase_roman_ambiguous():
    # Uppercase letters combinations like "DLI" would falsely match old uppercase-roman pattern.
    page = _make_page([("DLI", PAGE_W / 2, BOTTOM_Y)])
    assert detect_page_number(page) is None


def test_chapter_page_preferred_over_plain_number():
    # If both "1-4" and "25" appear in the footer band, prefer the chapter-style.
    page = _make_page([("25", PAGE_W / 2, BOTTOM_Y), ("1-4", 50, BOTTOM_Y)])
    assert detect_page_number(page) == "1-4"


def test_blank_page_returns_none():
    page = _make_page([])
    assert detect_page_number(page) is None


def test_top_text_ignored():
    page = _make_page([("42", 50, TOP_Y)])
    assert detect_page_number(page) is None


def test_picks_bottom_most_candidate():
    # Two valid candidates at bottom; the one with larger y wins.
    page = _make_page([("iii", 50, BOTTOM_Y - 40), ("20", 50, BOTTOM_Y)])
    assert detect_page_number(page) == "20"


def test_ignores_long_footer_note():
    page = _make_page([("This is a footnote that is too long", 50, BOTTOM_Y)])
    assert detect_page_number(page) is None


def test_ignores_plain_english_word():
    page = _make_page([("Chapter", 50, BOTTOM_Y)])
    assert detect_page_number(page) is None
