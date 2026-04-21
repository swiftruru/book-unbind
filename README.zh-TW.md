<div align="center">

[**English**](README.md) &nbsp;·&nbsp; **繁體中文**

# 📖 BookUnbind

### PDF 電子書「拆裝訂」工具

把整本 PDF 電子書切成每頁獨立檔案，自動辨識書籍頁碼並產生有意義的檔名。
原生跨平台桌面應用：macOS / Windows / Linux。

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

👉 歷史版本請至 [Releases](https://github.com/swiftruru/book-unbind/releases)。

</div>

> ### ⚠️ Windows 使用者請注意
>
> **推薦安裝 `BookUnbind-Setup-*.exe`**（Windows Installer），會自動裝到 `%LocalAppData%\Programs\BookUnbind\`，不需要系統管理員權限，並建立開始功能表捷徑。
>
> 如果要用 **Portable（`BookUnbind-windows.zip`）**，解壓後**請把資料夾放到 Windows 本機磁碟**（例如 `C:\Apps\` 或 `C:\Users\<你>\Documents\`）再執行。
>
> **不要**從以下路徑直接跑 `BookUnbind.exe`，會出現**開啟後視窗一片空白**：
>
> - Parallels Desktop / VMware Fusion 共享的 Mac 資料夾（路徑以 `C:\Mac\` 或 `\\Mac\` 開頭）
> - 任何 SMB / UNC 網路共享磁碟（`\\server\share\...`、`Z:\` 等映射的網路磁碟）
>
> **原因**：Flet 內嵌的 Python runtime 在虛擬檔案系統 / 網路共享上無法載入 `data\flutter_assets\app\app.zip`，導致 Flutter 殼啟動但 Python 未初始化。這是 VM 整合層的限制，不是 BookUnbind 本身的問題。

---

## ✨ 特色

- 🔍 **自動偵測書籍頁碼**：阿拉伯數字、羅馬數字、章節式 `1-4` / `D-11` / `附錄-5`、階層 `1.2.3`
- 👁 **Dry-run 預覽**：產檔前先列出全部檔名，確認無誤再執行
- 📁 **自動建立輸出資料夾**：預設 `{PDF 所在目錄}/{檔名}_unbind`，可手動更換
- ⚠️ **覆寫確認**：輸出資料夾已有檔案時提示使用者
- 🌙 **深色模式 UI**：Flet + Material Design
- ⚡ **純原生應用**：打包後的執行檔不需要使用者安裝 Python
- 🎨 **自訂 App 圖示**：dev 模式下也能看到自己的圖示（非預設 Flet runner 圖）
- 🤖 **CI 三平台自動打包**：推 `v*` tag → GitHub Actions 自動編譯 macOS / Windows / Linux

## 🧾 檔名規則

| 原始頁碼 | 偵測到 | 檔名 |
|---|---|---|
| 21 | `20` | `021_Page_20.pdf` |
| 25 | `1-4` | `025_Page_1-4.pdf` |
| 410 | `D-11` | `410_Page_D-11.pdf` |
| 5 | `iii` | `005_Page_iii.pdf` |
| 1 | —（封面） | `001.pdf` |

## 🛠 使用方式

1. 下載對應平台版本、安裝、開啟 BookUnbind
2. 點擊「選擇 PDF 檔案」卡片，挑選要拆的電子書
3. 輸出資料夾會自動預填為 `{PDF 檔名}_unbind`，視需要按「更換」
4. 點「預覽檔名」確認命名無誤
5. 點「開始拆分」執行 → 完成後可直接開啟輸出資料夾

## 🧑‍💻 從原始碼執行（開發者）

需要 Python 3.10+ 與 macOS / Linux / Windows 環境。

```bash
git clone https://github.com/swiftruru/book-unbind.git
cd book-unbind
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 執行測試

```bash
pytest -v
```

## 📦 自行打包

需先安裝 Flutter SDK 3.41.4 與平台對應工具鏈（macOS 需 Xcode + CocoaPods、Linux 需 `libgtk-3-dev`、Windows 需 Visual Studio）。

```bash
flet build macos   # 或 windows / linux
```

## 🔍 偵測規則

頁碼偵測只掃描頁面底部 7% 的區域，並套用下列 pattern（優先序由上至下）：

| 類型 | 範例 |
|---|---|
| 章節-頁碼 | `1-4`、`12-3` |
| 字母章節 | `A-3`、`D-11` |
| 中文章節 | `附錄-5` |
| 阿拉伯數字 | `1`、`410` |
| 小寫羅馬數字 | `iii`、`xii` |
| 三階層編號 | `1.2.3` |

另外會過濾掉同一行含 `$`、`NT`、`ISBN`、`電話`、`售價` 等字的 span，避免把價格、電話誤判為頁碼。

## ⚠️ 已知限制

- **純掃描型 PDF**（無文字層）全部頁面會落入「未偵測」狀態，檔名只有前綴。後續版本預計加 OCR。
- **原生 OS 檔案拖曳**目前不支援（Flet 0.84 的 desktop 框架尚未提供 file-drop API）；以大面積卡片點擊開啟選檔器代替。
- **加密 PDF** 需先解密才能處理。
- **Windows：勿從 VM 共享資料夾 / 網路磁碟執行** Portable 版（詳見上方 [Download 章節的警告](#-download)）。建議改用 Installer。

## 📝 版本紀錄

每個版本的詳細 changelog 保留在 [`changelog/`](changelog/) 資料夾：

- [v0.2.0](changelog/v0.2.0.md) — Custom app icon, dev-mode branding, redesigned README
- [v0.1.0](changelog/v0.1.0.md) — Initial release

## 🧱 專案結構

```
.
├── main.py                    # Flet 入口（含 dev-mode icon 注入）
├── src/
│   ├── page_detector.py       # 頁碼偵測
│   ├── filename_builder.py    # 檔名組裝
│   ├── pdf_splitter.py        # 切分流程
│   └── gui/app.py             # Flet UI
├── assets/icon.png            # App 圖示（2048x2048 PNG）
├── tests/                     # pytest 測試
├── changelog/                 # 每版 Changelog
├── .github/workflows/         # CI（三平台自動 release）
└── pyproject.toml             # flet build 設定
```

## 📄 授權

[MIT License](LICENSE) — © 2026 swiftruru
