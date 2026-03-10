# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# TCP Socket Test Tool — Claude 작업 규칙

## 프로젝트 개요

asyncio + Textual 기반의 터미널 UI(TUI) TCP 소켓 클라이언트/서버 도구. Python 3.10+ 필요.

**진입점:** `main.py` 단일 파일로 전체 앱 구성.

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

전체 코드가 `main.py` 한 파일에 있으며 Textual의 Screen 스택 기반으로 동작한다.

| 클래스 | 역할 |
|--------|------|
| `TCPSocketApp` | 앱 진입점, `StartScreen` 푸시 |
| `StartScreen` | Server/Client 모드 선택 화면 |
| `ServerConfigScreen` | 포트 입력 후 `ChatScreen(mode="server")` 전환 |
| `ClientConfigScreen` | 호스트+포트 입력 후 `ChatScreen(mode="client")` 전환 |
| `ChatScreen` | Server/Client 공용 채팅 화면; `asyncio.start_server` 또는 `asyncio.open_connection` 사용 |

**핵심 패턴:**
- `@work(exclusive=True)` 데코레이터로 비동기 네트워크 작업을 Textual Worker로 실행
- `_writer: asyncio.StreamWriter`로 메시지 전송, `reader.read(4096)` 루프로 수신
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
type: 설명
```

**메시지 스타일:**
- 한국어 단문, 명사형 마무리 (`추가`, `분리`, `개선`, `수정` 등)
- 제목은 50자 이내 권장
- 본문은 필요 시만 추가

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

**제목 형식:** 커밋 컨벤션과 동일 (`type: 설명`)

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
