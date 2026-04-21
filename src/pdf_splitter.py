"""Core PDF splitting orchestration.

PyMuPDF handles page-number detection (text + coordinates);
pypdf handles the actual page extraction and writing.
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Callable

import fitz
from pypdf import PdfReader, PdfWriter

from src.filename_builder import build_filename
from src.page_detector import detect_page_number


class PdfSplitError(Exception):
    pass


ProgressCb = Callable[[int, int, str], None]


def _collect_filenames(pdf_path: str) -> list[str]:
    doc = fitz.open(pdf_path)
    try:
        names: list[str] = []
        for i, page in enumerate(doc, start=1):
            detected = detect_page_number(page)
            names.append(build_filename(i, detected))
        return _deduplicate(names)
    finally:
        doc.close()


def _deduplicate(names: list[str]) -> list[str]:
    """If two pages produce the same filename, append a suffix to later ones."""
    seen: Counter[str] = Counter()
    out: list[str] = []
    for name in names:
        if seen[name] == 0:
            out.append(name)
        else:
            base, ext = os.path.splitext(name)
            out.append(f"{base}_dup{seen[name]}{ext}")
        seen[name] += 1
    return out


def preview(pdf_path: str) -> list[tuple[int, str]]:
    """Dry-run: return [(1-based pdf page, filename), ...] without writing."""
    _validate_input(pdf_path)
    names = _collect_filenames(pdf_path)
    return [(i + 1, name) for i, name in enumerate(names)]


def split(
    pdf_path: str,
    output_dir: str,
    progress_cb: ProgressCb | None = None,
) -> list[str]:
    """Split the PDF into one file per page and return produced paths."""
    _validate_input(pdf_path)
    _validate_output_dir(output_dir)

    names = _collect_filenames(pdf_path)
    total = len(names)
    produced: list[str] = []

    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        raise PdfSplitError("PDF 已加密，請先解密後再試。")

    for idx, (page, name) in enumerate(zip(reader.pages, names), start=1):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = os.path.join(output_dir, name)
        with open(out_path, "wb") as f:
            writer.write(f)
        produced.append(os.path.abspath(out_path))
        if progress_cb:
            progress_cb(idx, total, name)

    return produced


def _validate_input(pdf_path: str) -> None:
    if not os.path.isfile(pdf_path):
        raise PdfSplitError(f"找不到 PDF 檔案：{pdf_path}")
    if not pdf_path.lower().endswith(".pdf"):
        raise PdfSplitError("輸入檔必須是 .pdf")


def _validate_output_dir(output_dir: str) -> None:
    if not os.path.isdir(output_dir):
        raise PdfSplitError(f"輸出資料夾不存在：{output_dir}")
    if not os.access(output_dir, os.W_OK):
        raise PdfSplitError(f"沒有寫入權限：{output_dir}")
