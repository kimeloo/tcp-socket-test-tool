"""TUI 독립 TCP 네트워크 로직."""
from __future__ import annotations

import asyncio
from typing import Callable

from tcp_socket_tool.logging_config import log, get_local_ip


class TCPConnection:
    """콜백 기반 TCP 연결 관리 클래스.

    Textual 의존성 없이 순수 asyncio로 동작하며,
    상태 변화를 콜백으로 전달한다.
    """

    def __init__(
        self,
        *,
        on_connected: Callable[[str], None] | None = None,
        on_disconnected: Callable[[str], None] | None = None,
        on_message: Callable[[str, str], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        on_info: Callable[[str], None] | None = None,
    ):
        self._writer: asyncio.StreamWriter | None = None
        self._server: asyncio.Server | None = None
        self.connected: bool = False
        self.mode: str = ""
        self.actual_port: int = 0

        self._on_connected = on_connected or (lambda peer: None)
        self._on_disconnected = on_disconnected or (lambda peer: None)
        self._on_message = on_message or (lambda peer, text: None)
        self._on_error = on_error or (lambda msg: None)
        self._on_info = on_info or (lambda msg: None)

    # ── Server ────────────────────────────────────────────────

    async def start_server(self, port: int = 0) -> None:
        """서버를 시작하고 클라이언트 연결을 수락한다."""
        self.mode = "server"
        log.info("TCPConnection[server]: asyncio.start_server 호출 port=%s", port)
        try:
            self._server = await asyncio.start_server(
                self._handle_client,
                host="0.0.0.0",
                port=port,
            )
            self.actual_port = self._server.sockets[0].getsockname()[1]
            local_ip = get_local_ip()
            log.info("TCPConnection[server]: 서버 바인딩 완료 %s:%s", local_ip, self.actual_port)
            self._on_info(f"서버 시작: {local_ip}:{self.actual_port}")
            async with self._server:
                await self._server.serve_forever()
        except Exception as e:
            log.error("[E003] TCPConnection[server]: 서버 오류: %s", e)
            log.debug("[E003] TCPConnection[server]: 서버 오류 traceback", exc_info=True)
            self._on_error(f"서버 오류: {e}")

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = "{}:{}".format(*writer.get_extra_info("peername", ("?", "?")))
        log.info("TCPConnection[server]: 클라이언트 연결 수락 peer=%s", peer)
        self._writer = writer
        self.connected = True
        self._on_connected(peer)
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    log.info("TCPConnection[server]: peer=%s EOF 수신", peer)
                    break
                log.info("TCPConnection[server]: RX %d bytes from %s | repr=%r",
                         len(data), peer, data)
                text = data.decode(errors="replace")
                self._on_message(peer, text)
        except Exception as e:
            log.error("[E004] TCPConnection[server]: 수신 루프 예외 peer=%s: %s", peer, e)
            log.debug("[E004] TCPConnection[server]: 수신 루프 예외 traceback peer=%s", peer, exc_info=True)
        finally:
            writer.close()
            log.debug("TCPConnection[server]: writer 닫힘 peer=%s", peer)
            self.connected = False
            self._writer = None
            self._on_disconnected(peer)

    # ── Client ────────────────────────────────────────────────

    async def connect(self, host: str, port: int) -> None:
        """클라이언트로서 서버에 연결한다."""
        self.mode = "client"
        # 재연결을 위한 상태 초기화
        if self._writer:
            try:
                self._writer.close()
            except Exception:
                pass
            self._writer = None
        self.connected = False
        log.info("TCPConnection[client]: open_connection 시도 %s:%s", host, port)
        self._on_info(f"{host}:{port} 에 연결 시도...")
        try:
            reader, writer = await asyncio.open_connection(host, port)
        except Exception as e:
            log.error("[E005] TCPConnection[client]: 연결 실패 %s:%s → %s", host, port, e)
            log.debug("[E005] TCPConnection[client]: 연결 실패 traceback", exc_info=True)
            self._on_error(f"연결 실패: {e}")
            return

        peer = f"{host}:{port}"
        log.info("TCPConnection[client]: 연결 성공 peer=%s", peer)
        self._writer = writer
        self.connected = True
        self._on_connected(peer)

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    log.info("TCPConnection[client]: peer=%s EOF 수신", peer)
                    break
                log.info("TCPConnection[client]: RX %d bytes from %s | repr=%r",
                         len(data), peer, data)
                text = data.decode(errors="replace")
                self._on_message(peer, text)
        except Exception as e:
            log.error("[E006] TCPConnection[client]: 수신 루프 예외 peer=%s: %s", peer, e)
            log.debug("[E006] TCPConnection[client]: 수신 루프 예외 traceback peer=%s", peer, exc_info=True)
        finally:
            writer.close()
            log.debug("TCPConnection[client]: writer 닫힘 peer=%s", peer)
            self.connected = False
            self._writer = None
            self._on_disconnected(peer)

    # ── 공통 ──────────────────────────────────────────────────

    def send(self, text: str) -> None:
        """메시지를 전송한다."""
        if not self.connected or not self._writer:
            return
        payload = text.rstrip("\n").encode()
        log.info("TCPConnection[%s]: TX %d bytes | repr=%r", self.mode, len(payload), payload)
        try:
            self._writer.write(payload)
            asyncio.get_event_loop().create_task(self._drain())
            log.debug("TCPConnection[%s]: write() 호출 완료, drain 예약", self.mode)
        except Exception as e:
            log.error("[E001] TCPConnection[%s]: 전송 실패: %s", self.mode, e)
            log.debug("[E001] TCPConnection[%s]: 전송 실패 traceback", self.mode, exc_info=True)
            self._on_error(f"전송 실패: {e}")

    async def _drain(self) -> None:
        if self._writer:
            try:
                await self._writer.drain()
                log.debug("TCPConnection[%s]: drain 완료", self.mode)
            except Exception as e:
                log.error("[E002] TCPConnection[%s]: drain 실패: %s", self.mode, e)
                log.debug("[E002] TCPConnection[%s]: drain 실패 traceback", self.mode, exc_info=True)

    def close(self) -> None:
        """연결 및 서버를 닫는다."""
        log.info("TCPConnection[%s]: close 호출", self.mode)
        if self._writer:
            try:
                self._writer.close()
                log.debug("TCPConnection[%s]: writer 닫힘", self.mode)
            except Exception as e:
                log.warning("[E008] TCPConnection[%s]: writer 닫기 실패: %s", self.mode, e)
                log.debug("[E008] TCPConnection[%s]: writer 닫기 실패 traceback", self.mode, exc_info=True)
        if self._server:
            self._server.close()
            log.debug("TCPConnection[%s]: server 닫힘", self.mode)
        self.connected = False
        self._writer = None
