"""
TCP Socket TUI Tool
asyncio + Textual 기반 양방향 TCP 소켓 클라이언트/서버 도구
"""
from __future__ import annotations

import asyncio
import logging
import socket
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# 파일 로거 설정
# ─────────────────────────────────────────────────────────────

_LOG_PATH = Path(__file__).parent / "tcp-socket-tool.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(_LOG_PATH, encoding="utf-8")],
)
log = logging.getLogger("tcp-socket-tool")

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Static
from textual.screen import Screen
from textual import on, work


# ─────────────────────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────────────────────

def get_local_ip() -> str:
    """현재 머신의 로컬 IP 주소를 반환한다."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        log.warning("[E007] get_local_ip: 로컬 IP 감지 실패: %s", e)
        log.debug("[E007] get_local_ip: 로컬 IP 감지 실패 traceback", exc_info=True)
        return "127.0.0.1"


def ts() -> str:
    """현재 시각 타임스탬프 문자열 반환."""
    return datetime.now().strftime("%H:%M:%S")


# ─────────────────────────────────────────────────────────────
# 시작 화면: Client / Server 선택
# ─────────────────────────────────────────────────────────────

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
        log.info("StartScreen: Server 모드 선택")
        self.app.push_screen(ServerConfigScreen())

    @on(Button.Pressed, "#btn-client")
    def go_client(self) -> None:
        log.info("StartScreen: Client 모드 선택")
        self.app.push_screen(ClientConfigScreen())


# ─────────────────────────────────────────────────────────────
# 서버 설정 화면: 포트 입력
# ─────────────────────────────────────────────────────────────

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
        port_str = self.query_one("#port-input", Input).value.strip()
        port = int(port_str) if port_str else 0  # 0 = OS가 자동 배정
        log.info("ServerConfigScreen: 서버 시작 요청 port=%s (0=자동)", port)
        self.app.switch_screen(ChatScreen(mode="server", port=port))


# ─────────────────────────────────────────────────────────────
# 클라이언트 설정 화면: 서버 주소 + 포트 입력
# ─────────────────────────────────────────────────────────────

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
        host = self.query_one("#host-input", Input).value.strip() or "127.0.0.1"
        port_str = self.query_one("#port-input", Input).value.strip()
        if not port_str:
            log.warning("ClientConfigScreen: 포트 번호 미입력")
            self.notify("포트 번호를 입력하세요.", severity="error")
            return
        log.info("ClientConfigScreen: 연결 요청 host=%s port=%s", host, port_str)
        self.app.switch_screen(ChatScreen(mode="client", host=host, port=int(port_str)))


# ─────────────────────────────────────────────────────────────
# 메인 채팅 화면 (Server / Client 공용)
# ─────────────────────────────────────────────────────────────

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
        self._writer: asyncio.StreamWriter | None = None
        self._server: asyncio.Server | None = None
        self._connected = False

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
            self._start_server()
        else:
            self._connect_client()

    def action_go_home(self) -> None:
        """연결 정리 후 시작 화면으로 돌아간다."""
        log.info("ChatScreen[%s]: 홈으로 복귀 (연결 정리)", self.mode)
        if self._writer:
            try:
                self._writer.close()
                log.debug("ChatScreen[%s]: writer 닫힘", self.mode)
            except Exception as e:
                log.warning("[E008] ChatScreen[%s]: writer 닫기 실패: %s", self.mode, e)
                log.debug("[E008] ChatScreen[%s]: writer 닫기 실패 traceback", self.mode, exc_info=True)
        if self._server:
            self._server.close()
            log.debug("ChatScreen[%s]: server 닫힘", self.mode)
        self.app.switch_screen(StartScreen())

    # ── 메시지 전송 ──────────────────────────────────────────

    @on(Button.Pressed, "#btn-send")
    @on(Input.Submitted, "#msg-input")
    def send_message(self) -> None:
        if not self._connected or not self._writer:
            log.debug("ChatScreen[%s]: send_message 무시 (connected=%s, writer=%s)",
                      self.mode, self._connected, self._writer is not None)
            return
        inp = self.query_one("#msg-input", Input)
        text = inp.value.strip()
        if not text:
            return
        inp.value = ""
        self._send(text)

    def _send(self, text: str) -> None:
        richlog = self.query_one("#log", RichLog)
        richlog.write(f"[bold cyan][{ts()}] [나] {text}[/bold cyan]")
        payload = text.rstrip("\n").encode()
        log.info("ChatScreen[%s]: TX %d bytes | repr=%r", self.mode, len(payload), payload)
        try:
            self._writer.write(payload)
            asyncio.get_event_loop().create_task(self._drain())
            log.debug("ChatScreen[%s]: write() 호출 완료, drain 예약", self.mode)
        except Exception as e:
            log.error("[E001] ChatScreen[%s]: 전송 실패: %s", self.mode, e)
            log.debug("[E001] ChatScreen[%s]: 전송 실패 traceback", self.mode, exc_info=True)
            richlog.write(f"[red][{ts()}] 전송 실패: {e}[/red]")

    async def _drain(self) -> None:
        if self._writer:
            try:
                await self._writer.drain()
                log.debug("ChatScreen[%s]: drain 완료", self.mode)
            except Exception as e:
                log.error("[E002] ChatScreen[%s]: drain 실패: %s", self.mode, e)
                log.debug("[E002] ChatScreen[%s]: drain 실패 traceback", self.mode, exc_info=True)

    # ── UI 상태 업데이트 헬퍼 ────────────────────────────────

    def _set_connected(self, peer: str) -> None:
        log.info("ChatScreen[%s]: 연결 확립 peer=%s", self.mode, peer)
        self._connected = True
        mode_label = "SERVER" if self.mode == "server" else "CLIENT"
        info = self.query_one("#info-bar", Static)
        info.update(f"[{mode_label}]  연결됨: {peer}")
        self.query_one("#msg-input", Input).disabled = False
        self.query_one("#btn-send", Button).disabled = False
        richlog = self.query_one("#log", RichLog)
        richlog.write(f"[green][{ts()}] 연결 성공: {peer}[/green]")

    def _set_disconnected(self, peer: str = "") -> None:
        log.info("ChatScreen[%s]: 연결 끊김 peer=%s", self.mode, peer or "(unknown)")
        self._connected = False
        self._writer = None
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

    # ── Server 모드 ──────────────────────────────────────────

    @work(exclusive=True)
    async def _start_server(self) -> None:
        richlog = self.query_one("#log", RichLog)
        log.info("ChatScreen[server]: asyncio.start_server 호출 port=%s", self.target_port)
        try:
            self._server = await asyncio.start_server(
                self._handle_client,
                host="0.0.0.0",
                port=self.target_port,
            )
            actual_port = self._server.sockets[0].getsockname()[1]
            self.target_port = actual_port
            local_ip = get_local_ip()
            log.info("ChatScreen[server]: 서버 바인딩 완료 %s:%s", local_ip, actual_port)
            mode_label = "SERVER"
            info = self.query_one("#info-bar", Static)
            info.update(f"[{mode_label}]  {local_ip}:{actual_port}  |  연결 대기 중...")
            richlog.write(f"[green][{ts()}] 서버 시작: {local_ip}:{actual_port}[/green]")
            async with self._server:
                await self._server.serve_forever()
        except Exception as e:
            log.error("[E003] ChatScreen[server]: 서버 오류: %s", e)
            log.debug("[E003] ChatScreen[server]: 서버 오류 traceback", exc_info=True)
            richlog.write(f"[red][{ts()}] 서버 오류: {e}[/red]")

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = "{}:{}".format(*writer.get_extra_info("peername", ("?", "?")))
        log.info("ChatScreen[server]: 클라이언트 연결 수락 peer=%s", peer)
        self._writer = writer
        self._set_connected(peer)
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    log.info("ChatScreen[server]: peer=%s EOF 수신", peer)
                    break
                log.info("ChatScreen[server]: RX %d bytes from %s | repr=%r",
                         len(data), peer, data)
                text = data.decode(errors="replace")
                richlog = self.query_one("#log", RichLog)
                richlog.write(f"[bold green][{ts()}] [상대] {text}[/bold green]")
        except Exception as e:
            log.error("[E004] ChatScreen[server]: 수신 루프 예외 peer=%s: %s", peer, e)
            log.debug("[E004] ChatScreen[server]: 수신 루프 예외 traceback peer=%s", peer, exc_info=True)
        finally:
            writer.close()
            log.debug("ChatScreen[server]: writer 닫힘 peer=%s", peer)
            self._set_disconnected(peer)

    # ── Client 모드 ──────────────────────────────────────────

    @work(exclusive=True)
    async def _connect_client(self) -> None:
        richlog = self.query_one("#log", RichLog)
        log.info("ChatScreen[client]: open_connection 시도 %s:%s",
                 self.target_host, self.target_port)
        richlog.write(f"[{ts()}] {self.target_host}:{self.target_port} 에 연결 시도...")
        try:
            reader, writer = await asyncio.open_connection(
                self.target_host, self.target_port
            )
        except Exception as e:
            log.error("[E005] ChatScreen[client]: 연결 실패 %s:%s → %s",
                      self.target_host, self.target_port, e)
            log.debug("[E005] ChatScreen[client]: 연결 실패 traceback", exc_info=True)
            richlog.write(f"[red][{ts()}] 연결 실패: {e}[/red]")
            return

        peer = f"{self.target_host}:{self.target_port}"
        log.info("ChatScreen[client]: 연결 성공 peer=%s", peer)
        self._writer = writer
        self._set_connected(peer)

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    log.info("ChatScreen[client]: peer=%s EOF 수신", peer)
                    break
                log.info("ChatScreen[client]: RX %d bytes from %s | repr=%r",
                         len(data), peer, data)
                text = data.decode(errors="replace")
                richlog.write(f"[bold green][{ts()}] [상대] {text}[/bold green]")
        except Exception as e:
            log.error("[E006] ChatScreen[client]: 수신 루프 예외 peer=%s: %s", peer, e)
            log.debug("[E006] ChatScreen[client]: 수신 루프 예외 traceback peer=%s", peer, exc_info=True)
        finally:
            writer.close()
            log.debug("ChatScreen[client]: writer 닫힘 peer=%s", peer)
            self._set_disconnected(peer)


# ─────────────────────────────────────────────────────────────
# App 진입점
# ─────────────────────────────────────────────────────────────

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


if __name__ == "__main__":
    TCPSocketApp().run()
    log.info("TCPSocketApp 종료")
