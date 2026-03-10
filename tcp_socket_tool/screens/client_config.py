"""클라이언트 설정 화면: 서버 주소 + 포트 입력."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Input, Label, Static
from textual.screen import Screen
from textual import on

from tcp_socket_tool.logging_config import log


class ClientConfigScreen(Screen):
    CSS = """
    ClientConfigScreen {
        align: center middle;
    }
    #config-box {
        width: 50;
        height: auto;
        border: solid $success;
        padding: 2 4;
    }
    #config-title {
        text-align: center;
        text-style: bold;
        color: $success;
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
            yield Static("Client 설정", id="config-title")
            yield Label("서버 주소")
            yield Input(placeholder="예: 127.0.0.1", value="127.0.0.1", id="host-input")
            yield Label("포트 번호")
            yield Input(placeholder="예: 9000", id="port-input", type="integer")
            with Horizontal(id="btn-row"):
                yield Button("연결", id="btn-connect", variant="success")
                yield Button("뒤로", id="btn-back")
        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-connect")
    @on(Input.Submitted)
    def connect(self) -> None:
        from tcp_socket_tool.screens.chat import ChatScreen
        host = self.query_one("#host-input", Input).value.strip() or "127.0.0.1"
        port_str = self.query_one("#port-input", Input).value.strip()
        if not port_str:
            log.warning("ClientConfigScreen: 포트 번호 미입력")
            self.notify("포트 번호를 입력하세요.", severity="error")
            return
        log.info("ClientConfigScreen: 연결 요청 host=%s port=%s", host, port_str)
        self.app.switch_screen(ChatScreen(mode="client", host=host, port=int(port_str)))
