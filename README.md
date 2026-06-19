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

1. 왼쪽 메뉴에서 필요한 특약 섹션을 엽니다.
2. 원하는 특약사항을 클릭하거나 체크합니다.
3. 마지막에 `가계약서` 섹션으로 이동합니다.
4. 가계약 정보를 입력하면 선택한 특약이 자동으로 특약사항에 추가됩니다.
5. 가계약서의 `복사`, `인쇄`, `다운로드` 버튼으로 저장합니다.

## 배포

GitHub 저장소 이름은 `real_estate`로 사용합니다.

1. GitHub 저장소 `real_estate`에 push합니다.
2. 저장소의 `Settings > Pages`에서 Source를 `GitHub Actions`로 설정합니다.
3. `Actions > Deploy real estate app to GitHub Pages`가 실행되면 `app/` 폴더가 배포됩니다.
