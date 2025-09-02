# 나라장터 입찰공고 조회 시스템

나라장터(G2B) 입찰공고정보를 조회하는 Python 애플리케이션입니다.

## 🌐 온라인 데모

**GitHub Pages에서 바로 사용해보세요!**
👉 **[https://cjlee-cmd.github.io/publicportal/](https://cjlee-cmd.github.io/publicportal/)**

> **참고**: GitHub Pages 버전은 CORS 정책으로 인해 일부 기능이 제한될 수 있습니다. 완전한 기능을 원하시면 로컬 환경에서 실행해주세요.

## 🌟 특징

### 📱 현대적인 웹 UI
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 최적화
- **실시간 검색**: 날짜 구간 및 기관별 필터링
- **인터랙티브 그리드**: 체크박스 선택, 정렬, 페이지네이션
- **Excel 내보내기**: 선택된 데이터를 Excel 파일로 다운로드
- **다크모드 지원**: 사용자 환경에 맞는 테마

### 🔧 기능
- 오늘 공고된 입찰 조회
- 용역, 건설공사, 물품 입찰공고 조회
- 날짜 구간 설정 검색
- 발주기관별 필터링
- 선택 항목 일괄 삭제
- curl subprocess를 이용한 안정적인 API 연동
- SSL 문제 우회 처리

## 📦 설치

```bash
# Python 3.x 필요
python3 --version

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

## 🚀 사용법

### 웹 애플리케이션 (권장)

```bash
# 웹 서버 시작
python3 run_web.py

# 브라우저에서 접속
# http://localhost:5000
```

#### 웹 UI 기능
- **날짜 검색**: 시작일~종료일 범위로 검색
- **입찰 구분**: 전체/용역/건설공사/물품 선택
- **기관 필터**: 발주기관별 필터링
- **결과 관리**: 체크박스로 선택 후 삭제/Excel 저장
- **실시간 업데이트**: 현재 시간 표시 및 자동 갱신

### CLI 애플리케이션

```bash
python3 main.py
```

### 프로그래밍 방식

```python
from g2b_client import G2BClient

# 클라이언트 생성
client = G2BClient()

# 오늘 공고된 모든 입찰 조회
today_bids = client.get_today_bids("all")

# 최근 용역 입찰공고 조회
servc_data = client.get_bid_list("servc", num_of_rows=10)
client.print_bid_summary(servc_data)
```

## 📁 프로젝트 구조

```
PublicPortal/
├── main.py              # CLI 애플리케이션
├── g2b_client.py        # 통합 API 클라이언트
├── config.py            # 설정 파일
├── run_web.py           # 웹 애플리케이션 실행 스크립트
├── requirements.txt     # 의존성 목록
├── README.md            # 프로젝트 문서
├── web/                 # 웹 애플리케이션
│   ├── app.py           # Flask 백엔드 서버
│   ├── templates/       # HTML 템플릿
│   │   └── index.html   # 메인 페이지
│   └── static/          # 정적 파일
│       ├── css/         # 스타일시트
│       │   └── style.css
│       └── js/          # JavaScript
│           └── app.js   # 프론트엔드 로직
└── old_tests/           # 이전 테스트 파일들 (보관용)
```

## 🔌 API 정보

- **서비스**: 조달청 나라장터 입찰공고정보서비스
- **제공처**: 공공데이터포털 (data.go.kr)
- **인증**: 서비스 키 기반 인증
- **응답 형식**: XML (자동으로 JSON 변환)

## 🎨 기술 스택

### 백엔드
- **Python 3.x**
- **Flask**: 웹 프레임워크
- **Pandas**: 데이터 처리
- **OpenPyXL**: Excel 파일 생성

### 프론트엔드
- **HTML5** + **CSS3** + **JavaScript (ES6+)**
- **Tailwind CSS**: 유틸리티 기반 CSS 프레임워크
- **Font Awesome**: 아이콘
- **Axios**: HTTP 클라이언트

## ⚠️ 주의사항

### 시스템 요구사항
- **Python 3.7+** 필요
- **curl 명령어** 필요 (macOS/Linux 기본 설치, Windows는 별도 설치)
- **모던 브라우저** 권장 (Chrome, Firefox, Safari, Edge)

### 네트워크
- 인터넷 연결 필요 (공공데이터포털 API 호출)
- 방화벽에서 5000 포트 허용 필요 (웹 서버용)

## 🔧 문제 해결

### 의존성 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 가상환경에서 재설치
pip install -r requirements.txt --force-reinstall
```

### 웹 서버 접속 불가
```bash
# 포트 사용 확인
netstat -an | grep :5000

# 방화벽 설정 확인
# macOS: 시스템 환경설정 > 보안 및 개인 정보 보호
# Windows: Windows Defender 방화벽
```

### API 오류 발생시
1. 서비스 키 유효성 확인
2. 네트워크 연결 상태 확인
3. 공공데이터포털 서비스 상태 확인