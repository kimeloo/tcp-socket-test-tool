"""TCP Socket TUI App 진입점."""
from __future__ import annotations

import sys

from textual.app import App
from textual.binding import Binding

from tcp_socket_tool.logging_config import log
from tcp_socket_tool.screens.start import StartScreen

_MOD = "^" if sys.platform == "darwin" else "Ctrl+"


class TCPSocketApp(App):
    ENABLE_COMMAND_PALETTE = False
    TITLE = "TCP Socket Tool"
    CSS = """
    Screen {
        background: $surface;
    }
    """
    BINDINGS = [
        Binding("ctrl+p", "command_palette", "팔레트", key_display=f"{_MOD}P"),
        Binding("ctrl+q", "quit", "종료", key_display=f"{_MOD}Q"),
    ]

    async def action_command_palette(self) -> None:
        self.ENABLE_COMMAND_PALETTE = True
        await super().action_command_palette()

    def on_mount(self) -> None:
        log.info("=" * 60)
        log.info("TCPSocketApp 시작")
        self.push_screen(StartScreen())
