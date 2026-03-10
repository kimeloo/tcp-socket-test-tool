"""서버 설정 화면: 포트 입력."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Input, Label, Static
from textual.screen import Screen
from textual import on

from tcp_socket_tool.logging_config import log


class ServerConfigScreen(Screen):
    CSS = """
    ServerConfigScreen {
        align: center middle;
    }
    #config-box {
        width: 50;
        height: auto;
        border: solid $accent;
        padding: 2 4;
    }
    #config-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }
    Label {
        margin-top: 1;
    }
    Input {
        margin-top: 0;
    }
    #btn-row {
        margin-top: 2;
        align: center middle;
    }
    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="config-box"):
            yield Static("Server 설정", id="config-title")
            yield Label("포트 번호 (비워두면 자동 선택)")
            yield Input(placeholder="예: 9000", id="port-input", type="integer")
            with Horizontal(id="btn-row"):
                yield Button("시작", id="btn-start", variant="primary")
                yield Button("뒤로", id="btn-back")
        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-start")
    @on(Input.Submitted, "#port-input")
    def start_server(self) -> None:
        from tcp_socket_tool.screens.chat import ChatScreen
        port_str = self.query_one("#port-input", Input).value.strip()
        port = int(port_str) if port_str else 0  # 0 = OS가 자동 배정
        log.info("ServerConfigScreen: 서버 시작 요청 port=%s (0=자동)", port)
        self.app.switch_screen(ChatScreen(mode="server", port=port))
