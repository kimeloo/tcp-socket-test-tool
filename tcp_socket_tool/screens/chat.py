"""메인 채팅 화면 (Server / Client 공용)."""
from __future__ import annotations

import asyncio
import sys

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Input, RichLog, Static
from textual.screen import Screen
from textual import on, work

from tcp_socket_tool.logging_config import log, ts, get_local_ip
from tcp_socket_tool.network import TCPConnection

DEFAULT_RECONNECT_INTERVAL = 5.0
MIN_RECONNECT_INTERVAL = 1.0

_MOD = "^" if sys.platform == "darwin" else "Ctrl+"


class ChatScreen(Screen):
    CSS = """
    ChatScreen {
        layout: vertical;
    }
    #info-bar {
        height: 1;
        background: $panel;
        color: $text-muted;
        padding: 0 2;
        text-style: bold;
    }
    #log {
        border: solid $panel;
        margin: 0 1;
        height: 1fr;
    }
    #input-row {
        height: 3;
        margin: 0 1 1 1;
    }
    #msg-input {
        width: 1fr;
    }
    #btn-send {
        width: 10;
        margin-left: 1;
    }
    #btn-reconnect {
        width: 12;
        margin-left: 1;
        display: none;
    }
    """

    BINDINGS = [
        Binding("escape", "go_home", "처음으로", key_display="Esc"),
        Binding("ctrl+r", "reconnect", "재연결", key_display=f"{_MOD}R"),
        Binding("ctrl+q", "quit", "종료", key_display=f"{_MOD}Q"),
    ]

    def __init__(
        self,
        mode: str,
        port: int = 0,
        host: str = "127.0.0.1",
        auto_reconnect: bool = False,
        reconnect_interval: float = 0.0,
    ):
        super().__init__()
        self.mode = mode          # "server" or "client"
        self.target_port = port
        self.target_host = host
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = (
            max(reconnect_interval, MIN_RECONNECT_INTERVAL)
            if reconnect_interval > 0
            else DEFAULT_RECONNECT_INTERVAL
        )
        self._mode_label = "SERVER" if mode == "server" else "CLIENT"
        self._user_closed = False
        self._conn = TCPConnection(
            on_connected=self._on_connected,
            on_disconnected=self._on_disconnected,
            on_message=self._on_net_message,
            on_error=self._on_error,
            on_info=self._on_info,
        )

    # ── UI 구성 ──────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static(f"[{self._mode_label}]  연결 대기 중...", id="info-bar")
        yield RichLog(id="log", highlight=True, markup=True)
        with Horizontal(id="input-row"):
            yield Input(placeholder="메시지 입력 후 Enter", id="msg-input", disabled=True)
            yield Button("전송", id="btn-send", variant="primary", disabled=True)
            yield Button("재연결", id="btn-reconnect", variant="warning")
        yield Footer()

    def on_mount(self) -> None:
        if self.mode == "server":
            self._run_server()
        else:
            self._run_client()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "reconnect" and self.mode != "client":
            return None
        return True

    def _show_reconnect_ui(self, show: bool) -> None:
        """클라이언트 모드에서 재연결/전송 버튼 display를 토글한다."""
        if self.mode != "client":
            return
        self.query_one("#btn-send", Button).display = not show
        self.query_one("#btn-reconnect", Button).display = show

    def action_go_home(self) -> None:
        """연결 정리 후 시작 화면으로 돌아간다."""
        log.info("ChatScreen[%s]: 홈으로 복귀 (연결 정리)", self.mode)
        self._user_closed = True
        self._conn.close()
        from tcp_socket_tool.screens.start import StartScreen
        self.app.switch_screen(StartScreen())

    # ── 네트워크 콜백 핸들러 ──────────────────────────────────

    def _on_connected(self, peer: str) -> None:
        log.info("ChatScreen[%s]: 연결 확립 peer=%s", self.mode, peer)
        info = self.query_one("#info-bar", Static)
        info.update(f"[{self._mode_label}]  연결됨: {peer}")
        self.query_one("#msg-input", Input).disabled = False
        self.query_one("#btn-send", Button).disabled = False
        self._show_reconnect_ui(False)
        richlog = self.query_one("#log", RichLog)
        richlog.write(f"[green][{ts()}] 연결 성공: {peer}[/green]")

    def _on_disconnected(self, peer: str) -> None:
        log.info("ChatScreen[%s]: 연결 끊김 peer=%s", self.mode, peer or "(unknown)")
        info = self.query_one("#info-bar", Static)
        if self.mode == "server":
            local_ip = get_local_ip()
            info.update(f"[{self._mode_label}]  {local_ip}:{self.target_port}  |  연결 대기 중...")
        else:
            info.update(f"[{self._mode_label}]  연결 끊김")
        self.query_one("#msg-input", Input).disabled = True
        self.query_one("#btn-send", Button).disabled = True
        if not self._user_closed:
            self._show_reconnect_ui(True)
        richlog = self.query_one("#log", RichLog)
        msg = "연결 끊김" if not peer else f"{peer} 연결 끊김"
        richlog.write(f"[yellow][{ts()}] {msg}[/yellow]")

    def _on_net_message(self, peer: str, text: str) -> None:
        richlog = self.query_one("#log", RichLog)
        richlog.write(f"[bold green][{ts()}] [상대] {text}[/bold green]")

    def _on_error(self, msg: str) -> None:
        richlog = self.query_one("#log", RichLog)
        richlog.write(f"[red][{ts()}] {msg}[/red]")

    def _on_info(self, msg: str) -> None:
        richlog = self.query_one("#log", RichLog)
        if self.mode == "server" and self._conn.actual_port:
            self.target_port = self._conn.actual_port
            local_ip = get_local_ip()
            info = self.query_one("#info-bar", Static)
            info.update(f"[{self._mode_label}]  {local_ip}:{self.target_port}  |  연결 대기 중...")
        richlog.write(f"[green][{ts()}] {msg}[/green]")

    # ── 네트워크 작업 (@work 래퍼) ────────────────────────────

    @work(exclusive=True, group="server")
    async def _run_server(self) -> None:
        await self._conn.start_server(self.target_port)

    @work(exclusive=True, group="client")
    async def _run_client(self) -> None:
        await self._conn.connect(self.target_host, self.target_port)

        if self._user_closed:
            return

        if not self._conn.connected:
            self._show_reconnect_ui(True)
            if self.auto_reconnect:
                await self._auto_reconnect_loop()

    async def _auto_reconnect_loop(self) -> None:
        """자동 재연결 루프. 연결 성공 또는 사용자 종료까지 반복한다."""
        attempt = 0
        while not self._user_closed:
            attempt += 1
            info = self.query_one("#info-bar", Static)
            remaining = int(self.reconnect_interval)
            for sec in range(remaining, 0, -1):
                if self._user_closed:
                    return
                info.update(
                    f"[CLIENT]  재연결 대기 중... "
                    f"({sec}초 후 시도 #{attempt})"
                )
                await asyncio.sleep(1)

            if self._user_closed:
                break

            richlog = self.query_one("#log", RichLog)
            richlog.write(f"[yellow][{ts()}] 재연결 시도 중... (시도 #{attempt})[/yellow]")
            info.update(f"[CLIENT]  재연결 시도 중... (시도 #{attempt})")

            await self._conn.connect(self.target_host, self.target_port)

            if self._user_closed or self._conn.connected:
                break

    # ── 재연결 ──────────────────────────────────────────────

    def action_reconnect(self) -> None:
        """수동 재연결 (Ctrl+R)."""
        if self.mode != "client" or self._conn.connected:
            return
        log.info("ChatScreen[client]: 수동 재연결 요청")
        self._run_client()  # exclusive=True → 기존 worker 취소 후 새로 시작

    @on(Button.Pressed, "#btn-reconnect")
    def manual_reconnect(self) -> None:
        self.action_reconnect()

    # ── 메시지 전송 ──────────────────────────────────────────

    @on(Button.Pressed, "#btn-send")
    @on(Input.Submitted, "#msg-input")
    def send_message(self) -> None:
        if not self._conn.connected:
            log.debug("ChatScreen[%s]: send_message 무시 (connected=%s)",
                      self.mode, self._conn.connected)
            return
        inp = self.query_one("#msg-input", Input)
        text = inp.value.strip()
        if not text:
            return
        inp.value = ""
        richlog = self.query_one("#log", RichLog)
        richlog.write(f"[bold cyan][{ts()}] [나] {text}[/bold cyan]")
        self._conn.send(text)
