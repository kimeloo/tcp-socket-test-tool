# TCP Socket Test Tool

asyncio + [Textual](https://github.com/Textualize/textual) 기반의 터미널 UI TCP 소켓 클라이언트/서버 도구입니다.

## 기능

- **서버 모드**: 지정한 포트에서 TCP 연결을 수신 대기
- **클라이언트 모드**: 원격 호스트/포트에 TCP 연결
- **양방향 메시지 송수신**: 실시간 TUI 인터페이스
- **로컬 IP 자동 감지**

## 요구사항

- Python 3.10+
- [Textual](https://github.com/Textualize/textual) 3.2.0

## 설치

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 실행

```bash
python main.py
```

## 브랜치 구조

| 브랜치 | 설명 |
|--------|------|
| `main` | 안정 릴리즈 |
| `v1.0` | v1.0 릴리즈 스냅샷 |
| `dev`  | 개발 브랜치 |

## 기여하기

### Issue 컨벤션

**제목 형식:** `[타입] 설명`

| 타입 | 용도 |
|------|------|
| `bug` | 버그 리포트 |
| `feature` | 새 기능 제안 |
| `docs` | 문서 개선 |
| `question` | 질문·문의 |
| `chore` | 빌드, 설정, 의존성 등 |

**예시:**
- `[bug] 서버 연결 끊김 시 에러 메시지 미표시`
- `[feature] 자동 재연결 기능 추가`

**Bug Report 필수 항목:**
1. **재현 단계** — 버그를 재현하는 최소 절차
2. **예상 동작** — 정상적으로 동작해야 할 내용
3. **실제 동작** — 실제로 발생한 증상
4. **환경 정보** — OS, Python 버전, Textual 버전

---

### PR 컨벤션

**제목 형식:** 커밋 컨벤션과 동일 (`type: 설명`)

| 항목 | 설명 |
|------|------|
| 변경사항 | 무엇을 바꿨는지 |
| 이유 | 왜 바꿨는지 |
| 테스트 방법 | 어떻게 검증했는지 |
| 관련 이슈 | `Fixes #번호` 형식으로 링크 |

**체크리스트:**
- [ ] 커밋 컨벤션 준수
- [ ] 관련 이슈 링크 포함 (`Fixes #번호`)
- [ ] 로컬에서 테스트 완료
