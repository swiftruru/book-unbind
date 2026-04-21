"""Flet GUI for BookUnbind (Flet 0.84+)."""

from __future__ import annotations

import asyncio
import functools
import os
import subprocess
import sys
import traceback

import flet as ft

from src.pdf_splitter import preview, split


async def build_app(page: ft.Page) -> None:
    page.title = "BookUnbind — PDF 電子書拆檔工具"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 24

    # Skip Python finalizers to avoid a crash in PyMuPDF's static-object
    # destructors that try to call into Python during interpreter teardown.
    def hard_exit(_e=None) -> None:
        os._exit(0)

    page.on_close = hard_exit

    state: dict = {"pdf": None, "out_dir": None, "previewed": False}

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # --- Controls ---
    drop_title = ft.Text("點擊選擇 PDF 檔案", size=18, weight=ft.FontWeight.W_600)
    drop_subtitle = ft.Text(
        "支援 .pdf 格式",
        size=12,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )
    drop_icon = ft.Icon(ft.Icons.PICTURE_AS_PDF, size=56, color=ft.Colors.PRIMARY)

    out_path_label = ft.Text("尚未選擇", size=13, expand=True, no_wrap=False)
    out_path_hint = ft.Text(
        "選好 PDF 後會自動填入預設路徑",
        size=11,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )

    status = ft.Text("", size=13, color=ft.Colors.BLUE_200)
    progress = ft.ProgressBar(value=0, visible=False)
    preview_list = ft.ListView(expand=True, spacing=2, padding=12)
    preview_count = ft.Text("尚未預覽", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    def snack(msg: str, error: bool = False) -> None:
        bar = ft.SnackBar(
            ft.Text(msg),
            bgcolor=ft.Colors.RED_400 if error else None,
            open=True,
        )
        page.overlay.append(bar)
        page.update()

    def with_errors(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as ex:
                print(traceback.format_exc(), file=sys.stderr)
                snack(f"{type(ex).__name__}: {ex}", error=True)
        return wrapper

    def default_out_dir_for(pdf_path: str) -> str:
        parent = os.path.dirname(os.path.abspath(pdf_path))
        stem = os.path.splitext(os.path.basename(pdf_path))[0]
        return os.path.join(parent, f"{stem}_unbind")

    def refresh_buttons() -> None:
        ready = bool(state["pdf"] and state["out_dir"])
        preview_btn.disabled = not ready
        split_btn.disabled = not state["previewed"]
        page.update()

    def clear_preview() -> None:
        state["previewed"] = False
        preview_list.controls.clear()
        preview_count.value = "尚未預覽"

    def set_pdf(path: str) -> None:
        state["pdf"] = path
        state["out_dir"] = default_out_dir_for(path)
        drop_title.value = os.path.basename(path)
        drop_subtitle.value = f"📄 {path}"
        drop_icon.name = ft.Icons.CHECK_CIRCLE
        drop_icon.color = ft.Colors.GREEN_400
        out_path_label.value = state["out_dir"]
        out_path_hint.value = "（會自動建立此資料夾；可點右側按鈕換別的）"
        clear_preview()
        refresh_buttons()

    # --- Handlers ---
    async def on_pick_pdf(_e=None) -> None:
        result = await file_picker.pick_files(
            dialog_title="選擇 PDF 電子書",
            allow_multiple=False,
            allowed_extensions=["pdf"],
        )
        if result:
            set_pdf(result[0].path)

    async def on_pick_dir(_e=None) -> None:
        path = await file_picker.get_directory_path(dialog_title="選擇輸出資料夾")
        if path:
            state["out_dir"] = path
            out_path_label.value = path
            out_path_hint.value = "（已手動指定）"
            clear_preview()
            refresh_buttons()

    async def on_preview(_e=None) -> None:
        if not state["pdf"]:
            return
        status.value = "掃描頁面中…"
        preview_list.controls.clear()
        preview_count.value = ""
        page.update()
        rows = await asyncio.to_thread(preview, state["pdf"])
        for idx, name in rows:
            preview_list.controls.append(
                ft.Text(f"{idx:>4}  →  {name}", size=12, font_family="Menlo")
            )
        preview_count.value = f"共 {len(rows)} 頁"
        status.value = "請確認檔名清單，無誤後點「開始拆分」。"
        state["previewed"] = True
        refresh_buttons()

    async def on_split(_e=None) -> None:
        if not (state["pdf"] and state["out_dir"]):
            return
        out_dir = state["out_dir"]

        # Ensure output directory is ready; confirm overwrite if non-empty.
        if os.path.isdir(out_dir) and os.listdir(out_dir):
            confirmed = await confirm_overwrite(out_dir)
            if not confirmed:
                return
        else:
            os.makedirs(out_dir, exist_ok=True)

        progress.value = 0
        progress.visible = True
        split_btn.disabled = True
        preview_btn.disabled = True
        pick_pdf_btn.disabled = True
        pick_dir_btn.disabled = True
        status.value = "開始處理…"
        page.update()

        loop = asyncio.get_running_loop()

        def cb(cur: int, total: int, fn: str) -> None:
            def apply() -> None:
                progress.value = cur / total
                status.value = f"處理中 ({cur}/{total})  {fn}"
                page.update()
            loop.call_soon_threadsafe(apply)

        try:
            produced = await asyncio.to_thread(split, state["pdf"], out_dir, cb)
            status.value = f"完成！共產生 {len(produced)} 個檔案。"
            progress.value = 1
            page.update()
            await show_done_dialog(len(produced))
        finally:
            progress.visible = False
            pick_pdf_btn.disabled = False
            pick_dir_btn.disabled = False
            refresh_buttons()

    async def confirm_overwrite(out_dir: str) -> bool:
        fut: asyncio.Future[bool] = asyncio.get_running_loop().create_future()

        def on_yes(_e) -> None:
            page.pop_dialog()
            page.update()
            if not fut.done():
                fut.set_result(True)

        def on_no(_e) -> None:
            page.pop_dialog()
            page.update()
            if not fut.done():
                fut.set_result(False)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ 輸出資料夾已有檔案"),
            content=ft.Text(
                f"{out_dir}\n\n"
                "此資料夾已存在且包含檔案。繼續會直接覆寫同名檔案，"
                "其它既有檔案不會被刪除。是否繼續？"
            ),
            actions=[
                ft.TextButton("取消", on_click=on_no),
                ft.FilledButton("繼續覆寫", on_click=on_yes),
            ],
        )
        page.show_dialog(dlg)
        page.update()
        return await fut

    async def show_done_dialog(n: int) -> None:
        def open_folder(_e) -> None:
            _open_in_file_manager(state["out_dir"])
            page.pop_dialog()
            page.update()

        def close(_e) -> None:
            page.pop_dialog()
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("✅ 拆分完成"),
            content=ft.Text(f"共產生 {n} 個檔案於：\n{state['out_dir']}"),
            actions=[
                ft.TextButton("開啟輸出資料夾", on_click=open_folder),
                ft.TextButton("關閉", on_click=close),
            ],
        )
        page.show_dialog(dlg)
        page.update()

    # --- Buttons ---
    pick_pdf_btn = ft.ElevatedButton(
        "選擇 PDF", icon=ft.Icons.PICTURE_AS_PDF, on_click=with_errors(on_pick_pdf)
    )
    pick_dir_btn = ft.OutlinedButton(
        "更換", icon=ft.Icons.FOLDER_OPEN, on_click=with_errors(on_pick_dir)
    )
    preview_btn = ft.OutlinedButton(
        "預覽檔名", icon=ft.Icons.VISIBILITY, on_click=with_errors(on_preview), disabled=True
    )
    split_btn = ft.FilledButton(
        "開始拆分", icon=ft.Icons.CONTENT_CUT, on_click=with_errors(on_split), disabled=True
    )

    # --- Drop zone (click-to-pick; Flet 0.84 lacks native OS file-drop support) ---
    pick_pdf_btn_big = ft.FilledTonalButton(
        "選擇 PDF 檔案",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=with_errors(on_pick_pdf),
    )
    drop_zone = ft.Container(
        content=ft.Column(
            [
                drop_icon,
                drop_title,
                drop_subtitle,
                pick_pdf_btn_big,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        on_click=lambda _e: asyncio.create_task(with_errors(on_pick_pdf)()),
        alignment=ft.Alignment(0, 0),
        padding=24,
        border=ft.border.all(2, ft.Colors.OUTLINE),
        border_radius=14,
        ink=True,
    )

    out_row = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.FOLDER_OUTLINED, color=ft.Colors.ON_SURFACE_VARIANT),
                        out_path_label,
                        pick_dir_btn,
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                out_path_hint,
            ],
            spacing=4,
        ),
        padding=14,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
    )

    action_row = ft.Row(
        [preview_btn, split_btn, ft.Container(expand=True), preview_count], spacing=10
    )

    preview_panel = ft.Container(
        content=preview_list,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=12,
        expand=True,
        padding=4,
    )

    page.add(
        ft.Column(
            [
                ft.Column(
                    [
                        ft.Text("📖 BookUnbind", size=30, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "把 PDF 電子書切成每頁獨立檔案",
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=2,
                ),
                ft.Divider(),
                drop_zone,
                out_row,
                action_row,
                preview_panel,
                progress,
                status,
            ],
            spacing=14,
            expand=True,
        )
    )


def _open_in_file_manager(path: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", path], check=False)
    elif sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", path], check=False)
