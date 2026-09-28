# SK하이닉스 DART Financial Dashboard · 김예준

[![Dashboard](assets/dashboard-badge.svg)](https://hsc-class01.github.io/KYJ-SKhynix/)

## 🔗 대시보드 바로가기

[![대시보드 바로가기](assets/dashboard-badge.svg)](https://hsc-class01.github.io/KYJ-SKhynix/)

한림성심대학교 간호학과 김예준의 SK하이닉스 기업분석 프로젝트입니다. OpenDART를 이용해 정기보고서의 주요 재무수치를 수집하고, 재무비율을 계산하여 GitHub Pages 대시보드로 시각화합니다.

## 무엇을 자동화하나요?

- SK하이닉스 연결재무제표(CFS) 수집
- 사업보고서 / 반기보고서 / 1분기 / 3분기 재무수치 추출
- DART 접수번호별 원문 공시파일 저장
- 매출액·영업이익·순이익·자산·부채·자본·현금·재고·영업현금흐름 등 추출
- 영업이익률·순이익률·ROE·ROA·부채비율·유동비율·총자산회전율 계산
- Q2/Q3/Q4 standalone 수치 계산
- GitHub Pages Dashboard 재생성
- 매월 1일 GitHub Actions 자동 실행

## 데이터 범위에 대한 중요한 사항

프로젝트의 분석 타임라인은 2010년부터 시작하도록 설정했습니다. 다만 OpenDART의 **단일회사 주요계정 및 단일회사 전체 재무제표 API는 공식 개발가이드상 2015년 이후 사업연도를 대상으로 합니다.** 따라서 자동 구조화 재무수치 수집은 2015년부터 수행합니다.

2010~2014년까지 동일한 시계열을 완성하려면 별도의 역사 데이터 백필이 필요합니다. 이를 위한 입력 위치는 `data/historical_backfill/`입니다.

## API Key

OpenDART에서 인증키를 발급한 후 GitHub Repository에서:

`Settings → Secrets and variables → Actions → New repository secret`

- Name: `DART_API_KEY`
- Value: 40자리 OpenDART API 인증키

API 키는 코드나 README에 직접 넣지 않습니다.

## GitHub Actions 설치

이 ZIP은 숨김 파일을 포함하지 않습니다. 따라서 `.github/workflows`가 자동으로 업로드되지 않습니다.

`GITHUB_WORKFLOW/update-and-deploy.yml` 파일을 GitHub에서 다음 경로에 생성하세요.

`.github/workflows/update-and-deploy.yml`

자세한 순서는 `GITHUB_UPLOAD_GUIDE.md`를 참고하세요.

## Dashboard

GitHub Pages 주소:

https://hsc-class01.github.io/KYJ-SKhynix/

Repository:

https://github.com/HSC-Class01/KYJ-SKhynix

## Dashboard 구성

1. **Figures** — 매출·영업이익·순이익 추세, 수익성 그래프
2. **Annual** — 사업보고서 주요 재무수치
3. **Half-year** — 반기보고서 주요 재무수치
4. **Quarterly** — Q1~Q4 standalone 주요 수치
5. **Peer Firms** — 국내 반도체 산업 참고 기업

## 국내 Peer Firms

| 기업 | 종목코드 | 비교 맥락 |
|---|---:|---|
| 삼성전자 | 005930 | 메모리·시스템반도체를 포함하는 종합 반도체 기업 |
| DB하이텍 | 000990 | 국내 파운드리·반도체 제조 기업 |
| 한미반도체 | 042700 | 반도체 후공정 장비 기업 |
| LX세미콘 | 108320 | 반도체 설계 기업 |

## 폴더 구조

```text
KYJ-SKhynix/
├── agent/
│   ├── dart_client.py
│   ├── normalize.py
│   └── pipeline.py
├── assets/
│   └── dashboard-badge.svg
├── config/
│   ├── metrics.yml
│   └── settings.yml
├── data/
│   ├── historical_backfill/
│   └── raw/
├── docs/
│   └── index.html
├── GITHUB_WORKFLOW/
│   └── update-and-deploy.yml
├── scripts/
│   ├── build_dashboard.py
│   └── update_data.py
├── GITHUB_UPLOAD_GUIDE.md
├── README.md
└── requirements.txt
```
