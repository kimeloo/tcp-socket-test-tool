"""TCP Socket TUI App 진입점."""
from __future__ import annotations

from textual.app import App

from tcp_socket_tool.logging_config import log
from tcp_socket_tool.screens.start import StartScreen


class TCPSocketApp(App):
    TITLE = "TCP Socket Tool"
    CSS = """
    Screen {
        background: $surface;
    }
    """

    def on_mount(self) -> None:
        log.info("=" * 60)
        log.info("TCPSocketApp 시작")
        self.push_screen(StartScreen())
