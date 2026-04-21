# 📖 BookUnbind

把 PDF 電子書「拆裝訂」成每頁獨立 PDF 的 macOS 桌面工具。
檔名同時保留 **PDF 原始頁碼**（前綴）與 **書籍自身頁碼**（後綴），例如：

| 原始頁碼 | 偵測到 | 檔名 |
|---|---|---|
| 21 | `20` | `021_Page_20.pdf` |
| 25 | `1-4` | `025_Page_1-4.pdf` |
| 410 | `D-11` | `410_Page_D-11.pdf` |
| 5 | `iii` | `005_Page_iii.pdf` |
| 1 | —（封面） | `001.pdf` |

## 特色

- 🔍 **自動偵測書籍頁碼**：阿拉伯數字、羅馬數字、章節式 `1-4` / `D-11` / `附錄-5`、階層 `1.2.3`
- 👁 **Dry-run 預覽**：產檔前先列出全部檔名，確認無誤再執行
- 📁 **自動建立輸出資料夾**：預設 `{PDF 所在目錄}/{檔名}_unbind`，可手動更換
- ⚠️ **覆寫確認**：輸出資料夾已有檔案時提示使用者
- 🌙 **深色模式 UI**：Flet + Material Design
- ⚡ **純原生應用**：打包後的 `.app` 不需要使用者安裝 Python

## 安裝與使用

### 直接使用（推薦一般使用者）

到 [Releases](https://github.com/swiftruru/book-unbind/releases) 下載最新版的 `BookUnbind.app`，拖到 `/Applications/` 即可雙擊開啟。

操作流程：

1. 點擊「選擇 PDF 檔案」卡片，挑選要拆的電子書
2. 輸出資料夾會自動預填為 `{PDF 檔名}_unbind`，可視需要更換
3. 點「預覽檔名」確認命名無誤
4. 點「開始拆分」執行 → 完成後可直接開啟輸出資料夾

### 從原始碼執行（開發者）

需要 Python 3.10+ 與 macOS 環境。

```bash
git clone https://github.com/swiftruru/book-unbind.git
cd book-unbind
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 執行測試

```bash
.venv/bin/pytest -v
```

## 自行打包 macOS App

需先安裝 Flutter SDK 與 CocoaPods：

```bash
brew install --cask flutter
brew install cocoapods
```

打包：

```bash
.venv/bin/flet build macos \
  --project BookUnbind --product BookUnbind \
  --exclude .venv build local_samples tests .pytest_cache .claude .git
```

產物在 `build/macos/BookUnbind.app`。

## 偵測規則與限制

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

**已知限制**：

- **純掃描型 PDF**（無文字層）全部頁面會落入「未偵測」狀態，檔名只有前綴。後續版本預計加 OCR。
- **原生 OS 檔案拖曳**目前不支援（Flet 0.84 的 desktop 框架尚未提供 file-drop API）；以大面積卡片點擊開啟選檔器代替。
- **加密 PDF** 需先解密才能處理。

## 專案結構

```
.
├── main.py                    # Flet 入口
├── src/
│   ├── page_detector.py       # 頁碼偵測
│   ├── filename_builder.py    # 檔名組裝
│   ├── pdf_splitter.py        # 切分流程
│   └── gui/app.py             # Flet UI
├── tests/                     # 單元測試（pytest）
├── requirements.txt
└── pyproject.toml             # flet build 設定
```

## 技術棧

- **Python 3.10+**
- **[Flet](https://flet.dev/) 0.84** — Python 版 Flutter GUI
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** — 文字抽取 + 座標偵測
- **[pypdf](https://pypdf.readthedocs.io/)** — PDF 頁面切分

## 授權

[MIT License](LICENSE)
