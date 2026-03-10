"""TCP Socket TUI Tool — 진입점."""
from tcp_socket_tool.app import TCPSocketApp
from tcp_socket_tool.logging_config import log

if __name__ == "__main__":
    TCPSocketApp().run()
    log.info("TCPSocketApp 종료")
