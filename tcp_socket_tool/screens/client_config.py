"""클라이언트 설정 화면: 서버 주소 + 포트 입력."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Input, Label, Static, Switch
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
    #reconnect-row {
        height: 3;
        align: left middle;
    }
    #reconnect-label {
        margin-left: 1;
        content-align: left middle;
        height: 1;
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
            yield Label("자동 재연결")
            with Horizontal(id="reconnect-row"):
                yield Switch(value=False, id="reconnect-switch")
                yield Static("사용 안 함", id="reconnect-label")
            yield Label("재연결 간격 (초)")
            yield Input(placeholder="기본값: 5", id="interval-input", type="number", disabled=True)
            with Horizontal(id="btn-row"):
                yield Button("연결", id="btn-connect", variant="success")
                yield Button("뒤로", id="btn-back")
        yield Footer()

    @on(Button.Pressed, "#btn-back")
    def go_back(self) -> None:
        self.app.pop_screen()

    @on(Switch.Changed, "#reconnect-switch")
    def toggle_reconnect(self, event: Switch.Changed) -> None:
        interval_input = self.query_one("#interval-input", Input)
        label = self.query_one("#reconnect-label", Static)
        if event.value:
            interval_input.disabled = False
            label.update("사용")
        else:
            interval_input.disabled = True
            label.update("사용 안 함")

    @on(Button.Pressed, "#btn-connect")
    @on(Input.Submitted, "#host-input, #port-input")
    def connect(self) -> None:
        from tcp_socket_tool.screens.chat import ChatScreen
        host = self.query_one("#host-input", Input).value.strip() or "127.0.0.1"
        port_str = self.query_one("#port-input", Input).value.strip()
        if not port_str:
            log.warning("ClientConfigScreen: 포트 번호 미입력")
            self.notify("포트 번호를 입력하세요.", severity="error")
            return
        auto_reconnect = self.query_one("#reconnect-switch", Switch).value
        interval_str = self.query_one("#interval-input", Input).value.strip()
        reconnect_interval = float(interval_str) if interval_str else 0.0
        log.info("ClientConfigScreen: 연결 요청 host=%s port=%s auto_reconnect=%s interval=%s",
                 host, port_str, auto_reconnect, reconnect_interval)
        self.app.switch_screen(ChatScreen(
            mode="client", host=host, port=int(port_str),
            auto_reconnect=auto_reconnect,
            reconnect_interval=reconnect_interval,
        ))
