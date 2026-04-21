import pytest

from src.filename_builder import build_filename, sanitize


def test_arabic_page_number():
    assert build_filename(21, "20") == "021_Page_20.pdf"


def test_chapter_code():
    assert build_filename(410, "D-11") == "410_Page_D-11.pdf"


def test_roman_lower():
    assert build_filename(5, "iii") == "005_Page_iii.pdf"


def test_hierarchical():
    assert build_filename(42, "1.2.3") == "042_Page_1.2.3.pdf"


def test_chinese_chapter():
    assert build_filename(400, "附錄-5") == "400_Page_附錄-5.pdf"


def test_none_detected():
    assert build_filename(1, None) == "001.pdf"


def test_empty_string_detected():
    assert build_filename(1, "") == "001.pdf"


def test_unsafe_chars_are_replaced():
    assert sanitize("A/B") == "A_B"
    assert sanitize('x:y*z?"<>|\\q') == "x_y_z______q"


def test_prefix_zero_padded_three_digits():
    assert build_filename(7, None) == "007.pdf"
    assert build_filename(1000, None) == "1000.pdf"  # 超過 3 位數仍保留原值


def test_invalid_page_num_raises():
    with pytest.raises(ValueError):
        build_filename(0, None)
