# Error Codes

| 코드 | 설명 | 위치 |
|------|------|------|
| E001 | 메시지 전송 실패 | `ChatScreen._send()` |
| E002 | 스트림 drain 실패 | `ChatScreen._drain()` |
| E003 | 서버 시작 실패 | `ChatScreen._start_server()` |
| E004 | 서버 수신 루프 예외 | `ChatScreen._handle_client()` |
| E005 | 클라이언트 연결 실패 | `ChatScreen._connect_client()` |
| E006 | 클라이언트 수신 루프 예외 | `ChatScreen._connect_client()` |
| E007 | 로컬 IP 감지 실패 | `get_local_ip()` |
| E008 | Writer 닫기 실패 | `ChatScreen.action_go_home()` |
