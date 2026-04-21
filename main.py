"""BookUnbind entrypoint.

In dev mode (`python main.py`) on macOS, we clone the default Flet desktop
runner into `.flet-local/`, swap its icon + bundle name, and point Flet at
the clone via FLET_VIEW_PATH. This gives `python main.py` the same Dock /
About-dialog branding as the final built .app, without touching the
shared Flet runner used by other projects.
"""

from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

import flet as ft

# Ensure the app root is on sys.path so `from src...` works in packaged builds
# (on Windows the CWD isn't always the app root).
_APP_ROOT = Path(__file__).parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))


def _crash_log_path() -> Path:
    return Path.home() / ".bookunbind" / "crash.log"


def _write_crash_log(exc: BaseException) -> Path:
    log = _crash_log_path()
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n===== {datetime.now().isoformat()} =====\n")
        f.write(f"platform: {sys.platform}  python: {sys.version}\n")
        f.write(f"executable: {sys.executable}\n")
        f.write(f"cwd: {os.getcwd()}\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    return log

PROJECT_ROOT = Path(__file__).parent
ICON_PNG = PROJECT_ROOT / "assets" / "icon.png"
ICON_ICNS = PROJECT_ROOT / "assets" / "icon.icns"
LOCAL_RUNNER_DIR = PROJECT_ROOT / ".flet-local"
LOCAL_APP = LOCAL_RUNNER_DIR / "BookUnbind.app"
APP_DISPLAY_NAME = "BookUnbind"

# Pin to the Flet version our .venv installed; matches ~/.flet/client dir name.
FLET_RUNNER_DIRNAME = "flet-desktop-full-0.84.0"


def _build_icns(png: Path, icns: Path) -> None:
    """Convert a single PNG into a multi-resolution .icns via sips + iconutil."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        iconset = Path(td) / "icon.iconset"
        iconset.mkdir()
        # Apple's required iconset filenames (1x / 2x pairs)
        pairs = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]
        for size, name in pairs:
            subprocess.run(
                ["sips", "-z", str(size), str(size), str(png), "--out", str(iconset / name)],
                check=True,
                capture_output=True,
            )
        icns.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(icns)],
            check=True,
        )


def _prepare_dev_runner_macos() -> None:
    """Clone Flet's runner and apply our branding for `python main.py`."""
    if sys.platform != "darwin" or not ICON_PNG.exists():
        return

    # Flet checks ./build/macos/*.app BEFORE FLET_VIEW_PATH, so a stale
    # build from a previous `flet build` run would shadow our custom
    # runner. Remove it if its icon is older than assets/icon.png.
    build_macos = PROJECT_ROOT / "build" / "macos"
    if build_macos.exists():
        stale = True
        for app_dir in build_macos.glob("*.app"):
            icns = app_dir / "Contents" / "Resources" / "AppIcon.icns"
            if icns.exists() and icns.stat().st_mtime >= ICON_PNG.stat().st_mtime:
                stale = False
                break
        if stale:
            shutil.rmtree(build_macos)

    default_client = Path.home() / ".flet" / "client" / FLET_RUNNER_DIRNAME
    if not default_client.exists():
        # Flet hasn't downloaded the runner yet; skip this time. On the
        # next `python main.py` (after Flet downloads the runner) we'll
        # apply the customization.
        return

    default_app = next(default_client.glob("*.app"), None)
    if default_app is None:
        return

    # (Re)build icon.icns whenever the source PNG changes.
    png_mtime = ICON_PNG.stat().st_mtime
    if not ICON_ICNS.exists() or ICON_ICNS.stat().st_mtime < png_mtime:
        _build_icns(ICON_PNG, ICON_ICNS)

    local_icns = LOCAL_APP / "Contents" / "Resources" / "AppIcon.icns"
    needs_rebuild = (
        not LOCAL_APP.exists()
        or not local_icns.exists()
        or local_icns.stat().st_mtime < ICON_ICNS.stat().st_mtime
    )

    if needs_rebuild:
        LOCAL_RUNNER_DIR.mkdir(parents=True, exist_ok=True)
        if LOCAL_APP.exists():
            shutil.rmtree(LOCAL_APP)
        shutil.copytree(default_app, LOCAL_APP, symlinks=True)
        shutil.copy(ICON_ICNS, local_icns)
        # Assets.car is a compiled asset catalog that usually contains the
        # app icon. macOS prefers it over AppIcon.icns when CFBundleIconName
        # is set, so delete the catalog to force the OS to load our icns.
        assets_car = LOCAL_APP / "Contents" / "Resources" / "Assets.car"
        if assets_car.exists():
            assets_car.unlink()
        _patch_info_plist(LOCAL_APP / "Contents" / "Info.plist")
        # Bump mtime on the bundle and key files so macOS re-reads them.
        now = None
        os.utime(LOCAL_APP, now)
        os.utime(local_icns, now)
        os.utime(LOCAL_APP / "Contents" / "Info.plist", now)
        # Force Launch Services to re-register the bundle so the icon
        # cache is rebuilt (otherwise a stale icon can persist).
        lsregister = (
            "/System/Library/Frameworks/CoreServices.framework/Frameworks/"
            "LaunchServices.framework/Support/lsregister"
        )
        if os.path.isfile(lsregister):
            subprocess.run(
                [lsregister, "-f", str(LOCAL_APP)],
                check=False,
                capture_output=True,
            )

    os.environ["FLET_VIEW_PATH"] = str(LOCAL_RUNNER_DIR)


def _patch_info_plist(plist_path: Path) -> None:
    with plist_path.open("rb") as f:
        data = plistlib.load(f)
    data["CFBundleName"] = APP_DISPLAY_NAME
    data["CFBundleDisplayName"] = APP_DISPLAY_NAME
    data["CFBundleShortVersionString"] = "0.1.0"
    data["CFBundleVersion"] = "1"
    data["NSHumanReadableCopyright"] = "Copyright (c) 2026 RuData. All rights reserved."
    # Point the OS at our .icns and prevent it from looking inside Assets.car.
    data["CFBundleIconFile"] = "AppIcon"
    data.pop("CFBundleIconName", None)
    with plist_path.open("wb") as f:
        plistlib.dump(data, f)


def main() -> None:
    try:
        _prepare_dev_runner_macos()
    except Exception as ex:  # noqa: BLE001
        print(f"[main] dev icon setup skipped: {ex}", file=sys.stderr)

    from src.gui.app import build_app
    ft.run(build_app)


if __name__ == "__main__":
    try:
        main()
    except BaseException as ex:
        log = _write_crash_log(ex)
        print(f"[main] fatal error, wrote {log}", file=sys.stderr)
        raise
