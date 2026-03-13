# Changelog

이 프로젝트의 모든 주요 변경사항을 기록합니다.

## [Unreleased]

### Added

- Client 자동 재연결 기능 (ClientConfigScreen에서 활성화/간격 설정)
- Client 수동 재연결 버튼 및 단축키 (`Ctrl+R`)
- ChatScreen 진입 시 메시지 입력 필드 자동 포커스
- 포커스가 입력 필드 외부에 있을 때 printable key 입력 시 입력 필드로 리다이렉트

### Changed

- 메시지 전송을 연결 상태에 따라 제어 (연결 전/끊김 시 비활성화, 연결 성공 시 활성화)
- ChatScreen 버튼 토글 로직을 `_show_reconnect_ui()` 헬퍼로 통합
- 자동 재연결 루프를 `_auto_reconnect_loop()`으로 분리하여 `_run_client()` 단순화
- mode_label 중복 계산을 `_mode_label` 속성으로 통합
- 불필요한 `_reconnecting` 플래그 제거 (`@work(exclusive=True)`가 이미 처리)
- `main.py` 단일 파일을 `tcp_socket_tool` 패키지로 모듈 분리
- `TCPConnection` 클래스 도입으로 네트워크 레이어와 TUI 레이어 분리
- 에러 코드 위치를 새 모듈 경로로 업데이트

## [1.0.0] - 2026-03-10

### Added

- asyncio + Textual 기반 TCP 소켓 TUI 클라이언트/서버 도구 구현
- Server/Client 모드 선택 화면 (`StartScreen`)
- 서버 설정 화면 (`ServerConfigScreen`) - 포트 입력, 포트 0 입력 시 OS 자동 배정
- 클라이언트 설정 화면 (`ClientConfigScreen`) - 호스트/포트 입력
- 공용 채팅 화면 (`ChatScreen`) - 메시지 송수신, 연결 상태 표시
- 에러코드 정의 및 문서화 (`docs/errorCode.md`)
- CLAUDE.md 프로젝트 가이드 추가
- README.md 프로젝트 소개 문서 추가
- Issue/PR 컨벤션 문서 추가

### Changed

- 에러 로그에서 traceback 분리 및 구조화된 에러코드 체계 적용

### CI/CD

- Claude Code Review GitHub Actions 워크플로우 추가
- Claude PR Assistant GitHub Actions 워크플로우 추가
- GitHub Actions 워크플로우 권한 write로 상향
- Claude Code Review 워크플로우에 `track_progress`, `github_token` 추가 (PR 리뷰 결과 미출력 버그 수정)

### Chore

- `.claude` 폴더 `.gitignore`에 추가
- `errorCode.md`를 `docs` 폴더로 이동
