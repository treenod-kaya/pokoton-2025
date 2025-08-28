# 🚀 Streamlit Community Cloud 배포 테스트 앱

이것은 Streamlit Community Cloud에서 배포 테스트를 위한 간단한 Streamlit 애플리케이션입니다.

## 📋 기능

- 실시간 시간 표시
- 사용자 이름 입력 및 인사
- 색상 선택기
- 샘플 차트 표시
- 사이드바 상호작용 요소들

## 🛠️ 로컬 실행 방법

1. 저장소를 클론합니다:
```bash
git clone <your-repo-url>
cd pokoton-2025
```

2. 필요한 패키지를 설치합니다:
```bash
pip install -r requirements.txt
```

3. Streamlit 앱을 실행합니다:
```bash
streamlit run app.py
```

## 🌐 Streamlit Community Cloud 배포 방법

1. **GitHub 저장소 준비**
   - 이 프로젝트를 GitHub에 푸시합니다
   - 저장소가 public이어야 합니다

2. **Streamlit Community Cloud 설정**
   - [share.streamlit.io](https://share.streamlit.io)에 접속합니다
   - GitHub 계정으로 로그인합니다
   - "New app" 버튼을 클릭합니다

3. **앱 배포 설정**
   - Repository: 이 프로젝트의 GitHub URL
   - Branch: `main` (또는 기본 브랜치)
   - Main file path: `app.py`
   - App URL: 원하는 URL (선택사항)

4. **배포 완료**
   - "Deploy!" 버튼을 클릭합니다
   - 몇 분 후 앱이 배포됩니다

## 📁 파일 구조

```
pokoton-2025/
├── app.py              # 메인 Streamlit 애플리케이션
├── requirements.txt    # Python 패키지 의존성
├── README.md          # 프로젝트 설명서
└── .gitignore         # Git 무시 파일 목록
```

## 🔧 사용된 기술

- **Streamlit**: 웹 앱 프레임워크
- **Pandas**: 데이터 처리
- **NumPy**: 수치 계산

## 📝 참고사항

- Streamlit Community Cloud는 무료 서비스입니다
- 앱은 자동으로 GitHub 저장소와 동기화됩니다
- 코드를 푸시하면 자동으로 재배포됩니다
