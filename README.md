<div align="center">

**English** &nbsp;·&nbsp; [**繁體中文**](README.zh-TW.md)

# 📖 BookUnbind

### PDF e-book "unbinding" tool

Split a whole PDF e-book into one-file-per-page, automatically detecting the book's own page numbers and turning them into meaningful filenames.
Native cross-platform desktop app: macOS / Windows / Linux.

[![Build](https://img.shields.io/github/actions/workflow/status/swiftruru/book-unbind/release.yml?label=build&logo=githubactions&logoColor=white&style=flat-square)](https://github.com/swiftruru/book-unbind/actions/workflows/release.yml)
[![Release](https://img.shields.io/github/v/release/swiftruru/book-unbind?label=release&logo=github&color=orange&style=flat-square)](https://github.com/swiftruru/book-unbind/releases/latest)
[![License](https://img.shields.io/github/license/swiftruru/book-unbind?color=blue&style=flat-square)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey?style=flat-square)](#-download)
[![Downloads](https://img.shields.io/github/downloads/swiftruru/book-unbind/total?logo=github&color=brightgreen&style=flat-square)](https://github.com/swiftruru/book-unbind/releases)

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white&style=flat-square)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.84-02569B?logo=flutter&logoColor=white&style=flat-square)](https://flet.dev/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24-4B8BBE?style=flat-square)](https://pymupdf.readthedocs.io/)
[![pypdf](https://img.shields.io/badge/pypdf-4.0-4B8BBE?style=flat-square)](https://pypdf.readthedocs.io/)

<img src="assets/icon.png" alt="BookUnbind icon" width="180" />

---

## 📦 Download

Pre-built binaries are published on every tagged release. Pick your platform below:

[![macOS Apple Silicon](https://img.shields.io/badge/DOWNLOAD-MACOS%20APPLE%20SILICON-000?logo=apple&logoColor=white&style=for-the-badge)](https://github.com/swiftruru/book-unbind/releases/latest/download/BookUnbind-macos.zip)
[![Windows Installer](https://img.shields.io/badge/DOWNLOAD-WINDOWS%20INSTALLER-0078D6?logo=windows&logoColor=white&style=for-the-badge)](https://github.com/swiftruru/book-unbind/releases/latest)
[![Windows Portable](https://img.shields.io/badge/DOWNLOAD-WINDOWS%20PORTABLE-0078D6?logo=windows&logoColor=white&style=for-the-badge)](https://github.com/swiftruru/book-unbind/releases/latest/download/BookUnbind-windows.zip)
[![Linux Tarball](https://img.shields.io/badge/DOWNLOAD-LINUX%20TARBALL-FCC624?logo=linux&logoColor=black&style=for-the-badge)](https://github.com/swiftruru/book-unbind/releases/latest/download/BookUnbind-linux.tar.gz)

👉 Older versions are at [Releases](https://github.com/swiftruru/book-unbind/releases).

</div>

> ### ⚠️ Heads-up for Windows users
>
> **We recommend the `BookUnbind-Setup-*.exe` installer.** It installs to `%LocalAppData%\Programs\BookUnbind\` without admin rights and creates a Start Menu shortcut.
>
> If you prefer the **portable build (`BookUnbind-windows.zip`)**, extract it onto a **real local drive** (e.g. `C:\Apps\` or `C:\Users\<you>\Documents\`) before launching.
>
> **Do not** run `BookUnbind.exe` directly from:
>
> - Parallels Desktop / VMware Fusion shared Mac folders (paths starting with `C:\Mac\` or `\\Mac\`)
> - Any SMB / UNC network share (`\\server\share\...`, mapped network drives like `Z:\`, …)
>
> You will see the app window open and stay blank. **Why:** Flet's embedded Python runtime cannot load `data\flutter_assets\app\app.zip` from those virtual file systems, so the Flutter shell starts but the Python side never initializes. This is a limitation of the VM integration layer, not a BookUnbind bug.

---

## ✨ Features

- 🔍 **Automatic page-number detection** — Arabic, Roman, chapter-style `1-4` / `D-11` / `附錄-5`, hierarchical `1.2.3`
- 👁 **Dry-run preview** — list every generated filename before touching disk
- 📁 **Auto output folder** — defaults to `{pdf_dir}/{stem}_unbind`, easily overridable
- ⚠️ **Overwrite confirmation** — warns if the output folder already contains files
- 🌙 **Dark-mode UI** — Flet + Material Design
- ⚡ **Truly native** — packaged builds ship without the user needing to install Python
- 🎨 **Custom app icon** — shows your icon even in dev mode (not the default Flet runner icon)
- 🤖 **Cross-platform CI** — push a `v*` tag → GitHub Actions builds macOS / Windows / Linux

## 🧾 Filename format

| Book page | Detected | Filename |
|---|---|---|
| 21 | `20` | `021_Page_20.pdf` |
| 25 | `1-4` | `025_Page_1-4.pdf` |
| 410 | `D-11` | `410_Page_D-11.pdf` |
| 5 | `iii` | `005_Page_iii.pdf` |
| 1 | — (cover) | `001.pdf` |

## 🛠 How to use

1. Download the build for your platform, install, and launch BookUnbind.
2. Click the "Select PDF" card and pick the e-book you want to split.
3. The output folder is pre-filled as `{pdf_stem}_unbind`; hit "Change" to redirect it.
4. Click "Preview filenames" to verify the output.
5. Click "Start" — when it finishes, the output folder can be opened directly from the UI.

## 🧑‍💻 Running from source (developers)

Requires Python 3.10+ on macOS / Linux / Windows.

```bash
git clone https://github.com/swiftruru/book-unbind.git
cd book-unbind
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Running tests

```bash
pytest -v
```

## 📦 Building locally

Requires Flutter SDK 3.41.4 and platform toolchains (Xcode + CocoaPods on macOS, `libgtk-3-dev` on Linux, Visual Studio on Windows).

```bash
flet build macos   # or windows / linux
```

## 🔍 Detection rules

Page-number detection only scans the bottom 7% of each page and tries the following patterns (priority top-down):

| Type | Example |
|---|---|
| Chapter-page | `1-4`, `12-3` |
| Letter-chapter | `A-3`, `D-11` |
| Chinese chapter | `附錄-5` |
| Arabic digits | `1`, `410` |
| Lowercase Roman | `iii`, `xii` |
| 3-level dotted | `1.2.3` |

Spans whose line contains `$`, `NT`, `ISBN`, `電話`, `售價` etc. are filtered out so prices and phone numbers don't get misread as page numbers.

## ⚠️ Known limitations

- **Pure-scan PDFs** (no text layer) fall into the "undetected" bucket for every page; filenames carry only the prefix. OCR is planned for a future release.
- **Native OS file drag-and-drop** is not supported (Flet 0.84's desktop framework doesn't expose a file-drop API yet); a large clickable card opens the file picker instead.
- **Encrypted PDFs** must be decrypted before processing.
- **Windows: don't run the Portable build from a VM shared folder or network drive** (see the warning in the [Download section](#-download) above). Use the Installer instead.

## 📝 Release notes

Per-version changelogs live in the [`changelog/`](changelog/) directory:

- [v0.2.0](changelog/v0.2.0.md) — Custom app icon, dev-mode branding, redesigned README
- [v0.1.0](changelog/v0.1.0.md) — Initial release

## 🧱 Project layout

```
.
├── main.py                    # Flet entrypoint (with dev-mode icon injection)
├── src/
│   ├── page_detector.py       # page-number detection
│   ├── filename_builder.py    # filename assembly
│   ├── pdf_splitter.py        # split pipeline
│   └── gui/app.py             # Flet UI
├── assets/icon.png            # app icon (2048x2048 PNG)
├── installer/BookUnbind.iss   # Inno Setup script (Windows installer)
├── tests/                     # pytest tests
├── changelog/                 # per-version changelogs
├── .github/workflows/         # CI (three-platform auto release)
└── pyproject.toml             # flet build config
```

## 📄 License

[MIT License](LICENSE) — © 2026 swiftruru
