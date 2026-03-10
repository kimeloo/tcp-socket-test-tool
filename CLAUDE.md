# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# TCP Socket Test Tool — Claude 작업 규칙

## 프로젝트 개요

asyncio + Textual 기반의 터미널 UI(TUI) TCP 소켓 클라이언트/서버 도구. Python 3.10+ 필요.

**진입점:** `main.py` → `tcp_socket_tool` 패키지.

## 개발 환경

```bash
# 가상환경 활성화 (이미 .venv 존재)
source .venv/Scripts/activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# 실행
python main.py
```

## 아키텍처

`tcp_socket_tool` 패키지로 모듈 분리되어 있으며 Textual의 Screen 스택 기반으로 동작한다.

```
tcp-socket-tool/
  main.py                          # 진입점 (~6줄)
  tcp_socket_tool/
    __init__.py
    logging_config.py              # 로깅 설정 + 헬퍼 (log, ts, get_local_ip)
    network.py                     # TUI 독립 TCP 네트워크 로직 (TCPConnection)
    app.py                         # TCPSocketApp
    screens/
      __init__.py                  # Screen 클래스 re-export
      start.py                     # StartScreen
      server_config.py             # ServerConfigScreen
      client_config.py             # ClientConfigScreen
      chat.py                      # ChatScreen (TCPConnection 콜백 통합)
```

| 모듈 | 역할 |
|------|------|
| `logging_config.py` | 파일 로거 설정, `log`, `ts()`, `get_local_ip()` |
| `network.py` | `TCPConnection` — 콜백 기반 TCP 연결 관리 (Textual 의존 없음) |
| `app.py` | `TCPSocketApp` — 앱 진입점, `StartScreen` 푸시 |
| `screens/start.py` | `StartScreen` — Server/Client 모드 선택 |
| `screens/server_config.py` | `ServerConfigScreen` — 포트 입력 후 ChatScreen 전환 |
| `screens/client_config.py` | `ClientConfigScreen` — 호스트+포트 입력 후 ChatScreen 전환 |
| `screens/chat.py` | `ChatScreen` — TCPConnection 콜백으로 UI 업데이트 |

**핵심 패턴:**
- `TCPConnection`은 콜백 5개(`on_connected`, `on_disconnected`, `on_message`, `on_error`, `on_info`)로 UI와 분리
- `ChatScreen`이 `@work(exclusive=True)`로 `TCPConnection`의 async 메서드를 호출
- Screen 간 순환 import는 지연 import로 해결
- 로그는 `tcp-socket-tool.log` 파일에 기록 (DEBUG 레벨)
- 서버는 포트 0 입력 시 OS가 자동 배정

## 브랜치 구조

| 브랜치 | 설명 |
|--------|------|
| `main` | 안정 릴리즈 |
| `dev` | 개발 브랜치 |
| `release/v{버전}` | 릴리즈 브랜치 |

## Git Workflow

### 브랜치 전략

- 새 작업을 시작할 때 사용자가 브랜치를 별도로 지정하지 않으면 **`dev` 브랜치를 기반**으로 `feat/{기능명}` 브랜치를 만들어 작업한다.
- 브랜치 생성 순서: `git checkout dev` → `git checkout -b feat/{기능명}`
- 작업 완료 후 push: `git push -u origin feat/{기능명}`

### 커밋 컨벤션

| type | 용도 |
|---|---|
| `feat` | 새 기능 추가 |
| `refactor` | 동작 변경 없는 코드 구조 개선 |
| `fix` | 버그 수정 |
| `docs` | 주석·문서만 변경 |
| `test` | 테스트 추가·수정 |
| `chore` | 빌드, 설정, 의존성 등 기타 변경 |

**메시지 형식:**

```
type: short description in English

본문은 한국어로 작성 (필요 시)
```

**메시지 스타일:**
- 제목은 영어로 작성, 소문자 시작, 동사원형으로 시작 (`add`, `fix`, `update`, `remove` 등)
- 제목은 50자 이내 권장
- 본문은 한국어로 작성, 필요 시만 추가

**커밋 규칙:**
- `Co-Authored-By:` 트레일러 절대 추가 금지
- 사용자 확인 없이 커밋 실행 금지 (`/commit` 스킬 사용 시)
- `--no-verify` 사용 금지

### Issue 컨벤션

**제목 형식:** `[타입] 설명`

| 타입 | 용도 |
|------|------|
| `bug` | 버그 리포트 |
| `feature` | 새 기능 제안 |
| `docs` | 문서 개선 |
| `question` | 질문·문의 |
| `chore` | 빌드, 설정, 의존성 등 |

**Bug Report 필수 항목:** 재현 단계, 예상 동작, 실제 동작, 환경 정보 (OS, Python 버전)

### PR 컨벤션

**제목 형식:** 커밋 컨벤션과 동일 (`type: description in English`)

**본문 항목:**
- 변경사항: 무엇을 바꿨는지
- 이유: 왜 바꿨는지
- 테스트 방법: 어떻게 검증했는지
- 관련 이슈: `Fixes #번호` 또는 `Closes #번호`

**체크리스트:**
- [ ] 커밋 컨벤션 준수
- [ ] 관련 이슈 링크 포함
- [ ] 로컬에서 테스트 완료

### CHANGELOG

- 기능 추가, 버그 수정, 리팩토링 등 사용자에게 의미 있는 변경이 있을 때 `CHANGELOG.md`를 업데이트한다.
- [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) 형식을 따른다.
- 카테고리: `Added`, `Changed`, `Fixed`, `Removed`, `CI/CD`, `Chore`
- 새 릴리즈 시 `## [버전] - YYYY-MM-DD` 섹션을 추가한다.
