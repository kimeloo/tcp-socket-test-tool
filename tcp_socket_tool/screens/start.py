"""시작 화면: Client / Server 선택."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Static
from textual.screen import Screen
from textual import on

from tcp_socket_tool.logging_config import log


class StartScreen(Screen):
    CSS = """
    StartScreen {
        align: center middle;
    }
    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
        width: 100%;
    }
    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 3;
        width: 100%;
    }
    #btn-container {
        align: center middle;
        height: auto;
    }
    Button {
        margin: 0 2;
        min-width: 18;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("TCP Socket Tool", id="title")
        yield Static("모드를 선택하세요", id="subtitle")
        with Horizontal(id="btn-container"):
            yield Button("Server 시작", id="btn-server", variant="primary")
            yield Button("Client 연결", id="btn-client", variant="success")
        yield Footer()

    @on(Button.Pressed, "#btn-server")
    def go_server(self) -> None:
        from tcp_socket_tool.screens.server_config import ServerConfigScreen
        log.info("StartScreen: Server 모드 선택")
        self.app.push_screen(ServerConfigScreen())

    @on(Button.Pressed, "#btn-client")
    def go_client(self) -> None:
        from tcp_socket_tool.screens.client_config import ClientConfigScreen
        log.info("StartScreen: Client 모드 선택")
        self.app.push_screen(ClientConfigScreen())
