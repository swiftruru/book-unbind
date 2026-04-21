"""BookUnbind entrypoint."""

import flet as ft

from src.gui.app import build_app


def main() -> None:
    ft.run(build_app)


if __name__ == "__main__":
    main()
