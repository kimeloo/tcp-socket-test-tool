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
