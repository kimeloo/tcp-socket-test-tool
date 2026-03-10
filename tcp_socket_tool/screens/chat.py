"""메인 채팅 화면 (Server / Client 공용)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Input, RichLog, Static
from textual.screen import Screen
from textual import on, work

from tcp_socket_tool.logging_config import log, ts, get_local_ip
from tcp_socket_tool.network import TCPConnection


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
    """

    BINDINGS = [
        ("escape", "go_home", "처음으로"),
    ]

    def __init__(self, mode: str, port: int = 0, host: str = "127.0.0.1"):
        super().__init__()
        self.mode = mode          # "server" or "client"
        self.target_port = port
        self.target_host = host
        self._conn = TCPConnection(
            on_connected=self._on_connected,
            on_disconnected=self._on_disconnected,
            on_message=self._on_message,
            on_error=self._on_error,
            on_info=self._on_info,
        )

    # ── UI 구성 ──────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        mode_label = "SERVER" if self.mode == "server" else "CLIENT"
        yield Static(f"[{mode_label}]  연결 대기 중...", id="info-bar")
        yield RichLog(id="log", highlight=True, markup=True)
        with Horizontal(id="input-row"):
            yield Input(placeholder="메시지 입력 후 Enter", id="msg-input", disabled=True)
            yield Button("전송", id="btn-send", variant="primary", disabled=True)
        yield Footer()

    def on_mount(self) -> None:
        if self.mode == "server":
            self._run_server()
        else:
            self._run_client()

    def action_go_home(self) -> None:
        """연결 정리 후 시작 화면으로 돌아간다."""
        log.info("ChatScreen[%s]: 홈으로 복귀 (연결 정리)", self.mode)
        self._conn.close()
        from tcp_socket_tool.screens.start import StartScreen
        self.app.switch_screen(StartScreen())

    # ── 네트워크 콜백 핸들러 ──────────────────────────────────

    def _on_connected(self, peer: str) -> None:
        log.info("ChatScreen[%s]: 연결 확립 peer=%s", self.mode, peer)
        mode_label = "SERVER" if self.mode == "server" else "CLIENT"
        info = self.query_one("#info-bar", Static)
        info.update(f"[{mode_label}]  연결됨: {peer}")
        self.query_one("#msg-input", Input).disabled = False
        self.query_one("#btn-send", Button).disabled = False
        richlog = self.query_one("#log", RichLog)
        richlog.write(f"[green][{ts()}] 연결 성공: {peer}[/green]")

    def _on_disconnected(self, peer: str) -> None:
        log.info("ChatScreen[%s]: 연결 끊김 peer=%s", self.mode, peer or "(unknown)")
        mode_label = "SERVER" if self.mode == "server" else "CLIENT"
        info = self.query_one("#info-bar", Static)
        if self.mode == "server":
            local_ip = get_local_ip()
            info.update(f"[{mode_label}]  {local_ip}:{self.target_port}  |  연결 대기 중...")
        else:
            info.update(f"[{mode_label}]  연결 끊김")
        self.query_one("#msg-input", Input).disabled = True
        self.query_one("#btn-send", Button).disabled = True
        richlog = self.query_one("#log", RichLog)
        msg = "연결 끊김" if not peer else f"{peer} 연결 끊김"
        richlog.write(f"[yellow][{ts()}] {msg}[/yellow]")

    def _on_message(self, peer: str, text: str) -> None:
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
            info.update(f"[SERVER]  {local_ip}:{self.target_port}  |  연결 대기 중...")
        richlog.write(f"[green][{ts()}] {msg}[/green]")

    # ── 네트워크 작업 (@work 래퍼) ────────────────────────────

    @work(exclusive=True)
    async def _run_server(self) -> None:
        await self._conn.start_server(self.target_port)

    @work(exclusive=True)
    async def _run_client(self) -> None:
        await self._conn.connect(self.target_host, self.target_port)

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
