# 부동산 HTML 독립 실행 앱

`../data`의 기존 HTML 11개를 각각 독립 페이지로 유지해 실행하는 정적 앱입니다.

## 로컬 실행

```bash
cd /home/gentler/Develop2/real_estate/app
python3 -m http.server 8766
```

접속: `http://127.0.0.1:8766`

## 사용 방법

- 왼쪽 메뉴에서 원본 HTML 항목을 선택합니다.
- 선택한 HTML은 iframe 안에서 독립적으로 실행됩니다.
- 가계약 섹션을 제외한 다른 섹션에서 선택한 특약사항은 가계약서의 `가계약 문구 자동 생성` 특약사항에 자동으로 합산됩니다.
- 가계약서 작성 후 `다운로드` 버튼으로 텍스트 파일을 저장할 수 있습니다.

## GitHub Pages 배포

이 저장소 루트에 `.github/workflows/real-estate-pages.yml`가 생성되어 있습니다.

1. 변경 파일을 GitHub 저장소에 push합니다.
2. GitHub 저장소의 `Settings > Pages`에서 Source를 `GitHub Actions`로 설정합니다.
3. `Actions > Deploy real estate app to GitHub Pages`를 실행하거나, 관련 파일을 push하면 자동 배포됩니다.

배포 대상 폴더는 git 저장소 루트 기준 `app`입니다.
