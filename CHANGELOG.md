# Changelog

이 프로젝트의 모든 주요 변경사항을 기록합니다.

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
