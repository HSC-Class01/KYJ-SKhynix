# GitHub 업로드 및 배포 순서

## 1. ZIP 압축 해제
이 패키지는 GitHub 웹 업로드를 어렵게 만드는 숨김 파일(`.github`, `.gitignore`, `.env` 등)을 넣지 않았습니다.

## 2. Repository에 일반 파일 업로드
`KYJ-SKhynix` 폴더 안의 파일과 폴더를 GitHub 저장소 `HSC-Class01/KYJ-SKhynix` 루트에 업로드합니다.

## 3. DART API Secret 등록
Repository → Settings → Secrets and variables → Actions → New repository secret

- Name: `DART_API_KEY`
- Value: OpenDART에서 발급받은 40자리 API 인증키

## 4. Workflow 설치
GitHub에서 직접 다음 경로를 만듭니다.

`.github/workflows/update-and-deploy.yml`

그 위치에 `GITHUB_WORKFLOW/update-and-deploy.yml` 파일의 내용을 그대로 붙여넣습니다.

## 5. Pages 설정
Repository → Settings → Pages → Source에서 `GitHub Actions`를 선택합니다.

## 6. 첫 실행
Actions → `DART Update & GitHub Pages` → Run workflow

성공하면 다음 주소에서 대시보드를 확인할 수 있습니다.

https://hsc-class01.github.io/KYJ-SKhynix/

## 7. 자동 업데이트
Workflow는 매월 1일 01:00 UTC(한국시간 오전 10시)에 실행됩니다.

## 중요
2010~2014년은 OpenDART 구조화 재무 API의 공식 제공 범위가 아니므로 자동 구조화 수집은 2015년부터 시작합니다. 2010~2014까지 동일한 테이블을 채우려면 `data/historical_backfill/`에 별도 역사 데이터 백필 파일을 추가해야 합니다.
