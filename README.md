# real_estate

부동산 계약 관련 HTML 도구를 GitHub Pages로 배포하기 위한 정적 앱입니다.

## 구조

- `data/`: 원본 HTML 11개
- `app/index.html`: 메뉴형 실행 화면
- `app/pages/`: 원본 HTML을 독립 실행할 수 있도록 복사하고 선택 특약 연동 스크립트를 삽입한 페이지
- `build_app.py`: `data/`를 기반으로 `app/`을 재생성하는 스크립트
- `.github/workflows/real-estate-pages.yml`: GitHub Pages 배포 workflow

## 로컬 실행

```bash
python3 build_app.py
cd app
python3 -m http.server 8766
```

접속: `http://127.0.0.1:8766`

## 사용 방법

- 왼쪽 메뉴에서 원본 HTML 항목을 선택합니다.
- 선택한 HTML은 iframe 안에서 독립적으로 실행됩니다.
- 가계약 섹션을 제외한 다른 섹션에서 선택한 특약사항은 가계약서의 `가계약 문구 자동 생성` 특약사항에 자동으로 합산됩니다.
- 가계약서 작성 후 `다운로드` 버튼으로 텍스트 파일을 저장할 수 있습니다.

## 배포

GitHub 저장소 이름은 `real_estate`로 사용합니다.

1. GitHub 저장소 `real_estate`에 push합니다.
2. 저장소의 `Settings > Pages`에서 Source를 `GitHub Actions`로 설정합니다.
3. `Actions > Deploy real estate app to GitHub Pages`가 실행되면 `app/` 폴더가 배포됩니다.
