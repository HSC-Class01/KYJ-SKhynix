# SK하이닉스 DART Financial Dashboard · 김예준

[![대시보드 바로가기](assets/dashboard-badge.svg)](https://hsc-class01.github.io/KYJ-SKhynix/)

## 🔗 대시보드 바로가기

[![대시보드 바로가기](assets/dashboard-badge.svg)](https://hsc-class01.github.io/KYJ-SKhynix/)

SK하이닉스의 OpenDART 연결재무제표를 수집·정규화하고 Annual / Half-year / Quarterly 재무수치와 Figures를 GitHub Pages에서 제공하는 자동화 프로젝트입니다.

## Dashboard

- Figures: 매출액·영업이익·순이익 추세와 수익성 지표
- Annual: 사업보고서 주요 재무수치
- Half-year: 반기보고서 주요 재무수치
- Quarterly: Q1~Q4 standalone 주요 재무수치
- Peer Firms: 국내 반도체 산업 비교기업

## 자동 업데이트

GitHub Actions가 매월 1일 10:00 KST에 실행되며, 필요할 때는 workflow_dispatch로 수동 실행할 수 있습니다.

OpenDART 구조화 재무 API는 2015년 이후 데이터를 대상으로 하므로 구조화 수치의 자동 수집은 2015년부터 시작합니다. 2010~2014년은 별도 historical backfill이 필요합니다.

### API Secret

GitHub Repository → Settings → Secrets and variables → Actions → New repository secret

- Name: DART_API_KEY
- Value: OpenDART 40자리 인증키

API key는 코드와 README에 저장하지 않습니다.

## 국내 Peer Firms

| 기업 | 종목코드 | 비교 맥락 |
|---|---:|---|
| 삼성전자 | 005930 | 가장 직접적인 국내 메모리 반도체 비교기업 |
| DB하이텍 | 000990 | 국내 상장 반도체 제조·파운드리 비교기업 |
| SK실트론 | 비상장 | 반도체 웨이퍼 소재 기업 |
| 한미반도체 | 042700 | 반도체 후공정 장비 기업 |
| LX세미콘 | 108320 | 반도체 설계 기업 |

Peer firms는 사업모델이 동일하다는 의미가 아니라, 국내 반도체 밸류체인과 경쟁환경을 비교하기 위한 참고기업입니다.

## Repository / Dashboard

- Repository: https://github.com/HSC-Class01/KYJ-SKhynix
- Dashboard: https://hsc-class01.github.io/KYJ-SKhynix/

## 폴더 구조

KYJ-SKhynix/
├── .github/workflows/
│   └── update-and-deploy.yml
├── agent/
├── assets/
├── config/
├── data/
├── docs/
├── scripts/
├── README.md
└── requirements.txt
