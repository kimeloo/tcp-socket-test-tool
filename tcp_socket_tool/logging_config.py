"""로깅 설정 및 공통 헬퍼 함수."""
from __future__ import annotations

import logging
import socket
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# 파일 로거 설정
# ─────────────────────────────────────────────────────────────

_LOG_PATH = Path(__file__).parent.parent / "tcp-socket-tool.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(_LOG_PATH, encoding="utf-8")],
)
log = logging.getLogger("tcp-socket-tool")


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
